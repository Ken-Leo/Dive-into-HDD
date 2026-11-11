#!/usr/bin/env python3
"""Consistency checks for the Dive-into-HDD book repository.

Checks:
1. Relative markdown links in README.md and docs/README.md resolve.
2. figures/manifest.yaml entries reference existing scripts/outputs and have
   source/licence fields; SHA256 mismatches are reported as warnings.
3. No hard-coded absolute paths (/Volumes/..., ~/...) in chapter files and
   experiment scripts.
4. docs/plan/asset-registry.csv has the required columns and non-empty rows.

Usage: python tools/check_docs.py [--strict]
Exit code 1 on errors (warnings do not fail unless --strict).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
ABS_RE = re.compile(r"(/Volumes/|~/)")


def check_links() -> list[str]:
    errors: list[str] = []
    for md in (ROOT / "README.md", ROOT / "docs" / "README.md"):
        text = md.read_text(encoding="utf-8")
        for target in LINK_RE.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path = (md.parent / target.split("#")[0]).resolve()
            if not path.exists():
                errors.append(f"{md.relative_to(ROOT)}: broken link -> {target}")
    return errors


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_manifest() -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    manifest = ROOT / "figures" / "manifest.yaml"
    if not manifest.exists():
        warnings.append("figures/manifest.yaml not found")
        return errors, warnings
    entries = yaml.safe_load(manifest.read_text(encoding="utf-8")) or []
    for entry in entries:
        fid = entry.get("figure_id", "<missing>")
        script = entry.get("script")
        output = entry.get("output")
        if not script or not (ROOT / script).exists():
            errors.append(f"manifest {fid}: script missing -> {script}")
        if not output or not (ROOT / output).exists():
            errors.append(f"manifest {fid}: output missing -> {output}")
        elif entry.get("output_sha256") and sha256(ROOT / output) != entry["output_sha256"]:
            warnings.append(f"manifest {fid}: SHA256 mismatch (figure changed?)")
        for field in ("source", "license"):
            if not entry.get(field):
                errors.append(f"manifest {fid}: missing {field}")
    return errors, warnings


def check_absolute_paths() -> list[str]:
    errors: list[str] = []
    targets = list((ROOT / "docs" / "chapters").glob("*.md")) + list((ROOT / "code" / "experiments").glob("*.py"))
    for path in targets:
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if ABS_RE.search(line) and "sys.path" not in line:
                errors.append(f"{path.relative_to(ROOT)}:{i}: absolute path -> {line.strip()}")
    return errors


def check_registry() -> list[str]:
    errors: list[str] = []
    registry = ROOT / "docs" / "plan" / "asset-registry.csv"
    if not registry.exists():
        return ["docs/plan/asset-registry.csv missing"]
    required = {"asset_id", "type", "path", "license", "chapters", "usage", "status", "risk"}
    with open(registry, encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if not required.issubset(reader.fieldnames or []):
            errors.append(f"asset-registry.csv: missing columns {required - set(reader.fieldnames or [])}")
        for i, row in enumerate(reader, 2):
            for col in ("asset_id", "type", "path"):
                if not row.get(col):
                    errors.append(f"asset-registry.csv:{i}: empty {col}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    errors += check_links()
    e, w = check_manifest()
    errors += e
    warnings += w
    errors += check_absolute_paths()
    errors += check_registry()

    for msg in warnings:
        print(f"WARN  {msg}")
    for msg in errors:
        print(f"ERROR {msg}")
    print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)")
    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
