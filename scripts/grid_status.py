#!/usr/bin/env python3
"""Print status of a partition-variance grid by scanning results/."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.run_grid import classify_cell, enumerate_cells, load_grid  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Grid status table")
    parser.add_argument("--grid", required=True, help="Grid YAML path")
    args = parser.parse_args()
    grid_path = Path(args.grid)
    if not grid_path.is_absolute():
        grid_path = REPO_ROOT / grid_path
    grid = load_grid(grid_path)
    cells = enumerate_cells(grid)
    counts: Counter = Counter()
    rows = []
    for c in cells:
        st = classify_cell(c)
        counts[st] += 1
        rows.append((st, c.cell_id))
    print(f"Grid: {grid.get('name', grid_path.stem)}  expected={grid.get('expected_runs')}  enumerated={len(cells)}")
    known = ("complete", "needs_holdout", "resumable", "orphan", "fresh")
    print(
        f"complete={counts['complete']}  needs_holdout={counts['needs_holdout']}  "
        f"resumable={counts['resumable']}  orphan={counts['orphan']}  "
        f"fresh={counts['fresh']}  "
        f"other={sum(v for k, v in counts.items() if k not in known)}"
    )
    print("-" * 72)
    print(f"{'status':<14} cell_id")
    for st, cid in rows:
        print(f"{st:<14} {cid}")


if __name__ == "__main__":
    main()
