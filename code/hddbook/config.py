"""Global paths, deterministic RNG and figure style for the book experiments.

All scripts must obtain randomness via :func:`rng` and must not hard-code
absolute paths outside the repository.
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
FIG_DIR = REPO_ROOT / "figures"
DATA_DIR = REPO_ROOT / "code" / "data"
EXPERIMENT_DIR = REPO_ROOT / "code" / "experiments"

#: External root for proprietary/large datasets (company measured signals).
#: Set HDD_DATA_ROOT to use it; scripts must degrade gracefully when unset.
EXTERNAL_DATA_ROOT = Path(os.environ["HDD_DATA_ROOT"]) if os.environ.get("HDD_DATA_ROOT") else None

DEFAULT_SEED = 20261111

#: Chinese-capable font fallbacks (macOS/Linux/Windows). Matplotlib silently
#: falls back to DejaVu Sans when none is installed.
CJK_FONTS = [
    "Hiragino Sans GB",
    "PingFang HK",
    "STHeiti",
    "Songti SC",
    "Arial Unicode MS",
    "Noto Sans CJK SC",
    "Source Han Sans SC",
    "Microsoft YaHei",
    "SimHei",
    "WenQuanYi Zen Hei",
    "DejaVu Sans",
]


def rng(seed: int | None = None) -> np.random.Generator:
    """Return a deterministic NumPy generator (defaults to DEFAULT_SEED)."""
    return np.random.default_rng(DEFAULT_SEED if seed is None else seed)


def ensure_dir(path: str | Path) -> Path:
    """Create a directory (and parents) and return it as a Path."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p
