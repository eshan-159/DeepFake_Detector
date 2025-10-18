from pathlib import Path

from PIL import Image

from src.train.data_pipeline import DataConfig, create_dataloaders


def _write_image(path: Path, color: tuple[int, int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (64, 64), color=color).save(path)


def test_create_dataloaders(tmp_path):
    train_real = tmp_path / "train" / "real"
    train_fake = tmp_path / "train" / "deepfake"
    val_real = tmp_path / "val" / "real"
    val_fake = tmp_path / "val" / "deepfake"

    for idx in range(4):
        _write_image(train_real / f"real_{idx}.png", (255, 0, 0))
        _write_image(train_fake / f"fake_{idx}.png", (0, 0, 255))
        _write_image(val_real / f"real_{idx}.png", (255, 0, 0))
        _write_image(val_fake / f"fake_{idx}.png", (0, 0, 255))

    config = DataConfig(
        train_dir=train_real.parent.parent / "train",
        val_dir=val_real.parent.parent / "val",
        image_size=128,
        batch_size=2,
        num_workers=0,
    )
    train_loader, val_loader = create_dataloaders(config)

    assert len(train_loader.dataset) == 8
    assert len(val_loader.dataset) == 8
    batch = next(iter(train_loader))
    images, labels = batch
    assert images.shape[1:] == (3, 128, 128)
    assert labels.shape[0] == 2
