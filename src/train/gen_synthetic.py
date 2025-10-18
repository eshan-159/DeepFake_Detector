"""
DO NOT use this script to generate or distribute deepfakes of real people without explicit consent.
Generating deepfakes of non-consenting individuals is unethical and may be illegal. This tool defaults
to consent-only synthetic identities and requires an explicit override (with acknowledgement) to run
on real names. Use responsibly.
"""

from __future__ import annotations

import argparse
import json
import os
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

import numpy as np
from PIL import Image, ImageDraw
from rich import print as rprint
from tqdm import trange

try:
    from diffusers import StableDiffusionPipeline
    import torch
except ImportError:  # pragma: no cover - diffusers optional for CI
    StableDiffusionPipeline = None  # type: ignore
    torch = None  # type: ignore


@dataclass
class GenerationConfig:
    output: Path
    n: int
    preset: str
    image_size: int
    prompt: str
    negative_prompt: str
    steps: int
    guidance_scale: float
    consent_only: bool
    allow_nonconsensual: bool
    acknowledge_risk: bool
    identity_file: Optional[Path]
    dry_run: bool
    seed: Optional[int]
    model_id: str
    hf_token: Optional[str]


SAFE_DEFAULT_PROMPT = (
    "portrait photo of a synthetic person, neutral lighting, high detail, studio background, "
    "created with full consent, no resemblance to real public figures"
)
NEGATIVE_PROMPT = "low quality, artifacts, deformed, duplicated, signature, watermark"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic deepfake training images safely.")
    parser.add_argument("--output", type=Path, required=True, help="Output directory.")
    parser.add_argument("--n", type=int, default=1000, help="Number of images to generate.")
    parser.add_argument("--preset", choices=["synthetic-only", "dreambooth", "lora"], default="synthetic-only")
    parser.add_argument("--image-size", type=int, default=512)
    parser.add_argument("--prompt", type=str, default=SAFE_DEFAULT_PROMPT)
    parser.add_argument("--negative-prompt", type=str, default=NEGATIVE_PROMPT)
    parser.add_argument("--steps", type=int, default=30)
    parser.add_argument("--guidance-scale", type=float, default=7.5)
    parser.add_argument("--consent-only", action="store_true", default=True)
    parser.add_argument("--allow-nonconsensual", action="store_true")
    parser.add_argument(
        "--i-understand-the-risks",
        dest="acknowledge",
        action="store_true",
        help="Required if you disable consent-only safeguards.",
    )
    parser.add_argument(
        "--identity-file",
        type=Path,
        help="Optional JSON/JSONL listing consented identity prompts (each entry with 'name' & 'prompt').",
    )
    parser.add_argument("--model", type=str, default=os.getenv("SD_MODEL_ID", "runwayml/stable-diffusion-v1-5"))
    parser.add_argument("--hf-token", type=str, default=os.getenv("HF_TOKEN"))
    parser.add_argument("--dry-run", action="store_true", help="Create placeholder images without diffusion.")
    parser.add_argument("--seed", type=int)
    return parser.parse_args()


def _validate_consent(config: GenerationConfig, identities: Iterable[dict[str, str]]) -> None:
    if not config.consent_only and not (config.allow_nonconsensual and config.acknowledge_risk):
        raise SystemExit(
            "Consent-only guard is active. To override you must pass --allow-nonconsensual "
            "AND --i-understand-the-risks. This action is logged."
        )
    if config.consent_only:
        for entry in identities:
            name = entry.get("name", "").strip().lower()
            if name and any(part in name for part in ("celebrity", "president", "actor", "politician")):
                raise SystemExit(
                    "Identity list appears to reference public figures. Remove them or override the consent guard "
                    "(not recommended)."
                )


def _load_identities(path: Optional[Path]) -> List[dict[str, str]]:
    if not path:
        return []
    entries: List[dict[str, str]] = []
    if path.suffix.lower() == ".jsonl":
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
    else:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                entries.extend(data)
            else:
                entries.append(data)
    return entries


def _seed_everything(seed: Optional[int]) -> None:
    if seed is None:
        return
    random.seed(seed)
    np.random.seed(seed)
    if torch is not None:
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)


def _placeholder_image(path: Path, image_size: int, label: str) -> None:
    rng = np.random.default_rng()
    array = rng.integers(0, 255, size=(image_size, image_size, 3), dtype=np.uint8)
    img = Image.fromarray(array, mode="RGB")
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), label, fill=(255, 255, 255))
    img.save(path)


def _load_pipeline(config: GenerationConfig, token: Optional[str]):
    if config.dry_run:
        return None
    if StableDiffusionPipeline is None:
        raise ImportError("diffusers not installed; run `pip install diffusers`.")
    rprint("[cyan]Loading Stable Diffusion pipeline...")
    pipeline = StableDiffusionPipeline.from_pretrained(
        config.model_id,
        torch_dtype=torch.float16 if torch and torch.cuda.is_available() else torch.float32,
        use_auth_token=token,
    )
    if torch and torch.cuda.is_available():
        pipeline = pipeline.to("cuda")
    return pipeline


def _generate_with_pipeline(config: GenerationConfig, identities: List[dict[str, str]]) -> None:
    pipeline = _load_pipeline(config, config.hf_token)
    config.output.mkdir(parents=True, exist_ok=True)
    prompts = [entry.get("prompt", SAFE_DEFAULT_PROMPT) for entry in identities] or [config.prompt]
    for idx in trange(config.n, desc="generating"):
        prompt = prompts[idx % len(prompts)]
        if pipeline is None:
            label = "real" if idx % 2 == 0 else "deepfake"
            _placeholder_image(config.output / f"{label}_{idx:05d}.png", config.image_size, label)
            continue
        image = pipeline(
            prompt=prompt,
            negative_prompt=config.negative_prompt,
            guidance_scale=config.guidance_scale,
            num_inference_steps=config.steps,
            height=config.image_size,
            width=config.image_size,
        ).images[0]
        label = "real" if idx % 2 == 0 else "deepfake"
        image.save(config.output / f"{label}_{idx:05d}.png")


def main() -> None:
    args = parse_args()
    config = GenerationConfig(
        output=args.output,
        n=args.n,
        preset=args.preset,
        image_size=args.image_size,
        prompt=args.prompt,
        negative_prompt=args.negative_prompt,
        steps=args.steps,
        guidance_scale=args.guidance_scale,
        consent_only=args.consent_only,
        allow_nonconsensual=args.allow_nonconsensual,
        acknowledge_risk=args.acknowledge,
        identity_file=args.identity_file,
        dry_run=args.dry_run,
        seed=args.seed,
        model_id=args.model,
        hf_token=args.hf_token,
    )

    _seed_everything(config.seed)
    identities = _load_identities(config.identity_file)
    _validate_consent(config, identities)

    rprint(
        f"[bold green]Generating {config.n} images to {config.output} using preset '{config.preset}' "
        f"(dry_run={config.dry_run})"
    )
    config.output.mkdir(parents=True, exist_ok=True)

    if config.preset in {"dreambooth", "lora"}:
        rprint(
            "[yellow]DreamBooth/LoRA fine-tuning hooks are stubs in this demo. "
            "Provide consented identity images and integrate with Accelerate for full training."
        )

    _generate_with_pipeline(config, identities)
    rprint("[bold green]Synthetic generation complete.")


if __name__ == "__main__":
    main()
