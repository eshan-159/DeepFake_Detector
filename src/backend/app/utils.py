from __future__ import annotations

import io
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import numpy as np
from PIL import Image
import torch
from torch.utils.hooks import RemovableHandle
from torchvision import transforms

from src.train.models.hybrid_cnn import HybridDeepfakeModel

SALIENCY_ROOT = Path("static/saliency")
SALIENCY_ROOT.mkdir(parents=True, exist_ok=True)

_preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.25, 0.25, 0.25]),
])


@dataclass
class GradCAMResult:
    saliency_path: Path
    elapsed_ms: float


class GradCAM:
    """Minimal Grad-CAM implementation for the hybrid CNN."""

    def __init__(self, model: HybridDeepfakeModel, target_layer: torch.nn.Module | None = None) -> None:
        self.model = model
        self.target_layer = target_layer or model.cam_target_layer
        self._activations = None
        self._gradients = None
        self._handles: List[RemovableHandle] = []
        self._register_hooks()

    def _register_hooks(self) -> None:
        def forward_hook(_module, _input, output):
            self._activations = output.detach()

        def backward_hook(_module, grad_input, grad_output):
            self._gradients = grad_output[0].detach()

        self._handles.append(self.target_layer.register_forward_hook(forward_hook))
        self._handles.append(self.target_layer.register_full_backward_hook(backward_hook))

    def close(self) -> None:
        for handle in self._handles:
            handle.remove()
        self._handles.clear()

    def generate(self, raw_image: Image.Image) -> Path:
        if self._activations is None or self._gradients is None:
            raise RuntimeError("Hooks did not capture activations/gradients.")
        gradients = self._gradients.mean(dim=(2, 3), keepdim=True)
        weighted = (self._activations * gradients).sum(dim=1, keepdim=True)
        heatmap = torch.relu(weighted)
        heatmap = heatmap.squeeze().cpu().numpy()
        heatmap -= heatmap.min()
        heatmap /= np.clip(heatmap.max(), a_min=1e-8, a_max=None)

        heatmap_img = Image.fromarray(np.uint8(heatmap * 255), mode="L").resize(raw_image.size)
        heatmap_img = heatmap_img.convert("RGBA")
        overlay = raw_image.convert("RGBA")
        heatmap_img.putalpha(128)
        composite = Image.alpha_composite(overlay, heatmap_img)

        saliency_path = SALIENCY_ROOT / f"{uuid.uuid4().hex}.png"
        composite.save(saliency_path)
        return saliency_path


def read_image_to_pil(data: bytes) -> Image.Image:
    return Image.open(io.BytesIO(data)).convert("RGB")


def preprocess_tensor(image: Image.Image) -> torch.Tensor:
    return _preprocess(image).unsqueeze(0)


def run_inference(
    model: HybridDeepfakeModel,
    image: Image.Image,
    device: torch.device,
) -> Tuple[torch.Tensor, torch.Tensor, GradCAMResult]:
    start = time.time()
    tensor = preprocess_tensor(image).to(device)
    tensor.requires_grad_(True)

    cam = GradCAM(model)
    try:
        logits = model(tensor)
        probs = torch.softmax(logits, dim=1)
        confidence, pred_idx = probs.max(dim=1)
        class_score = logits[0, pred_idx.item()]
        model.zero_grad(set_to_none=True)
        class_score.backward(retain_graph=True)

        saliency_path = cam.generate(image)
    finally:
        cam.close()
    elapsed_ms = (time.time() - start) * 1000

    return probs.detach(), torch.tensor(pred_idx.item()), GradCAMResult(saliency_path, elapsed_ms)
