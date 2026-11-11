#!/usr/bin/env python3
"""Convert book Markdown chapters into LaTeX sections for ElegantBook.

Pipeline (single source of truth: docs/chapters/*.md):

    Markdown -> preprocess (strip numbering, expand cross-refs)
             -> pandoc (LaTeX body, biblatex citations)
             -> wrap in refsegment + per-chapter bibliography
             -> book/sections/*.tex

The generated .tex files must not be edited by hand; edit the Markdown source.

Usage:
    python tools/md2tex.py --book-yaml book/book.yaml --out-dir book
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
FRONTMATTER_RE = re.compile(r"^---\n.*?\n---\n", re.S)
CHAPTER_HEAD_RE = re.compile(r"^#\s+第\s*(\d+)\s*章\s+(.*)$")
APPENDIX_HEAD_RE = re.compile(r"^#\s+附录\s*([A-Z])\s+(.*)$")
NUM_HEAD_RE = re.compile(r"^(#{2,6})\s+\d+(?:\.\d+)*\s+(.*)$")
PLACEHOLDER_RE = re.compile(r"\{\{(fig|tab|eq|sec|ch|exp|code):([^}]+)\}\}")


def strip_frontmatter(text: str) -> str:
    return FRONTMATTER_RE.sub("", text, count=1)


def preprocess(text: str) -> tuple[str, int | None]:
    """Strip chapter/section numbering (LaTeX auto-numbers) and expand refs."""
    lines = text.splitlines()
    chapter_no: int | None = None
    out: list[str] = []
    for line in lines:
        m = CHAPTER_HEAD_RE.match(line)
        if m and chapter_no is None:
            chapter_no = int(m.group(1))
            line = f"# {m.group(2).strip()}"
        else:
            ma = APPENDIX_HEAD_RE.match(line)
            if ma:
                line = f"# {ma.group(2).strip()}"
            else:
                m2 = NUM_HEAD_RE.match(line)
                if m2:
                    line = f"{m2.group(1)} {m2.group(2)}"
        out.append(line)
    body = "\n".join(out)

    def repl(match: re.Match[str]) -> str:
        kind, ident = match.group(1), match.group(2)
        if kind == "fig":
            return rf"\ref{{fig:{ident}}}"
        if kind == "tab":
            return rf"\ref{{tab:{ident}}}"
        if kind == "eq":
            return rf"\eqref{{eq:{ident}}}"
        if kind == "sec":
            return rf"\ref{{sec:{ident}}}"
        if kind == "ch":
            return rf"\ref{{ch:{ident}}}"
        if kind == "exp":
            return f"实验~{ident}"
        if kind == "code":
            return f"`{ident}`"
        return match.group(0)

    return PLACEHOLDER_RE.sub(repl, body), chapter_no


def pandoc_to_latex(markdown: str, source: Path) -> str:
    pandoc = subprocess.run(
        [
            "pandoc",
            str(source),
            "--from",
            "markdown+pipe_tables+tex_math_dollars+raw_tex",
            "--to",
            "latex",
            "--top-level-division=chapter",
            "--biblatex",
            "--wrap=preserve",
            "--resource-path",
            str(ROOT),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if pandoc.returncode != 0:
        raise RuntimeError(f"pandoc failed for {source}:\n{pandoc.stderr}")
    return pandoc.stdout


def add_starred_toc(body: str) -> str:
    """Add unnumbered sections (导读/小结/习题) to the table of contents."""
    for level in ("section", "subsection"):
        body = re.sub(
            rf"\\{level}\*\{{\{{([^{{}}]*)\}}\}}",
            lambda m, lv=level: rf"\\{lv}*{{{m.group(1)}}}\addcontentsline{{toc}}{{{lv}}}{{{m.group(1)}}}",
            body,
        )
    return body


def wrap_chapter(tex: str, chapter_no: int | None, chapter_id: str) -> str:
    body = tex.strip()
    # Remove pandoc's auto-generated Unicode labels; we add stable labels below.
    body = re.sub(r"\\label\{ux[0-9a-f]+\}\n?", "", body)
    body = add_starred_toc(body)
    if chapter_no is not None:
        body = re.sub(
            r"(\\chapter\{[^\n]*\})",
            rf"\1\n\\label{{ch:{chapter_no}}}",
            body,
            count=1,
        )
        prefix = f"\\setcounter{{chapter}}{{{chapter_no - 1}}}\n"
    else:
        # Front matter: unnumbered chapter, but keep it in the table of contents.
        body = re.sub(
            r"\\chapter\{([^\n]*)\}",
            r"\\chapter*{\1}\n\\addcontentsline{toc}{chapter}{\1}",
            body,
            count=1,
        )
        prefix = ""
    # Per-chapter bibliography only when the chapter actually cites something.
    bib = ""
    if re.search(r"\\(?:auto)?cite\b", body):
        bib = "\\printbibliography[segment=\\therefsegment,heading=subbibliography,title={参考文献}]\n"
    wrapped = "\\begin{refsegment}\n" f"{prefix}{body}\n" f"{bib}" "\\end{refsegment}\n"
    return wrapped


def convert_entry(entry: dict, out_dir: Path) -> tuple[bool, str]:
    src = ROOT / entry["file"]
    tex_rel = entry["tex"]
    if not src.exists():
        return False, f"missing: {entry['file']}"
    text = strip_frontmatter(src.read_text(encoding="utf-8"))
    processed, chapter_no = preprocess(text)
    # pandoc needs a file; write a temporary preprocessed copy
    tmp = out_dir / ".tmp.md"
    tmp.write_text(processed, encoding="utf-8")
    try:
        tex = pandoc_to_latex(processed, tmp)
    finally:
        tmp.unlink(missing_ok=True)
    chapter_id = entry.get("id", src.stem)
    wrapped = wrap_chapter(tex, chapter_no, chapter_id)
    target = out_dir / tex_rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(wrapped, encoding="utf-8")
    return True, str(target.relative_to(ROOT))


def build_structure(book: dict, out_dir: Path) -> list[str]:
    lines: list[str] = []
    missing: list[str] = []
    for entry in book.get("front") or []:
        ok, info = convert_entry(entry, out_dir)
        if ok:
            lines.append(f"\\input{{{entry['tex']}}}")
        else:
            missing.append(info)
    for part_idx, part in enumerate(book.get("parts") or []):
        converted = []
        for entry in part.get("chapters") or []:
            ok, info = convert_entry(entry, out_dir)
            if ok:
                converted.append(entry)
            else:
                missing.append(info)
        if converted:
            lines.append(f"\\setcounter{{part}}{{{part_idx}}}")
            lines.append(f"\\part{{{part['title']}}}")
            lines.extend(f"\\input{{{e['tex']}}}" for e in converted)
    appendices = []
    for entry in book.get("appendices") or []:
        ok, info = convert_entry(entry, out_dir)
        if ok:
            appendices.append(entry)
        else:
            missing.append(info)
    if appendices:
        lines.append("\\appendix")
        lines.extend(f"\\input{{{e['tex']}}}" for e in appendices)
    (out_dir / "sections" / "structure.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--book-yaml", default=str(ROOT / "book" / "book.yaml"))
    parser.add_argument("--out-dir", default=str(ROOT / "book"))
    args = parser.parse_args()

    book_path = Path(args.book_yaml)
    book = yaml.safe_load(book_path.read_text(encoding="utf-8"))
    out_dir = Path(args.out_dir)
    (out_dir / "sections").mkdir(parents=True, exist_ok=True)

    missing = build_structure(book, out_dir)
    for item in missing:
        print(f"SKIP  {item}")
    print(f"generated sections in {out_dir / 'sections'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
