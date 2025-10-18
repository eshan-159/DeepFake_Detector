#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

log() {
  printf "[run_local] %s\n" "$1"
}

log "Creating Python virtual environment (.venv)"
python -m venv .venv
source .venv/bin/activate

log "Installing Python dependencies"
pip install --upgrade pip
pip install -r requirements.txt

log "Generating placeholder synthetic data (dry run)"
python src/train/gen_synthetic.py \
  --output data/demo_synth \
  --n 200 \
  --image-size 256 \
  --dry-run

log "Preparing toy train/val split"
python - <<'PY'
from pathlib import Path
import shutil

src = Path("data/demo_synth")
dst = Path("data/demo")
if dst.exists():
    shutil.rmtree(dst)
(dst / "train" / "real").mkdir(parents=True, exist_ok=True)
(dst / "train" / "deepfake").mkdir(parents=True, exist_ok=True)
(dst / "val" / "real").mkdir(parents=True, exist_ok=True)
(dst / "val" / "deepfake").mkdir(parents=True, exist_ok=True)

real_images = sorted((src / "real").glob("*.png"))
fake_images = sorted((src / "deepfake").glob("*.png"))

for idx, path in enumerate(real_images):
    target = dst / ("train" if idx % 2 == 0 else "val") / "real" / path.name
    shutil.copyfile(path, target)

for idx, path in enumerate(fake_images):
    target = dst / ("train" if idx % 2 == 0 else "val") / "deepfake" / path.name
    shutil.copyfile(path, target)
PY

log "Running one-epoch training (AMP disabled for CPU compatibility)"
python src/train/train.py --config src/train/configs/default.yaml --epochs 1 --save-dir models/demo --no-amp

log "Evaluating demo checkpoint"
mkdir -p reports
python src/train/eval.py --config src/train/configs/default.yaml --checkpoint models/demo/demo.pt --report reports/demo.json

log "Installing frontend dependencies"
npm --prefix src/frontend install

log "Starting backend (background)"
uvicorn src.backend.app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
trap 'kill "$BACKEND_PID" 2>/dev/null || true' EXIT

log "Starting frontend dev server (Ctrl+C to stop)"
npm --prefix src/frontend run dev -- --host 0.0.0.0 --port 5173
