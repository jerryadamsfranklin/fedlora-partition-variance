#!/usr/bin/env python3
"""I0: build analysis/runs.csv from production holdout JSONs + run metadata."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.run_grid import enumerate_cells, load_grid  # noqa: E402
from scripts.verify_varpart import _complete_run_dirs, resolve_holdout  # noqa: E402

COLUMNS = [
    "model",
    "het",
    "method",
    "data_seed",
    "run_seed",
    "heldout_loss",
    "base_loss",
    "delta_loss",
    "final_train_loss",
    "comm_mb_total",
    "upload_mb_total",
    "active_clients",
    "run_dir",
    "gpu_name",
    "wall_clock_s",
]


def _final_train_loss(results: Any) -> Optional[float]:
    if not isinstance(results, list) or not results:
        return None
    last = results[-1]
    for key in ("avg_loss", "train_loss", "loss"):
        if key in last and last[key] is not None:
            return float(last[key])
    return None


def _comm_totals(results: Any) -> tuple[Optional[float], Optional[float]]:
    if not isinstance(results, list) or not results:
        return None, None
    last = results[-1]
    return (
        float(last["communication_mb"]) if "communication_mb" in last else None,
        float(last["upload_mb"]) if "upload_mb" in last else None,
    )


def build_rows(grid_paths: List[Path]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for gpath in grid_paths:
        grid = load_grid(gpath)
        for cell in enumerate_cells(grid):
            run_dir = _complete_run_dirs(cell)[0]
            holdout = json.loads(resolve_holdout(run_dir).read_text(encoding="utf-8"))
            row_h = holdout.get("row") or {}
            meta = json.loads((run_dir / "run_meta.json").read_text(encoding="utf-8"))
            pstats = json.loads(
                (run_dir / "partition_stats.json").read_text(encoding="utf-8")
            )
            results = json.loads((run_dir / "results.json").read_text(encoding="utf-8"))
            comm, upload = _comm_totals(results)
            heldout = float(row_h["tuned_loss"])
            base = float(row_h["base_loss"])
            rows.append(
                {
                    "model": cell.model,
                    "het": cell.het,
                    "method": cell.method,
                    "data_seed": cell.data_seed,
                    "run_seed": cell.run_seed,
                    "heldout_loss": heldout,
                    "base_loss": base,
                    "delta_loss": heldout - base,
                    "final_train_loss": _final_train_loss(results),
                    "comm_mb_total": comm,
                    "upload_mb_total": upload,
                    "active_clients": int(pstats["active_clients"]),
                    "run_dir": str(run_dir.relative_to(REPO_ROOT)),
                    "gpu_name": (meta.get("hardware") or {}).get("gpu_name"),
                    "wall_clock_s": meta.get("wall_clock_s"),
                }
            )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Build analysis/runs.csv (I0)")
    parser.add_argument(
        "--grids",
        nargs="+",
        default=["grids/tl.yaml", "grids/l3.yaml"],
    )
    parser.add_argument(
        "--out",
        default="analysis/runs.csv",
    )
    args = parser.parse_args()
    paths = [
        Path(g) if Path(g).is_absolute() else REPO_ROOT / g for g in args.grids
    ]
    rows = build_rows(paths)
    out = Path(args.out)
    if not out.is_absolute():
        out = REPO_ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {out} ({len(rows)} rows)")
    # null report
    for col in COLUMNS:
        n_null = sum(1 for r in rows if r[col] is None or r[col] == "")
        if n_null:
            print(f"  nulls in {col}: {n_null}")


if __name__ == "__main__":
    main()
