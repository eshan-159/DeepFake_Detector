from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

import matplotlib.pyplot as plt
import seaborn as sns
import torch
from rich import print as rprint
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_recall_fscore_support,
    roc_auc_score,
)

from src.train.data_pipeline import DataConfig, create_dataloaders
from src.train.models.hybrid_cnn import HybridDeepfakeModel, ModelConfig
from src.train.train import load_config

LABELS = ["real", "deepfake"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate a trained deepfake detector checkpoint.")
    parser.add_argument("--config", type=Path, required=True, help="Configuration file used for training.")
    parser.add_argument("--checkpoint", type=Path, required=True, help="Path to checkpoint (.pt).")
    parser.add_argument("--report", type=Path, help="Optional path to write JSON metrics.")
    parser.add_argument("--confusion", type=Path, help="Optional path to save confusion matrix PNG.")
    return parser.parse_args()


def _load_model(config: Dict[str, Any], checkpoint: Path) -> HybridDeepfakeModel:
    train_cfg = config["training"]
    model_cfg = ModelConfig(
        num_classes=train_cfg.get("num_classes", 2),
        backbone=train_cfg.get("backbone", "resnet18"),
        pretrained=False,
        dropout=train_cfg.get("dropout", 0.2),
    )
    model = HybridDeepfakeModel(model_cfg)
    ckpt = torch.load(checkpoint, map_location="cpu")
    state_dict = ckpt["model"] if isinstance(ckpt, dict) and "model" in ckpt else ckpt
    model.load_state_dict(state_dict, strict=False)
    model.eval()
    return model


@torch.no_grad()
def evaluate(config: Dict[str, Any], checkpoint: Path) -> Dict[str, Any]:
    data_cfg = config["dataset"]
    data_config = DataConfig(
        train_dir=Path(data_cfg["train_dir"]),
        val_dir=Path(data_cfg["val_dir"]),
        image_size=data_cfg.get("image_size", 224),
        batch_size=data_cfg.get("eval_batch_size", 32),
        num_workers=data_cfg.get("num_workers", 4),
    )
    _, val_loader = create_dataloaders(data_config)

    model = _load_model(config, checkpoint)
    preds, probs, targets = [], [], []
    for images, labels in val_loader:
        logits = model(images)
        probabilities = torch.softmax(logits, dim=1)[:, 1]
        preds.extend(logits.argmax(dim=1).tolist())
        probs.extend(probabilities.tolist())
        targets.extend(labels.tolist())

    acc = accuracy_score(targets, preds) if targets else 0.0
    precision, recall, f1, _ = precision_recall_fscore_support(
        targets, preds, average="binary", zero_division=0
    )
    try:
        roc = roc_auc_score(targets, probs)
    except ValueError:
        roc = float("nan")
    cm = confusion_matrix(targets, preds, labels=[0, 1])

    return {
        "accuracy": acc,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": roc,
        "confusion_matrix": cm.tolist(),
    }


def save_confusion_matrix(cm: list[list[int]], path: Path) -> None:
    fig, ax = plt.subplots(figsize=(4, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=LABELS, yticklabels=LABELS, ax=ax)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title("Confusion Matrix")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    metrics = evaluate(config, args.checkpoint)

    rprint("[bold green]Evaluation complete")
    for key, value in metrics.items():
        if key != "confusion_matrix":
            rprint(f"  {key:>12}: {value:.4f}")

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        with args.report.open("w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)
        rprint(f"[cyan]Metrics report written to {args.report}")

    if args.confusion:
        save_confusion_matrix(metrics["confusion_matrix"], args.confusion)
        rprint(f"[cyan]Confusion matrix saved to {args.confusion}")


if __name__ == "__main__":
    main()
