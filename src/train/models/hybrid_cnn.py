from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import torch
from torch import nn
from torchvision import models


@dataclass(frozen=True)
class ModelConfig:
    """Configuration object for the hybrid CNN."""

    num_classes: int = 2
    backbone: str = "resnet18"
    pretrained: bool = False
    dropout: float = 0.2


class HybridDeepfakeModel(nn.Module):
    """Hybrid CNN for real vs deepfake classification.

    Combines a ResNet backbone, extra convolutional refinement, and a
    lightweight attention head suitable for Grad-CAM style explainability.
    """

    def __init__(self, config: ModelConfig | None = None) -> None:
        super().__init__()
        self.config = config or ModelConfig()
        self.backbone, backbone_channels = self._build_backbone(
            self.config.backbone, self.config.pretrained
        )
        self.refine_conv = nn.Sequential(
            nn.Conv2d(backbone_channels, 384, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(384),
            nn.SiLU(inplace=True),
            nn.Conv2d(384, 192, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(192),
            nn.SiLU(inplace=True),
        )
        self.attention_head = nn.Sequential(
            nn.Conv2d(192, 64, kernel_size=1, bias=False),
            nn.BatchNorm2d(64),
            nn.SiLU(inplace=True),
            nn.Conv2d(64, 1, kernel_size=1),
            nn.Sigmoid(),
        )
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Dropout(self.config.dropout),
            nn.Linear(192, 96),
            nn.SiLU(inplace=True),
            nn.Dropout(self.config.dropout),
            nn.Linear(96, self.config.num_classes),
        )
        self.register_buffer("last_attention", torch.zeros(1, 1, 1, 1), persistent=False)

    @staticmethod
    def _build_backbone(name: str, pretrained: bool) -> Tuple[nn.Module, int]:
        name = name.lower()
        weights = None
        if pretrained:
            if name == "resnet18":
                weights = models.ResNet18_Weights.DEFAULT
            elif name == "resnet34":
                weights = models.ResNet34_Weights.DEFAULT
        if name == "resnet18":
            backbone = models.resnet18(weights=weights)
            out_channels = 512
        elif name == "resnet34":
            backbone = models.resnet34(weights=weights)
            out_channels = 512
        elif name == "convnext_tiny":
            weights = models.ConvNeXt_Tiny_Weights.DEFAULT if pretrained else None
            backbone = models.convnext_tiny(weights=weights)
            out_channels = backbone.features[-1][0].out_channels
        else:
            raise ValueError(f"Unsupported backbone: {name}")
        if "convnext" in name:
            feature_extractor = backbone.features
        else:
            feature_extractor = nn.Sequential(*list(backbone.children())[:-2])
        return feature_extractor, out_channels

    def forward_features(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        features = self.backbone(x)
        refined = self.refine_conv(features)
        attention_map = self.attention_head(refined)
        self.last_attention = attention_map.detach()
        return refined, attention_map

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        refined, attention_map = self.forward_features(x)
        weighted = refined * (1 + attention_map)
        logits = self.classifier(weighted)
        return logits

    @property
    def cam_target_layer(self) -> nn.Module:
        """Layer to hook for Grad-CAM."""
        return self.refine_conv[-3]  # second BatchNorm output
