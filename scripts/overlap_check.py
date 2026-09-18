#!/usr/bin/env python3
"""Shared 8-gram overlap check against old OJ-CS tex files (read in place).

Never copies the reference files into this repo.
Exit 0 if shared 8-gram rate < 5% (excluding a references/bibliography section
when a \\begin{thebibliography} or \\bibliography marker is present).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def _resolve_inputs(tex: str, base: Path, depth: int = 0) -> str:
    if depth > 20:
        return tex

    def repl(m: re.Match[str]) -> str:
        rel = m.group(1)
        for cand in (base / f"{rel}.tex", base / rel, base / f"{rel}"):
            if cand.is_file():
                return _resolve_inputs(cand.read_text(encoding="utf-8"), cand.parent, depth + 1)
        return m.group(0)

    return re.sub(r"\\(?:input|include)\{([^}]+)\}", repl, tex)


def _strip_comments(tex: str) -> str:
    return re.sub(r"(?<!\\)%.*?$", "", tex, flags=re.M)


def _body_only(tex: str, base: Path | None = None) -> str:
    if base is not None:
        tex = _resolve_inputs(tex, base)
    tex = _strip_comments(tex)
    # Drop bibliography / references block if present
    for pat in (
        r"\\begin\{thebibliography\}.*",
        r"\\bibliography\{.*?\}.*",
        r"\\section\*\{References\}.*",
    ):
        tex = re.sub(pat, "", tex, flags=re.S | re.I)
    # Drop bib items style
    tex = re.sub(r"\\(cite|ref|label|includegraphics)\{[^}]*\}", " ", tex)
    tex = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{[^}]*\})?", " ", tex)
    tex = re.sub(r"[{}$\\]", " ", tex)
    tex = re.sub(r"[^A-Za-z0-9\s]", " ", tex)
    return re.sub(r"\s+", " ", tex).strip().lower()


def _ngrams(text: str, n: int = 8) -> set[tuple[str, ...]]:
    toks = text.split()
    if len(toks) < n:
        return set()
    return {tuple(toks[i : i + n]) for i in range(len(toks) - n + 1)}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--manuscript", required=True)
    p.add_argument("--reference", action="append", required=True)
    p.add_argument("--n", type=int, default=8)
    p.add_argument("--threshold", type=float, default=0.05)
    args = p.parse_args()

    ms = Path(args.manuscript)
    body = _body_only(ms.read_text(encoding="utf-8"), base=ms.parent)
    grams = _ngrams(body, args.n)
    if not grams:
        print("OVERLAP FAIL: manuscript too short for 8-grams")
        return 1

    print(f"manuscript tokens~{len(body.split())}, {args.n}-grams={len(grams)}")
    worst = 0.0
    for ref in args.reference:
        rp = Path(ref)
        if not rp.is_file():
            print(f"OVERLAP FAIL: missing reference {rp}")
            return 1
        rgrams = _ngrams(_body_only(rp.read_text(encoding="utf-8"), base=rp.parent), args.n)
        shared = grams & rgrams
        rate = len(shared) / len(grams)
        worst = max(worst, rate)
        print(
            f"vs {rp.name}: shared={len(shared)} rate={rate:.4%} "
            f"({'PASS' if rate < args.threshold else 'FAIL'} < {args.threshold:.0%})"
        )
        if shared and rate >= args.threshold:
            # show a few examples
            for g in list(shared)[:5]:
                print("  ex:", " ".join(g))

    if worst >= args.threshold:
        print(f"OVERLAP FAIL: max shared 8-gram rate {worst:.4%}")
        return 1
    print(f"OVERLAP OK: max shared 8-gram rate {worst:.4%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
