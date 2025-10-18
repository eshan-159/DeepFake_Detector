#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-models/demo/demo.pt}"
TARGET_DIR="$(dirname "$TARGET")"
mkdir -p "$TARGET_DIR"

if [ -f "$TARGET" ]; then
  echo "[download_demo_checkpoint] Checkpoint already present at $TARGET"
  exit 0
fi

if [ -n "${DEMO_CHECKPOINT_URL:-}" ]; then
  echo "[download_demo_checkpoint] Downloading demo checkpoint from $DEMO_CHECKPOINT_URL"
  curl -L "$DEMO_CHECKPOINT_URL" -o "$TARGET"
  exit 0
fi

echo "[download_demo_checkpoint] No remote URL provided; creating a random warm-start checkpoint."
python - <<'PY'
from pathlib import Path
import torch

from src.train.models.hybrid_cnn import HybridDeepfakeModel, ModelConfig

path = Path("${TARGET}")
model = HybridDeepfakeModel(ModelConfig(num_classes=2))
state_dict = model.state_dict()
for key, value in state_dict.items():
    if value.dtype.is_floating_point:
        state_dict[key] = torch.randn_like(value) * 0.02
path.parent.mkdir(parents=True, exist_ok=True)
torch.save(state_dict, path)
print(f"Random checkpoint written to {path}")
PY
