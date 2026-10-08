#!/usr/bin/env python3
"""Flag banned typography in manuscript .tex and .bib files.

Flags: U+2014 em dash, U+2013 en dash, curly quotes U+201C/U+201D/U+2018/U+2019,
LaTeX three-hyphen em dash (---) in .tex files (not --), sentences starting
with First, Furthermore, Moreover, or Additionally, and IEEE Access abstract
word count outside 150 to 250.
Exit 0 if clean; exit 1 if any flag.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

BANNED_CHARS = {
    "\u2014": "em dash",
    "\u2013": "en dash",
    "\u201c": "curly double quote open",
    "\u201d": "curly double quote close",
    "\u2018": "curly single quote open",
    "\u2019": "curly single quote close",
}
BANNED_START = re.compile(
    r"(?:^|\n)\s*(First,|Furthermore|Moreover|Additionally)\b"
)

ABSTRACT_RE = re.compile(
    r"\\begin\{abstract\}(.*?)\\end\{abstract\}",
    re.DOTALL | re.IGNORECASE,
)
# Strip LaTeX commands (optional args) and math delimiters before counting.
_LATEX_CMD = re.compile(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{[^{}]*\})?")
_MATH = re.compile(r"\$[^$]*\$")
_BRACES = re.compile(r"[{}]")


def _is_comment_line(line: str) -> bool:
    return line.lstrip().startswith("%")


def check_latex_em_dash(path: Path, line: str, line_no: int) -> list[str]:
    """Flag --- in .tex files; skip comments; do not flag --."""
    if path.suffix != ".tex":
        return []
    if _is_comment_line(line):
        return []
    if "---" in line:
        return [f"{path}:{line_no}: LaTeX em dash (---)"]
    return []


def abstract_plain_text(tex: str) -> str | None:
    """Return stripped abstract body text, or None if no abstract environment."""
    m = ABSTRACT_RE.search(tex)
    if not m:
        return None
    body = m.group(1)
    # Drop comment lines inside the environment.
    body = "\n".join(
        ln for ln in body.splitlines() if not _is_comment_line(ln)
    )
    body = _MATH.sub(" ", body)
    # Iterate command stripping for nested simple braces.
    prev = None
    while prev != body:
        prev = body
        body = _LATEX_CMD.sub(" ", body)
    body = _BRACES.sub(" ", body)
    body = re.sub(r"[\\~^]", " ", body)
    body = re.sub(r"\s+", " ", body).strip()
    return body


def abstract_word_count(tex: str) -> int | None:
    """Whitespace-delimited token count of the stripped abstract, or None."""
    plain = abstract_plain_text(tex)
    if plain is None or not plain:
        return None
    return len(plain.split())


def check_abstract_word_count(
    path: Path, tex: str, *, lo: int = 150, hi: int = 250
) -> list[str]:
    """FAIL if main.tex abstract is outside [lo, hi] words."""
    if path.name != "main.tex":
        return []
    n = abstract_word_count(tex)
    if n is None:
        return [f"{path}: abstract environment missing or empty"]
    if n < lo or n > hi:
        return [
            f"{path}: abstract word count {n} outside IEEE Access "
            f"{lo}–{hi} limit"
        ]
    return []


_LABEL_RE = re.compile(r"\\label\{((?:fig|tab):[^}]+)\}")
_REF_RE = re.compile(r"\\ref\{((?:fig|tab):[^}]+)\}")


def check_float_citations(tex_files: list[Path]) -> list[str]:
    """Every fig:/tab: label must be \\ref'd; first refs in float-number order."""
    labels: list[tuple[str, Path]] = []
    refs: list[str] = []
    for path in tex_files:
        text = path.read_text(encoding="utf-8")
        # Strip comments
        body = "\n".join(
            ln for ln in text.splitlines() if not _is_comment_line(ln)
        )
        for m in _LABEL_RE.finditer(body):
            labels.append((m.group(1), path))
        for m in _REF_RE.finditer(body):
            refs.append(m.group(1))
    hits: list[str] = []
    ref_set = set(refs)
    for lab, path in labels:
        if lab not in ref_set:
            hits.append(f"{path}: label {lab} has no \\ref in the manuscript")
    # First-reference order must match label order for each family.
    for prefix in ("fig:", "tab:"):
        lab_order = [lab for lab, _ in labels if lab.startswith(prefix)]
        first_refs: list[str] = []
        seen: set[str] = set()
        for r in refs:
            if r.startswith(prefix) and r not in seen:
                seen.add(r)
                first_refs.append(r)
        # Only compare labels that are referenced (unref caught above).
        lab_order = [lab for lab in lab_order if lab in ref_set]
        if first_refs[: len(lab_order)] != lab_order:
            hits.append(
                f"manuscript: first {prefix} references {first_refs} "
                f"do not follow label order {lab_order}"
            )
    return hits


def check_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    hits: list[str] = []
    for i, line in enumerate(text.splitlines(), 1):
        for ch, name in BANNED_CHARS.items():
            if ch in line:
                hits.append(f"{path}:{i}: {name}")
        hits.extend(check_latex_em_dash(path, line, i))
    if BANNED_START.search(text):
        for m in BANNED_START.finditer(text):
            # approximate line
            line_no = text[: m.start()].count("\n") + 1
            hits.append(f"{path}:{line_no}: banned sentence start {m.group(1)!r}")
    hits.extend(check_abstract_word_count(path, text))
    return hits


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "manuscript")
    files = sorted(root.rglob("*.tex")) + sorted(root.rglob("*.bib"))
    if not files:
        print(f"no .tex/.bib under {root}")
        return 1
    all_hits: list[str] = []
    for f in files:
        all_hits.extend(check_file(f))
    tex_only = [f for f in files if f.suffix == ".tex"]
    all_hits.extend(check_float_citations(tex_only))
    if all_hits:
        print("TYPOGRAPHY FAIL:")
        for h in all_hits:
            print(f"  {h}")
        return 1
    print(f"TYPOGRAPHY OK: {len(files)} files clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
