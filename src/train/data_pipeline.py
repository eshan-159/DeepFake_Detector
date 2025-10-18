from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Tuple

import torch
from torch.utils.data import DataLoader, WeightedRandomSampler
from torchvision import datasets, transforms


@dataclass
class DataConfig:
    train_dir: Path
    val_dir: Path
    image_size: int = 224
    batch_size: int = 8
    num_workers: int = 4
    class_weights: Tuple[float, float] | None = None


def build_transforms(image_size: int) -> Tuple[transforms.Compose, transforms.Compose]:
    train_tf = transforms.Compose([
        transforms.Resize((image_size + 16, image_size + 16)),
        transforms.RandomResizedCrop(image_size, scale=(0.85, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomApply([transforms.ColorJitter(0.2, 0.2, 0.2, 0.1)], p=0.8),
        transforms.RandomApply([transforms.GaussianBlur(3)], p=0.3),
        transforms.RandomApply([transforms.RandomAdjustSharpness(1.5)], p=0.3),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.25, 0.25, 0.25]),
    ])
    val_tf = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.25, 0.25, 0.25]),
    ])
    return train_tf, val_tf


def _build_sampler(labels: Iterable[int], class_weights: Tuple[float, float] | None) -> WeightedRandomSampler | None:
    if class_weights is None:
        return None
    weights = torch.tensor([class_weights[label] for label in labels], dtype=torch.float)
    return WeightedRandomSampler(weights, num_samples=len(weights), replacement=True)


def create_dataloaders(config: DataConfig) -> Tuple[DataLoader, DataLoader]:
    train_tf, val_tf = build_transforms(config.image_size)
    train_dataset = datasets.ImageFolder(root=str(config.train_dir), transform=train_tf)
    val_dataset = datasets.ImageFolder(root=str(config.val_dir), transform=val_tf)

    sampler = _build_sampler(train_dataset.targets, config.class_weights)
    train_loader = DataLoader(
        train_dataset,
        batch_size=config.batch_size,
        shuffle=sampler is None,
        sampler=sampler,
        num_workers=config.num_workers,
        pin_memory=True,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=config.batch_size,
        shuffle=False,
        num_workers=config.num_workers,
        pin_memory=True,
    )
    return train_loader, val_loader


def _write_metadata(output: Path, metadata: dict) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)


def _prepare_faceforensics(output: Path) -> None:
    metadata = {
        "dataset": "FaceForensics++",
        "instructions": "Download from https://github.com/ondyari/FaceForensics. Extract REAL and FAKE subsets manually and place under the output folder.",
        "required_actions": [
            "Request access via official FaceForensics++ portal",
            "Download High Quality c23 version",
            "Run provided scripts to extract frames",
        ],
    }
    _write_metadata(output / "README.json", metadata)


def _prepare_dfdc(output: Path) -> None:
    metadata = {
        "dataset": "DFDC",
        "instructions": "Apply for access via Facebook DFDC Kaggle competition. Download chunks and extract frames. Place under output directory maintaining real/deepfake structure.",
        "required_actions": [
            "Review Kaggle DFDC terms of use",
            "Download videos and extract frames using ffmpeg",
            "Ensure consent and licensing compliance",
        ],
    }
    _write_metadata(output / "README.json", metadata)


def main() -> None:
    parser = argparse.ArgumentParser(description="Utility helpers for data pipeline management.")
    parser.add_argument("--prepare", choices=["faceforensics", "dfdc"], help="Generate metadata scaffolding for a dataset.")
    parser.add_argument("--output", type=Path, required=True, help="Output directory")
    args = parser.parse_args()

    if args.prepare == "faceforensics":
        _prepare_faceforensics(args.output)
    elif args.prepare == "dfdc":
        _prepare_dfdc(args.output)
    print(f"Metadata written to {args.output}")


if __name__ == "__main__":
    main()
