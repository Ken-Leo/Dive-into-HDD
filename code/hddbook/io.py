"""Dataset loading, checksums and figure-manifest bookkeeping."""

from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path

import numpy as np
import yaml

from . import config


def sha256(path: str | Path) -> str:
    """Return the SHA256 hex digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_dataset(name: str) -> dict:
    """Load a dataset from ``code/data/<name>``.

    Supported formats: ``.npz``, ``.json``, ``.csv``.  The directory must
    contain a README describing provenance and licence.
    """
    root = config.DATA_DIR / name
    if not root.is_dir():
        raise FileNotFoundError(f"dataset directory not found: {root}")
    readme = root / "README.md"
    if not readme.exists():
        raise FileNotFoundError(f"dataset README missing: {readme}")
    for ext, loader in ((".npz", _load_npz), (".json", _load_json), (".csv", _load_csv)):
        files = sorted(root.glob(f"*{ext}"))
        if files:
            return {p.stem: loader(p) for p in files}
    raise FileNotFoundError(f"no .npz/.json/.csv dataset found in {root}")


def _load_npz(path: Path) -> dict:
    with np.load(path) as data:
        return {k: data[k] for k in data.files}


def _load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _load_csv(path: Path) -> np.ndarray:
    return np.loadtxt(path, delimiter=",", skiprows=1)


def write_csv(path: str | Path, header: list[str], rows: list[list]) -> Path:
    """Write a small CSV result table and return its path."""
    out = Path(path)
    config.ensure_dir(out.parent)
    with open(out, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        writer.writerows(rows)
    return out


def manifest_path() -> Path:
    """Return the manifest path to write.

    ``HDDBOOK_MANIFEST`` overrides the repository manifest (used by the smoke
    tests so that a pytest run never rewrites ``figures/manifest.yaml``).
    """
    override = os.environ.get("HDDBOOK_MANIFEST")
    if override:
        return Path(override)
    return config.FIG_DIR / "manifest.yaml"


def repo_relative(path: str | Path) -> str:
    """Return ``path`` relative to the repository root when possible.

    Paths outside the repository (e.g. pytest ``tmp_path``) are returned as
    absolute strings instead of raising ``ValueError``.
    """
    p = Path(path)
    try:
        return str(p.resolve().relative_to(config.REPO_ROOT))
    except ValueError:
        return str(p)


def record_figure(
    figure_id: str,
    *,
    chapter: int,
    section: str,
    title: str,
    script: str,
    command: str,
    output: str | Path,
    source: str,
    license: str,
    status: str = "draft",
) -> None:
    """Insert or update one entry in ``figures/manifest.yaml``.

    The manifest is the single source of truth linking a book figure to the
    script that reproduces it; ``output_sha256`` is filled automatically.
    """
    manifest_file = manifest_path()
    config.ensure_dir(manifest_file.parent)
    entries = []
    if manifest_file.exists():
        with open(manifest_file, encoding="utf-8") as fh:
            entries = yaml.safe_load(fh) or []
    out = Path(output)
    entry = {
        "figure_id": figure_id,
        "chapter": chapter,
        "section": section,
        "title": title,
        "script": script,
        "command": command,
        "data": None,
        "output": repo_relative(out),
        "output_sha256": sha256(out) if out.exists() else None,
        "source": source,
        "license": license,
        "status": status,
    }
    entries = [e for e in entries if e.get("figure_id") != figure_id]
    entries.append(entry)
    entries.sort(key=lambda e: (e.get("chapter", 0), e.get("figure_id", "")))
    with open(manifest_file, "w", encoding="utf-8") as fh:
        yaml.safe_dump(entries, fh, allow_unicode=True, sort_keys=False)
