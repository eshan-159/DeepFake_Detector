"""
Dazza - DeepFake Detector API (Vercel Demo Mode)

This is a lightweight demo API that runs on Vercel without PyTorch.
For full inference capabilities, run the backend locally with:
    cd src/backend && uvicorn app.main:app --reload
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import random
import hashlib
from datetime import datetime

app = FastAPI(
    title="Dazza - DeepFake Detector API",
    description="Demo API for the Dazza DeepFake Detection system",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PredictionResponse(BaseModel):
    label: str
    confidence: float
    processing_time_ms: float
    model_version: str
    demo_mode: bool = True


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    demo_mode: bool = True


@app.get("/")
async def root():
    return {
        "name": "Dazza - DeepFake Detector",
        "version": "1.0.0",
        "status": "running",
        "demo_mode": True,
        "message": "This is a demo API. For full inference, run the backend locally.",
        "docs_url": "/docs",
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        demo_mode=True,
    )


@app.post("/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)):
    """
    Demo prediction endpoint.
    
    In demo mode, returns a simulated prediction based on file hash.
    For real inference, run the backend locally with PyTorch.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Read file and create deterministic "prediction" based on hash
    content = await file.read()
    file_hash = hashlib.md5(content).hexdigest()
    
    # Use hash to generate consistent pseudo-random result
    random.seed(file_hash)
    confidence = random.uniform(0.65, 0.98)
    is_real = random.random() > 0.5
    
    label = "Real" if is_real else "DeepFake"
    if not is_real:
        confidence = 1 - confidence + random.uniform(0.1, 0.2)
        confidence = min(confidence, 0.99)
    
    return PredictionResponse(
        label=label,
        confidence=round(confidence, 4),
        processing_time_ms=round(random.uniform(50, 150), 2),
        model_version="demo-1.0",
        demo_mode=True,
    )


@app.get("/metrics")
async def metrics():
    """Return simulated metrics for demo purposes."""
    return {
        "total_predictions": 0,
        "model_version": "demo-1.0",
        "demo_mode": True,
        "note": "Metrics are simulated in demo mode",
    }
