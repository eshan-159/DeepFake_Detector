from __future__ import annotations

import argparse
import json
import yaml
from pathlib import Path
from typing import Any, Dict

import torch
from rich import print as rprint
from sklearn.metrics import accuracy_score
from torch import nn
from torch.cuda.amp import GradScaler, autocast
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from tqdm import tqdm

from src.train.data_pipeline import DataConfig, create_dataloaders
from src.train.models.hybrid_cnn import HybridDeepfakeModel, ModelConfig


def load_config(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        if path.suffix == ".json":
            return json.load(f)
        return yaml.safe_load(f)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the hybrid CNN deepfake detector.")
    parser.add_argument("--config", type=Path, required=True, help="Path to YAML/JSON config file.")
    parser.add_argument("--epochs", type=int, help="Override epochs from config.")
    parser.add_argument("--save-dir", type=Path, default=Path("models/run"), help="Directory for checkpoints.")
    parser.add_argument("--resume", type=Path, help="Path to checkpoint to resume from.")
    parser.add_argument("--no-amp", action="store_true", help="Disable mixed precision training.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    return parser.parse_args()


def set_seed(seed: int) -> None:
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def build_criterion(train_cfg: Dict[str, Any], device: torch.device) -> nn.Module:
    smoothing = float(train_cfg.get("label_smoothing", 0.0))
    weights = train_cfg.get("class_weights")
    if weights:
        weight_tensor = torch.tensor(weights, dtype=torch.float32, device=device)
    else:
        weight_tensor = None
    return nn.CrossEntropyLoss(weight=weight_tensor, label_smoothing=smoothing)


def train_one_epoch(
    model: nn.Module,
    loader: torch.utils.data.DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
    scaler: GradScaler | None,
    use_amp: bool,
) -> float:
    model.train()
    total_loss = 0.0
    for images, labels in tqdm(loader, desc="train", leave=False):
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad(set_to_none=True)
        with autocast(enabled=use_amp):
            logits = model(images)
            loss = criterion(logits, labels)
        if use_amp and scaler is not None:
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
        else:
            loss.backward()
            optimizer.step()
        total_loss += loss.item() * images.size(0)
    return total_loss / len(loader.dataset)


@torch.no_grad()
def evaluate(
    model: nn.Module,
    loader: torch.utils.data.DataLoader,
    device: torch.device,
) -> Dict[str, float]:
    model.eval()
    preds, targets = [], []
    total_loss = 0.0
    dataset_size = len(loader.dataset)
    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        logits = model(images)
        loss = nn.functional.cross_entropy(logits, labels)
        total_loss += loss.item() * images.size(0)
        preds.extend(logits.argmax(dim=1).cpu().tolist())
        targets.extend(labels.cpu().tolist())
    accuracy = accuracy_score(targets, preds) if targets else 0.0
    val_loss = total_loss / dataset_size if dataset_size else 0.0
    return {"val_loss": val_loss, "val_accuracy": accuracy}


def main() -> None:
    args = parse_args()
    set_seed(args.seed)
    config = load_config(args.config)

    data_cfg = config["dataset"]
    train_cfg = config["training"]

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    data_config = DataConfig(
        train_dir=Path(data_cfg["train_dir"]),
        val_dir=Path(data_cfg["val_dir"]),
        image_size=data_cfg.get("image_size", 224),
        batch_size=train_cfg.get("batch_size", 8),
        num_workers=data_cfg.get("num_workers", 4),
        class_weights=tuple(train_cfg.get("class_weights", [])) or None,
    )
    train_loader, val_loader = create_dataloaders(data_config)

    model_cfg = ModelConfig(
        num_classes=train_cfg.get("num_classes", 2),
        backbone=train_cfg.get("backbone", "resnet18"),
        pretrained=train_cfg.get("pretrained", False),
        dropout=train_cfg.get("dropout", 0.2),
    )
    model = HybridDeepfakeModel(model_cfg)
    model.to(device)

    criterion = build_criterion(train_cfg, device)
    optimizer = AdamW(
        model.parameters(),
        lr=train_cfg.get("lr", 3e-4),
        weight_decay=train_cfg.get("weight_decay", 1e-2),
        betas=(train_cfg.get("beta1", 0.9), train_cfg.get("beta2", 0.999)),
    )
    scheduler = CosineAnnealingLR(optimizer, T_max=train_cfg.get("epochs", 1))

    use_amp = torch.cuda.is_available() and not args.no_amp
    scaler = GradScaler(enabled=use_amp)

    start_epoch = 1
    best_acc = 0.0
    best_path = None
    if args.resume:
        checkpoint = torch.load(args.resume, map_location=device)
        model.load_state_dict(checkpoint["model"])
        optimizer.load_state_dict(checkpoint["optimizer"])
        scheduler.load_state_dict(checkpoint["scheduler"])
        start_epoch = checkpoint["epoch"] + 1
        best_acc = checkpoint.get("best_acc", 0.0)
        rprint(f"[yellow]Resumed from {args.resume}, starting epoch {start_epoch}")

    epochs = args.epochs or train_cfg.get("epochs", 1)
    args.save_dir.mkdir(parents=True, exist_ok=True)
    history = {"train_loss": [], "val_loss": [], "val_accuracy": []}

    for epoch in range(start_epoch, epochs + 1):
        rprint(f"[bold cyan]Epoch {epoch}/{epochs}")
        train_loss = train_one_epoch(model, train_loader, criterion, optimizer, device, scaler, use_amp)
        metrics = evaluate(model, val_loader, device)
        scheduler.step()

        history["train_loss"].append(train_loss)
        history["val_loss"].append(metrics["val_loss"])
        history["val_accuracy"].append(metrics["val_accuracy"])

        rprint(
            f"  train_loss={train_loss:.4f} | val_loss={metrics['val_loss']:.4f} | val_acc={metrics['val_accuracy']:.4f}"
        )

        checkpoint = {
            "epoch": epoch,
            "model": model.state_dict(),
            "optimizer": optimizer.state_dict(),
            "scheduler": scheduler.state_dict(),
            "best_acc": best_acc,
            "config": config,
        }
        path = args.save_dir / f"epoch_{epoch:02d}.pt"
        torch.save(checkpoint, path)

        if metrics["val_accuracy"] >= best_acc:
            best_acc = metrics["val_accuracy"]
            best_path = args.save_dir / "best.pt"
            torch.save(model.state_dict(), best_path)

    final_model_path = args.save_dir / "demo.pt"
    torch.save(model.state_dict(), final_model_path)
    with (args.save_dir / "history.json").open("w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

    rprint(f"[green]Training complete. Final weights: {final_model_path}")
    if best_path:
        rprint(f"[green]Best checkpoint (val_acc={best_acc:.4f}) saved to {best_path}")


if __name__ == "__main__":
    main()
