#!/usr/bin/env python3
"""Layout gates G1--G3 for the IEEE Access manuscript PDF/log/tables."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MANUSCRIPT = REPO / "manuscript"
TABLES = MANUSCRIPT / "tables"


def overfull_hbox_pts(log_text: str) -> list[tuple[float, str]]:
    """Return (pt, line) for every Overfull \\hbox larger than 0."""
    hits: list[tuple[float, str]] = []
    for line in log_text.splitlines():
        m = re.search(r"Overfull \\hbox \(([0-9.]+)pt too wide\)", line)
        if m:
            hits.append((float(m.group(1)), line.strip()))
    return hits


def content_overfull_hbox(
    log_text: str, *, max_pt: float = 1.0
) -> list[tuple[float, str, str]]:
    """Content Overfull \\hbox events that signal real manuscript overflow.

    Ignores ieeeaccess float-page chrome (``while \\output is active``) and
    tracks the current ``(./sections/...)`` / ``(./tables/...)`` input file so
    title-page class noise is not counted. Any overfull above 20pt is kept
    regardless of file context (catches clipped figure* captions).
    """
    hits: list[tuple[float, str, str]] = []
    current = ""
    for line in log_text.splitlines():
        # pdfTeX opens inputs as (./path or (/abs/path
        m_open = re.match(r"\(\./([^()\s]+)", line)
        if m_open:
            current = m_open.group(1)
        m = re.search(r"Overfull \\hbox \(([0-9.]+)pt too wide\)", line)
        if not m:
            continue
        pt = float(m.group(1))
        if pt <= max_pt:
            continue
        if "while \\output is active" in line:
            continue
        in_body = current.startswith("sections/") or current.startswith("tables/")
        if in_body or pt > 20.0:
            hits.append((pt, current, line.strip()))
    return hits


def check_g1_overfull(log_path: Path, *, max_pt: float = 1.0) -> list[str]:
    """G1: no content Overfull \\hbox larger than max_pt."""
    text = log_path.read_text(encoding="utf-8", errors="replace")
    bad = content_overfull_hbox(text, max_pt=max_pt)
    return [
        f"G1: Overfull hbox {pt:.3f}pt > {max_pt} in {ctx or '?'}: {line}"
        for pt, ctx, line in bad
    ]

def _caption_bodies_from_tex(tex_files: list[Path]) -> list[str]:
    """Extract caption bodies (rough LaTeX strip) from \\caption{...}."""
    bodies: list[str] = []
    for path in tex_files:
        text = path.read_text(encoding="utf-8")
        # Non-greedy; captions in this repo are single-line or short multi-line.
        for m in re.finditer(r"\\caption\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}", text):
            raw = m.group(1)
            # Drop math and commands for PDF text match.
            plain = re.sub(r"\$[^$]*\$", " ", raw)
            plain = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{[^{}]*\})?", " ", plain)
            plain = re.sub(r"[{}]", " ", plain)
            plain = re.sub(r"\s+", " ", plain).strip()
            if plain:
                bodies.append(plain)
    return bodies


def check_g2_captions_in_pdf(pdf_path: Path, tex_files: list[Path]) -> list[str]:
    """G2: every caption's distinctive words appear in pdftotext output."""
    pdf_text = subprocess.check_output(
        ["pdftotext", str(pdf_path), "-"], text=True, errors="replace"
    )
    # Normalize whitespace / hyphenation soft breaks.
    norm = re.sub(r"\s+", " ", pdf_text)
    hits: list[str] = []
    for body in _caption_bodies_from_tex(tex_files):
        # Require a long distinctive substring (first 40 chars of words).
        words = body.split()
        needle = " ".join(words[:8]) if len(words) >= 8 else body
        if needle and needle not in norm:
            # Also try without punctuation differences
            soft = re.sub(r"[^\w\s]", "", needle)
            soft_pdf = re.sub(r"[^\w\s]", "", norm)
            if soft not in soft_pdf:
                hits.append(f"G2: caption text missing from PDF: {needle!r}")
    return hits


def count_table_data_rows(tex: str) -> int:
    body = False
    n = 0
    for line in tex.splitlines():
        if r"\midrule" in line:
            body = True
            continue
        if r"\bottomrule" in line:
            break
        if body and line.rstrip().endswith(r"\\"):
            n += 1
    return n


def check_g3_table_rows() -> list[str]:
    """G3: Table 3 has 9 data rows; Table 2 has 4."""
    hits: list[str] = []
    t2 = count_table_data_rows((TABLES / "tab2_variance.tex").read_text(encoding="utf-8"))
    t3 = count_table_data_rows((TABLES / "tab3_means_comm.tex").read_text(encoding="utf-8"))
    if t2 != 4:
        hits.append(f"G3: Table 2 has {t2} data rows (expected 4)")
    if t3 != 9:
        hits.append(f"G3: Table 3 has {t3} data rows (expected 9)")
    return hits


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--log",
        type=Path,
        default=MANUSCRIPT / "main.log",
        help="latexmk/pdflatex log",
    )
    ap.add_argument(
        "--pdf",
        type=Path,
        default=MANUSCRIPT / "main.pdf",
        help="compiled manuscript PDF",
    )
    args = ap.parse_args()
    tex_files = sorted((MANUSCRIPT / "sections").glob("*.tex")) + [MANUSCRIPT / "main.tex"]
    hits: list[str] = []
    if args.log.is_file():
        hits.extend(check_g1_overfull(args.log))
    else:
        hits.append(f"G1: missing log {args.log}")
    if args.pdf.is_file():
        hits.extend(check_g2_captions_in_pdf(args.pdf, tex_files))
    else:
        hits.append(f"G2: missing PDF {args.pdf}")
    hits.extend(check_g3_table_rows())
    if hits:
        for h in hits:
            print(h, file=sys.stderr)
        print(f"LAYOUT FAIL: {len(hits)} issue(s)", file=sys.stderr)
        return 1
    print("LAYOUT OK: G1 G2 G3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
