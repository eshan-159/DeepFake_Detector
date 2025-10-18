from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class PredictionResponse(BaseModel):
    label: Literal["real", "deepfake"]
    confidence: float = Field(ge=0.0, le=1.0)
    saliency_path: str
    inference_ms: float


class MetricsResponse(BaseModel):
    total_predictions: int
    class_counts: dict[str, int]
    running_accuracy: float
    updated_at: datetime


class RetrainRequest(BaseModel):
    config_path: str
    epochs: Optional[int] = None
    consent_acknowledged: bool = False