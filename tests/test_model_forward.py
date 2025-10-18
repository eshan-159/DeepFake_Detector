import torch

from src.train.models.hybrid_cnn import HybridDeepfakeModel, ModelConfig


def test_model_forward_shape_cpu():
    model = HybridDeepfakeModel(ModelConfig(num_classes=2, backbone="resnet18"))
    inputs = torch.randn(2, 3, 224, 224)
    logits = model(inputs)
    assert logits.shape == (2, 2)


def test_cam_layer_exists():
    model = HybridDeepfakeModel()
    target_layer = model.cam_target_layer
    assert hasattr(target_layer, "weight")
