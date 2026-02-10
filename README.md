# Dazza — AI-Powered Deepfake Detection

<div align="center">

![Dazza Logo](docs/assets/dazza_hero.png)

**Real-time deepfake detection with Grad-CAM explainability**

[![License](https://img.shields.io/badge/license-MIT-8b5cf6.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-8b5cf6.svg)](https://python.org)
[![Node](https://img.shields.io/badge/node-18.x-8b5cf6.svg)](https://nodejs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-8b5cf6.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-8b5cf6.svg)](https://react.dev)

[Demo](#getting-started) • [Documentation](#inference-service) • [Contributing](#contributing)

</div>

---

> **⚠️ Responsible AI Notice:** This repository is for research into detecting synthetic media. Never use it to create or distribute deepfakes of real people without their explicit, informed consent. Violations may be illegal and are unequivocally unethical.

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🎯 Detection Engine
- Hybrid CNN with attention-augmented ResNet backbone
- ~92% validation accuracy on balanced datasets
- Real-time inference (<100ms on CPU)
- Grad-CAM saliency visualization

</td>
<td width="50%">

### 🎨 Elegant Dark UI
- Premium glass-morphism design
- Drag & drop image upload
- Live confidence meter
- Space-themed ambience

</td>
</tr>
<tr>
<td width="50%">

### 🔬 Research Tools
- Synthetic data generation (Stable Diffusion)
- FaceForensics++ / DFDC ingestion
- Mixed-precision training (AMP)
- Experiment tracking & checkpointing

</td>
<td width="50%">

### 🚀 Production Ready
- FastAPI backend with OpenAPI docs
- Dockerized services
- GitHub Actions CI/CD
- Consent-first safety guardrails

</td>
</tr>
</table>

---

## 📸 Screenshots

<div align="center">

### Upload Interface
![Dazza Upload Interface](docs/assets/dazza_upload.png)
*Elegant drag & drop upload with real-time file preview*

### Detection Results
![Dazza Detection Results](docs/assets/dazza_results.png)
*Confidence scoring with Grad-CAM saliency overlay*

### API Metrics Dashboard
![Dazza Metrics](docs/assets/dazza_metrics.png)
*Live prediction statistics and class distribution*

</div>

---

## 🏗️ Architecture

```mermaid
flowchart LR
    subgraph Frontend["🎨 Frontend (React + Vite)"]
        A[Upload Panel] --> B[Results Display]
        B --> C[Grad-CAM Overlay]
        B --> D[Metrics Dashboard]
    end
    
    subgraph Backend["⚡ Backend (FastAPI)"]
        E[/predict] --> F[Hybrid CNN]
        F --> G[Grad-CAM]
        H[/metrics] --> I[Stats Engine]
    end
    
    subgraph Training["🔬 Training Pipeline"]
        J[Data Pipeline] --> K[Model Training]
        K --> L[Evaluation]
        L --> M[Checkpoints]
    end
    
    A -->|POST image| E
    G -->|saliency.png| C
    I -->|JSON| D
    M -->|demo.pt| F
```

---

## 📁 Project Structure

```
dazza/
├── src/
│   ├── frontend/          # React + Vite + Tailwind UI
│   │   ├── src/App.jsx    # Main application component
│   │   ├── src/index.css  # Dazza design system
│   │   └── UI_STYLE.md    # UI documentation
│   ├── backend/           # FastAPI inference service
│   │   └── app/
│   │       ├── main.py    # Application factory
│   │       ├── predict.py # /predict endpoint
│   │       └── model.py   # Model loading & Grad-CAM
│   └── train/             # Training pipeline
│       ├── train.py       # Training loop
│       ├── eval.py        # Evaluation metrics
│       └── models/        # Hybrid CNN architecture
├── api/                   # Vercel serverless entry
├── models/                # Saved checkpoints
├── static/saliency/       # Generated Grad-CAM images
├── tests/                 # Pytest suite
└── docs/assets/           # Documentation images
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- (Optional) CUDA GPU for training

### Quick Start

```bash
# Clone the repository
git clone https://github.com/eshan-159/DeepFake_Detector.git
cd DeepFake_Detector

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
npm --prefix src/frontend install

# Start backend (Terminal 1)
export PYTHONPATH=$PWD/src:$PYTHONPATH
uvicorn src.backend.app.main:app --host 0.0.0.0 --port 8000

# Start frontend (Terminal 2)
npm --prefix src/frontend run dev -- --host
```

Open **http://localhost:5173** to use Dazza!

### One-Command Demo

```bash
bash examples/run_local.sh
```

---

## 🔌 API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/predict` | POST | Upload image, returns label, confidence, saliency path |
| `/metrics` | GET | Prediction statistics and class distribution |
| `/health` | GET | Liveness check (`{"status": "ok"}`) |
| `/saliency/{id}.png` | GET | Static Grad-CAM overlay images |

### Example Request

```bash
curl -X POST "http://localhost:8000/predict" \
  -F "image=@face.jpg" \
  | jq
```

```json
{
  "label": "deepfake",
  "confidence": 0.934,
  "saliency_path": "/saliency/abc123.png",
  "inference_ms": 47.2
}
```

---

## 🎨 UI Design System

Dazza uses an **Elegant Dark Interface** design language:

| Element | Specification |
|---------|---------------|
| **Background** | `#030305` with radial violet glow |
| **Panels** | Glass-morphism with 16px blur |
| **Accent** | Violet gradient (`#8b5cf6` → `#6366f1`) |
| **Typography** | Inter + JetBrains Mono |
| **Corners** | 12-16px border radius |

See [`src/frontend/UI_STYLE.md`](src/frontend/UI_STYLE.md) for the complete style guide.

---

## 🔬 Training

```bash
# Generate synthetic training data
python src/train/gen_synthetic.py \
  --output data/synth \
  --n 10000 \
  --dry-run

# Train the model
python src/train/train.py \
  --config src/train/configs/default.yaml \
  --save-dir models/run_001

# Evaluate
python src/train/eval.py \
  --checkpoint models/run_001/best.pt \
  --report reports/run_001.json
```

---

## 🐳 Docker

```bash
# Run full stack
docker compose up --build

# Training with GPU
docker run --gpus all -v $(pwd)/data:/app/data dazza-train
```

---

## 🧪 Testing

```bash
PYTHONPATH=$PWD/src:$PYTHONPATH pytest -v
```

---

## 🛣️ Roadmap

- [ ] Advanced explainability (Guided Grad-CAM, LayerCAM)
- [ ] Video deepfake detection
- [ ] Browser extension for real-time checking
- [ ] Model fine-tuning via UI
- [ ] Multi-language support

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

**Built with 💜 for responsible AI research**

[⬆ Back to top](#dazza--ai-powered-deepfake-detection)

</div>
