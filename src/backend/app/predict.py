from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile

from .model import get_metrics_snapshot, get_model_and_device, update_metrics
from .schemas import MetricsResponse, PredictionResponse, RetrainRequest
from . import utils

router = APIRouter()
LABELS = ["real", "deepfake"]


@router.post("/predict", response_model=PredictionResponse)
async def predict(image: UploadFile = File(...)) -> PredictionResponse:
    model, device = get_model_and_device()
    contents = await image.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Empty image upload")

    pil_image = utils.read_image_to_pil(contents)
    probs, pred_idx_tensor, cam_result = utils.run_inference(model, pil_image, device)
    pred_idx = int(pred_idx_tensor.item())
    confidence = float(probs[0, pred_idx].item())
    label = LABELS[pred_idx]

    update_metrics(label, confidence, correct=None)

    return PredictionResponse(
        label=label,
        confidence=confidence,
        saliency_path=f"/saliency/{Path(cam_result.saliency_path).name}",
        inference_ms=cam_result.elapsed_ms,
    )


@router.get("/metrics", response_model=MetricsResponse)
async def metrics() -> MetricsResponse:
    snapshot = get_metrics_snapshot()
    return MetricsResponse(**snapshot)


@router.post("/retrain")
async def retrain(request: RetrainRequest, background: BackgroundTasks) -> dict[str, Literal["queued"]]:
    if not request.consent_acknowledged:
        raise HTTPException(status_code=400, detail="You must acknowledge consent and legal compliance before retraining.")
    if not Path(request.config_path).exists():
        raise HTTPException(status_code=404, detail="Config path not found")

    def task() -> None:
        command = [
            "python",
            "src/train/train.py",
            "--config",
            request.config_path,
        ]
        if request.epochs:
            command.extend(["--epochs", str(request.epochs)])
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            print("[retrain] Training failed:\n", result.stderr)
        else:
            print("[retrain] Training completed:\n", result.stdout)

    background.add_task(task)
    return {"status": "queued"}


@router.get("/health")
async def health() -> dict[str, Literal["ok"]]:
    return {"status": "ok"}
