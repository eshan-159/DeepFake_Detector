from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .predict import router as predict_router
from . import utils


def create_app() -> FastAPI:
    app = FastAPI(title="Deepfake Detector", version="0.2.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_headers=["*"],
        allow_methods=["*"],
    )
    saliency_root = utils.SALIENCY_ROOT
    Path(saliency_root).mkdir(parents=True, exist_ok=True)
    app.mount("/saliency", StaticFiles(directory=saliency_root), name="saliency")
    app.include_router(predict_router)
    return app


app = create_app()
