#!/usr/bin/env python3
"""Flag banned typography in manuscript .tex and .bib files.

Flags: U+2014 em dash, U+2013 en dash, curly quotes U+201C/U+201D/U+2018/U+2019,
and sentences starting with First, Furthermore, Moreover, or Additionally.
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


def check_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    hits: list[str] = []
    for i, line in enumerate(text.splitlines(), 1):
        for ch, name in BANNED_CHARS.items():
            if ch in line:
                hits.append(f"{path}:{i}: {name}")
        # LaTeX -- is intentional for en-dash in print; only flag Unicode en/em
    if BANNED_START.search(text):
        for m in BANNED_START.finditer(text):
            # approximate line
            line_no = text[: m.start()].count("\n") + 1
            hits.append(f"{path}:{line_no}: banned sentence start {m.group(1)!r}")
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
    if all_hits:
        print("TYPOGRAPHY FAIL:")
        for h in all_hits:
            print(f"  {h}")
        return 1
    print(f"TYPOGRAPHY OK: {len(files)} files clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
