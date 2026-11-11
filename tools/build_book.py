#!/usr/bin/env python3
"""Build the book PDF from Markdown sources using the ElegantBook template.

Steps:
1. Convert existing Markdown chapters into LaTeX sections (tools/md2tex.py).
2. Generate book/sections/structure.tex.
3. Run latexmk (XeLaTeX + biber) on book/main.tex.

Usage:
    python tools/build_book.py            # build PDF into book/build/main.pdf
    python tools/build_book.py --clean    # remove build artifacts
    python tools/build_book.py --check    # convert + compile, keep logs

Requirements: pandoc, latexmk, xelatex, biber (TeX Live/MacTeX).
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK_DIR = ROOT / "book"
BUILD_DIR = BOOK_DIR / "build"


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess:
    print("$", " ".join(cmd), f"(cwd={cwd})")
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)


def clean() -> None:
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
        print(f"removed {BUILD_DIR}")
    for pattern in ("sections/*.tex", "sections/.tmp.md"):
        for path in BOOK_DIR.glob(pattern):
            if path.name != "structure.tex":
                path.unlink()
    print("removed generated sections")


def convert() -> bool:
    proc = run([sys.executable, str(ROOT / "tools" / "md2tex.py")], ROOT)
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr)
        return False
    print(proc.stdout)
    return True


def compile_pdf() -> tuple[bool, str]:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    cmd = [
        "latexmk",
        "-xelatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-file-line-error",
        "-outdir=build",
        "main.tex",
    ]
    proc = run(cmd, BOOK_DIR)
    log = BUILD_DIR / "main.log"
    if proc.returncode != 0:
        print(proc.stdout[-4000:])
        print(proc.stderr[-2000:])
        if log.exists():
            errors = [line for line in log.read_text(errors="ignore").splitlines() if line.startswith("!")]
            print("\n".join(errors[-20:]))
        return False, ""
    text = log.read_text(errors="ignore") if log.exists() else ""
    m = re.search(r"Output written on (?:build/)?main\.(?:pdf|xdv) \((\d+) pages", text)
    pages = m.group(1) if m else "?"
    pdf = BUILD_DIR / "main.pdf"
    if not pdf.exists():
        return False, ""
    print(f"PDF: {pdf} ({pages} pages)")
    return True, str(pdf)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clean", action="store_true", help="remove build artifacts and exit")
    parser.add_argument("--check", action="store_true", help="compile and keep logs")
    args = parser.parse_args()

    if args.clean:
        clean()
        return 0

    for tool in ("pandoc", "latexmk", "xelatex", "biber"):
        if not shutil.which(tool):
            print(f"ERROR missing tool: {tool}")
            return 2

    if not convert():
        return 1
    ok, _ = compile_pdf()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
