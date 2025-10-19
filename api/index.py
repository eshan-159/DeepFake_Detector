from __future__ import annotations

import sys
from pathlib import Path

# Ensure the project root and src directory are on the Python path when running on Vercel.
ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from src.backend.app.main import create_app  # noqa: E402

app = create_app()
