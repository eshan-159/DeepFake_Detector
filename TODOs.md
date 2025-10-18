# TODOs

- [ ] Train full-scale model to reach ~92.4% validation accuracy using ≥10k balanced samples.
- [ ] Implement DreamBooth/LoRA fine-tuning workflow in `src/train/gen_synthetic.py` with consent verification prompts.
- [ ] Acquire and preprocess FaceForensics++ / DFDC datasets (requires license compliance and manual download).
- [ ] Harden `/retrain` endpoint with authentication, job queue, and resource quotas before production use.
- [ ] Log provenance metadata to SQLite or MLflow for every sample and checkpoint.
- [ ] Expand explainability (Guided Grad-CAM, LayerCAM) and add frontend overlays for multiple layers.
- [ ] Extend CI with linting, type-checking, frontend tests, and container security scans.
- [ ] Provision long-term artifact storage (S3, Azure Blob, or Hugging Face Spaces) for large checkpoints.
