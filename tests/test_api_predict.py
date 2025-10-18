import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image
import torch

from src.backend.app.main import create_app
from src.backend.app import utils


@pytest.fixture(autouse=True)
def saliency_dir(tmp_path, monkeypatch):
    saliency_root = tmp_path / "saliency"
    saliency_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(utils, "SALIENCY_ROOT", saliency_root)
    return saliency_root


def test_predict_endpoint(monkeypatch, saliency_dir):
    app = create_app()
    client = TestClient(app)

    gradcam_result = utils.GradCAMResult(saliency_path=saliency_dir / "dummy.png", elapsed_ms=12.5)
    gradcam_result.saliency_path.write_bytes(b"fake")

    def fake_run_inference(model, image, device):
        return torch.tensor([[0.2, 0.8]]), torch.tensor(1), gradcam_result

    monkeypatch.setattr(utils, "run_inference", fake_run_inference)

    image = Image.new("RGB", (64, 64), color=(255, 0, 0))
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)

    response = client.post("/predict", files={"image": ("test.png", buf, "image/png")})
    assert response.status_code == 200
    data = response.json()
    assert data["label"] == "deepfake"
    assert data["confidence"] == pytest.approx(0.8, rel=1e-3)
    assert data["saliency_path"].startswith("/saliency/")
    assert data["inference_ms"] == pytest.approx(12.5, rel=1e-3)


def test_metrics_endpoint(monkeypatch, saliency_dir):
    app = create_app()
    client = TestClient(app)

    monkeypatch.setattr(utils, "run_inference", lambda *args, **kwargs: (
        torch.tensor([[0.6, 0.4]]), torch.tensor(0),
        utils.GradCAMResult(saliency_path=saliency_dir / "dummy2.png", elapsed_ms=5.0)
    ))
    (saliency_dir / "dummy2.png").write_bytes(b"fake")

    image = Image.new("RGB", (32, 32), color=(0, 255, 0))
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)
    client.post("/predict", files={"image": ("test.png", buf, "image/png")})

    response = client.get("/metrics")
    assert response.status_code == 200
    payload = response.json()
    assert "total_predictions" in payload
    assert payload["total_predictions"] >= 1