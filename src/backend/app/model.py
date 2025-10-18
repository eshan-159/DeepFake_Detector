from __future__ import annotations

import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Tuple

import torch

from src.train.models.hybrid_cnn import HybridDeepfakeModel, ModelConfig

_MODEL: HybridDeepfakeModel | None = None
_DEVICE: torch.device | None = None
_METRICS_LOCK = threading.Lock()
_METRICS = {
    "total_predictions": 0,
    "class_counts": {"real": 0, "deepfake": 0},
    "running_accuracy": 0.0,
    "updated_at": datetime.utcnow(),
}


def _load_state_dict(model: HybridDeepfakeModel, checkpoint_path: Path, device: torch.device) -> None:
    if not checkpoint_path.exists():
        return
    state = torch.load(checkpoint_path, map_location=device)
    if isinstance(state, dict) and "model" in state:
        state = state["model"]
    model.load_state_dict(state, strict=False)


def get_model_and_device() -> Tuple[HybridDeepfakeModel, torch.device]:
    global _MODEL, _DEVICE
    if _MODEL is None or _DEVICE is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = HybridDeepfakeModel(ModelConfig())
        checkpoint_path = Path(os.getenv("MODEL_PATH", "models/demo.pt"))
        _load_state_dict(model, checkpoint_path, device)
        model.to(device)
        model.eval()
        _MODEL, _DEVICE = model, device
    return _MODEL, _DEVICE


def update_metrics(label: str, confidence: float, correct: bool | None) -> None:
    with _METRICS_LOCK:
        _METRICS["total_predictions"] += 1
        _METRICS["class_counts"].setdefault(label, 0)
        _METRICS["class_counts"][label] += 1
        if correct is not None:
            alpha = 0.1
            prev = _METRICS["running_accuracy"]
            _METRICS["running_accuracy"] = prev * (1 - alpha) + (1 if correct else 0) * alpha
        _METRICS["updated_at"] = datetime.utcnow()


def get_metrics_snapshot() -> dict:
    with _METRICS_LOCK:
        return {
            "total_predictions": _METRICS["total_predictions"],
            "class_counts": dict(_METRICS["class_counts"]),
            "running_accuracy": float(_METRICS["running_accuracy"]),
            "updated_at": _METRICS["updated_at"],
        }
