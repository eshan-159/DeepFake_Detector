# Dazza

**AI-Powered Deepfake Detection with Grad-CAM Explainability**

[![License](https://img.shields.io/badge/license-MIT-8b5cf6.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-8b5cf6.svg)](https://python.org)
[![Node](https://img.shields.io/badge/node-18.x-8b5cf6.svg)](https://nodejs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-8b5cf6.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-8b5cf6.svg)](https://react.dev)

---

> **Responsible AI Notice:** This repository is for research into detecting synthetic media. Never use it to create or distribute deepfakes of real people without their explicit, informed consent.

---

## Features

| Detection Engine | Elegant Dark UI |
|------------------|-----------------|
| Hybrid CNN with attention-augmented ResNet | Premium glass-morphism design |
| ~92% validation accuracy | Drag & drop image upload |
| Real-time inference (<100ms) | Live confidence meter |
| Grad-CAM saliency visualization | Space-themed ambience |

| Research Tools | Production Ready |
|----------------|------------------|
| Synthetic data generation | FastAPI backend with OpenAPI |
| FaceForensics++ / DFDC support | Dockerized services |
| Mixed-precision training (AMP) | GitHub Actions CI/CD |
| Experiment tracking | Safety guardrails |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         DAZZA SYSTEM                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐    ┌──────────────────┐                  │
│  │  React Frontend  │───▶│  FastAPI Backend │                  │
│  │                  │    │                  │                  │
│  │  • Upload Panel  │    │  • /predict      │                  │
│  │  • Results View  │◀───│  • /metrics      │                  │
│  │  • Grad-CAM      │    │  • /health       │                  │
│  │  • Metrics       │    │  • Grad-CAM Gen  │                  │
│  └──────────────────┘    └────────┬─────────┘                  │
│                                   │                             │
│                          ┌────────▼─────────┐                  │
│                          │   Hybrid CNN     │                  │
│                          │   + Grad-CAM     │                  │
│                          └────────┬─────────┘                  │
│                                   │                             │
│  ┌──────────────────┐    ┌────────▼─────────┐                  │
│  │ Training Pipeline│───▶│   Checkpoints    │                  │
│  │                  │    │   (models/*.pt)  │                  │
│  │  • Data Pipeline │    └──────────────────┘                  │
│  │  • Train Loop    │                                          │
│  │  • Evaluation    │                                          │
│  └──────────────────┘                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
dazza/
├── src/
│   ├── frontend/           # React + Vite + Tailwind
│   │   ├── src/App.jsx     # Main component
│   │   ├── src/index.css   # Design system
│   │   └── UI_STYLE.md     # Style documentation
│   ├── backend/            # FastAPI service
│   │   └── app/
│   │       ├── main.py     # App factory
│   │       ├── predict.py  # Prediction endpoint
│   │       └── model.py    # Model + Grad-CAM
│   └── train/              # Training pipeline
│       ├── train.py        # Training loop
│       ├── eval.py         # Evaluation
│       └── models/         # CNN architecture
├── api/                    # Vercel serverless
├── models/                 # Saved checkpoints
├── static/saliency/        # Grad-CAM outputs
└── tests/                  # Pytest suite
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- (Optional) CUDA GPU for training

### Installation

```bash
# Clone repository
git clone https://github.com/eshan-159/DeepFake_Detector.git
cd DeepFake_Detector

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
npm --prefix src/frontend install
```

### Run the Application

**Terminal 1 - Backend:**
```bash
export PYTHONPATH=$PWD/src:$PYTHONPATH
uvicorn src.backend.app.main:app --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
npm --prefix src/frontend run dev -- --host
```

Open **http://localhost:5173** in your browser.

---

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/predict` | POST | Upload image, get prediction |
| `/metrics` | GET | Prediction statistics |
| `/health` | GET | Service health check |
| `/saliency/{id}.png` | GET | Grad-CAM images |

### Example

```bash
curl -X POST http://localhost:8000/predict -F "image=@photo.jpg"
```

Response:
```json
{
  "label": "deepfake",
  "confidence": 0.934,
  "saliency_path": "/saliency/abc123.png",
  "inference_ms": 47.2
}
```

---

## UI Design

Dazza uses an **Elegant Dark Interface** design:

| Element | Value |
|---------|-------|
| Background | `#030305` with violet glow |
| Panels | Glass-morphism, 16px blur |
| Accent | `#8b5cf6` to `#6366f1` |
| Typography | Inter, JetBrains Mono |
| Border Radius | 12-16px |

See `src/frontend/UI_STYLE.md` for the complete style guide.

---

## Training

```bash
# Generate synthetic data
python src/train/gen_synthetic.py --output data/synth --n 10000 --dry-run

# Train model
python src/train/train.py --config src/train/configs/default.yaml --save-dir models/run_001

# Evaluate
python src/train/eval.py --checkpoint models/run_001/best.pt --report reports/run_001.json
```

---

## Docker

```bash
docker compose up --build
```

---

## Testing

```bash
PYTHONPATH=$PWD/src:$PYTHONPATH pytest -v
```

---

## Roadmap

- [ ] Guided Grad-CAM, LayerCAM
- [ ] Video deepfake detection
- [ ] Browser extension
- [ ] Model fine-tuning UI
- [ ] Multi-language support

---

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/name`
3. Commit changes: `git commit -m 'Add feature'`
4. Push: `git push origin feature/name`
5. Open Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

[MIT License](LICENSE)

---

**Built for responsible AI research**
