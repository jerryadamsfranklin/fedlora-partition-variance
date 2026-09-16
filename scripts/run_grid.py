#!/usr/bin/env python3
"""Enumerate and run partition-variance grid cells (training + holdout)."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

HET_ORDER = {"iid": 0, "a01": 1}
RESULTS_RAW_MARKER = "results/raw/"


@dataclass(frozen=True)
class Cell:
    het: str
    data_seed: int
    run_seed: int
    method: str
    config: str
    model: str  # tl | l3
    tag: str

    @property
    def cell_id(self) -> str:
        return f"{self.model}_{self.method}_{self.het}_d{self.data_seed}_r{self.run_seed}"

    @property
    def exp_name(self) -> str:
        return f"vp_{self.model}_{self.method}_{self.het}"

    @property
    def seed_dir(self) -> str:
        return f"seed_{self.data_seed}_run{self.run_seed}"

    def run_glob(self) -> Path:
        return (
            REPO_ROOT
            / "results"
            / "raw"
            / self.exp_name
            / self.method
            / self.seed_dir
            / self.tag
        )


def load_grid(path: str | Path) -> Dict[str, Any]:
    with open(path) as f:
        return yaml.safe_load(f)


def model_from_pattern(config_pattern: str) -> str:
    # config/vp/vp_tl_{method}_{het}.yaml
    m = re.search(r"vp_([a-z0-9]+)_\{method\}", config_pattern)
    if not m:
        raise ValueError(f"Cannot infer model key from config_pattern={config_pattern!r}")
    return m.group(1)


def enumerate_cells(grid: Dict[str, Any]) -> List[Cell]:
    methods: Sequence[str] = list(grid["methods"])
    pattern: str = grid["config_pattern"]
    tag: str = grid["tag"]
    model = model_from_pattern(pattern)
    cells: List[Cell] = []
    for block in grid["cells"]:
        het = block["het"]
        for data_seed in block["data_seeds"]:
            for run_seed in block["run_seeds"]:
                for method in methods:
                    cfg = pattern.format(method=method, het=het)
                    cells.append(
                        Cell(
                            het=het,
                            data_seed=int(data_seed),
                            run_seed=int(run_seed),
                            method=method,
                            config=cfg,
                            model=model,
                            tag=tag,
                        )
                    )
    cells.sort(
        key=lambda c: (
            HET_ORDER.get(c.het, 99),
            c.data_seed,
            c.run_seed,
            methods.index(c.method) if c.method in methods else 99,
        )
    )
    return cells


def group_key(cell: Cell) -> Tuple[str, int, int]:
    """Partition/run identity shared by all methods in a group."""
    return (cell.het, cell.data_seed, cell.run_seed)


def ordered_groups(cells: Sequence[Cell]) -> List[Tuple[str, int, int]]:
    """Unique (het, data_seed, run_seed) groups in cell enumeration order."""
    groups: List[Tuple[str, int, int]] = []
    seen: set[Tuple[str, int, int]] = set()
    for cell in cells:
        key = group_key(cell)
        if key not in seen:
            seen.add(key)
            groups.append(key)
    return groups


def shard_cells(cells: Sequence[Cell], shard: int, num_shards: int) -> List[Cell]:
    if num_shards < 1:
        raise ValueError("num_shards must be >= 1")
    if shard < 0 or shard >= num_shards:
        raise ValueError(f"shard must be in [0, {num_shards})")
    group_shard = {
        key: idx % num_shards for idx, key in enumerate(ordered_groups(cells))
    }
    return [c for c in cells if group_shard[group_key(c)] == shard]


def _results_key(path: str | Path) -> str:
    """Normalize absolute or relative run paths for comparison."""
    s = str(path).replace("\\", "/")
    idx = s.find(RESULTS_RAW_MARKER)
    if idx < 0:
        raise ValueError(f"path missing {RESULTS_RAW_MARKER!r}: {path!r}")
    return s[idx:]


def _resolve_run_dir(run_dir: Path) -> Path:
    if run_dir.is_absolute():
        return run_dir.resolve()
    return (REPO_ROOT / run_dir).resolve()


def production_guard(
    grid: Dict[str, Any],
    *,
    git_points_at=None,
    git_status_tracked=None,
    env: Optional[Dict[str, str]] = None,
) -> None:
    """Refuse production launch unless freeze-v1, clean tracked tree, HF_TOKEN set."""
    env = env if env is not None else os.environ

    if grid.get("overrides"):
        raise SystemExit(
            "ERROR: --production requires a grid with no overrides "
            f"(found {grid.get('overrides')!r})"
        )

    def _run(cmd: List[str]) -> str:
        return subprocess.check_output(cmd, text=True, cwd=str(REPO_ROOT)).strip()

    if git_points_at is None:
        try:
            tags = [t for t in _run(["git", "tag", "--points-at", "HEAD"]).splitlines() if t]
        except subprocess.CalledProcessError as e:
            raise SystemExit(
                "ERROR: --production requires HEAD tagged freeze-v1 "
                f"(git tag --points-at HEAD failed: {e})"
            ) from e
    else:
        tags = git_points_at()

    if "freeze-v1" not in tags:
        raise SystemExit(
            f"ERROR: --production requires freeze-v1 in git tag --points-at HEAD; got {tags!r}"
        )

    if git_status_tracked is None:
        dirty = _run(["git", "status", "--porcelain", "--untracked-files=no"])
    else:
        dirty = git_status_tracked()
    if dirty:
        raise SystemExit(
            "ERROR: --production requires a clean tracked tree "
            "(git status --porcelain --untracked-files=no must be empty)"
        )

    if not env.get("HF_TOKEN"):
        raise SystemExit("ERROR: --production requires HF_TOKEN to be set")


def _timestamp_dirs(cell: Cell) -> List[Path]:
    base = cell.run_glob()
    if not base.is_dir():
        return []
    return sorted([p for p in base.iterdir() if p.is_dir()])


def _has_complete_results_json(run_dir: Path, expected_rounds: int = 15) -> bool:
    path = run_dir / "results.json"
    if not path.is_file():
        return False
    try:
        with open(path) as f:
            data = json.load(f)
    except Exception:
        return False
    if isinstance(data, list):
        return len(data) == expected_rounds
    if isinstance(data, dict):
        rounds = data.get("rounds") or data.get("history") or data.get("results")
        if isinstance(rounds, list):
            return len(rounds) == expected_rounds
    return False


def _checkpoint_matches_holdout(run_dir: Path, checkpoint_value: str) -> bool:
    if not checkpoint_value:
        return False
    try:
        return _results_key(checkpoint_value) == _results_key(
            run_dir / "final_adapter_state.pt"
        )
    except ValueError:
        return False


def _has_holdout(run_dir: Path) -> bool:
    holdout_local = list(run_dir.rglob("instruction_holdout.json"))
    if holdout_local:
        return True
    downstream = REPO_ROOT / "results" / "downstream_instruction"
    if not downstream.is_dir():
        return False
    for p in downstream.rglob("instruction_holdout.json"):
        try:
            payload = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        row = payload.get("row") or {}
        meta = payload.get("meta") or {}
        if _checkpoint_matches_holdout(
            run_dir, str(row.get("checkpoint", ""))
        ) or _checkpoint_matches_holdout(
            run_dir, str(meta.get("checkpoint", ""))
        ):
            return True
    return False


def classify_cell(cell: Cell, expected_rounds: int = 15) -> str:
    """Return complete | needs_holdout | resumable | orphan | fresh."""
    dirs = _timestamp_dirs(cell)
    for d in reversed(dirs):
        has_meta = (d / "run_meta.json").is_file()
        has_pstats = (d / "partition_stats.json").is_file()
        has_results = _has_complete_results_json(d, expected_rounds)
        if has_results and has_meta and has_pstats:
            if _has_holdout(d):
                return "complete"
            return "needs_holdout"
        if (d / "checkpoints" / "latest.pt").is_file() and not has_results:
            return "resumable"
    # Orphan: timestamp dir with partition_stats (or other partial artifacts) but
    # no complete results.json and no resumable checkpoint.
    for d in reversed(dirs):
        has_pstats = (d / "partition_stats.json").is_file()
        has_results = _has_complete_results_json(d, expected_rounds)
        has_ckpt = (d / "checkpoints" / "latest.pt").is_file()
        if has_pstats and not has_results and not has_ckpt:
            return "orphan"
    return "fresh"


def find_run_dir(
    cell: Cell, prefer: str, expected_rounds: int = 15
) -> Optional[Path]:
    dirs = _timestamp_dirs(cell)
    for d in reversed(dirs):
        has_meta = (d / "run_meta.json").is_file()
        has_pstats = (d / "partition_stats.json").is_file()
        has_results = _has_complete_results_json(d, expected_rounds)
        if prefer == "needs_holdout" and has_results and has_meta and has_pstats:
            return d
        if prefer == "resumable" and (d / "checkpoints" / "latest.pt").is_file():
            return d
    return dirs[-1] if dirs else None


def _gpu_name() -> str:
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            text=True,
        ).strip()
        return out.splitlines()[0] if out else ""
    except Exception:
        return ""


def train_cmd(
    cell: Cell,
    device: str,
    resume: Optional[Path] = None,
    overrides: Optional[Sequence[str]] = None,
) -> List[str]:
    cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "run_experiment.py"),
        "--config",
        str(REPO_ROOT / cell.config),
        "--data-seed",
        str(cell.data_seed),
        "--run-seed",
        str(cell.run_seed),
        "--tag",
        cell.tag,
        "--device",
        device,
        "--save-every",
        "5",
    ]
    for override in overrides or ():
        cmd.extend(["--override", override])
    if resume is not None:
        cmd.extend(["--resume", str(resume)])
    return cmd


def holdout_cmd(
    cell: Cell,
    run_dir: Path,
    device: str,
    grid_name: str,
    shard: int,
    *,
    workers: int = 1,
) -> List[str]:
    if workers > 1:
        csv_name = f"holdout_{grid_name}_shard{shard}_{cell.cell_id}.csv"
    else:
        csv_name = f"holdout_{grid_name}_shard{shard}.csv"
    return [
        sys.executable,
        str(REPO_ROOT / "scripts" / "evaluate_instruction_holdout.py"),
        "--checkpoint",
        str(run_dir / "final_adapter_state.pt"),
        "--device",
        device,
        "--start-index",
        "3000",
        "--num-examples",
        "500",
        "--max-seq-length",
        "256",
        "--summary-csv",
        str(REPO_ROOT / "analysis" / csv_name),
        "--skip-existing",
    ]


def _parse_output_dir(stdout: str) -> Optional[Path]:
    for line in stdout.splitlines():
        if line.startswith("Output: ") or line.startswith("Results: "):
            return Path(line.split(":", 1)[1].strip())
    return None


def run_one_cell(
    cell: Cell,
    *,
    device: str,
    grid_name: str,
    shard: int,
    max_retries: int,
    holdout_only: bool,
    dry_run: bool,
    log_dir: Path,
    jsonl_path: Path,
    expected_rounds: int = 15,
    overrides: Optional[Sequence[str]] = None,
    workers: int = 1,
) -> str:
    status0 = classify_cell(cell, expected_rounds)
    if status0 == "complete":
        _append_jsonl(
            jsonl_path,
            {
                "cell_id": cell.cell_id,
                "attempt": 0,
                "status": "complete",
                "start": None,
                "end": None,
                "duration_s": 0,
                "train_exit": 0,
                "holdout_exit": 0,
                "run_dir": None,
                "gpu_name": _gpu_name(),
            },
        )
        return "complete"

    if dry_run:
        print(f"[dry-run] {cell.cell_id} status={status0}")
        return status0

    log_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)

    attempts = max_retries + 1
    last_status = status0
    for attempt in range(1, attempts + 1):
        start = datetime.now(timezone.utc).isoformat()
        t0 = time.perf_counter()
        train_exit = None
        holdout_exit = None
        run_dir: Optional[Path] = None
        cur = classify_cell(cell, expected_rounds)

        try:
            if cur == "complete":
                _append_jsonl(
                    jsonl_path,
                    {
                        "cell_id": cell.cell_id,
                        "attempt": attempt,
                        "status": "complete",
                        "start": start,
                        "end": datetime.now(timezone.utc).isoformat(),
                        "duration_s": round(time.perf_counter() - t0, 3),
                        "train_exit": 0,
                        "holdout_exit": 0,
                        "run_dir": None,
                        "gpu_name": _gpu_name(),
                        "note": "already complete before attempt",
                    },
                )
                return "complete"

            if holdout_only or cur == "needs_holdout":
                run_dir = find_run_dir(cell, "needs_holdout", expected_rounds)
                if run_dir is None:
                    raise RuntimeError("needs_holdout but no complete training dir found")
            elif cur in ("fresh", "orphan", "resumable"):
                resume = None
                if cur == "resumable":
                    resume = find_run_dir(cell, "resumable", expected_rounds)
                cmd = train_cmd(cell, device, resume=resume, overrides=overrides)
                train_exit, out, err = _run_logged(cmd, log_dir / f"{cell.cell_id}.log")
                parsed = _parse_output_dir(out)
                run_dir = _resolve_run_dir(parsed) if parsed is not None else None
                if run_dir is None:
                    run_dir = find_run_dir(cell, "needs_holdout", expected_rounds)
                if train_exit != 0:
                    raise RuntimeError(f"train failed exit={train_exit}")
                if run_dir is None:
                    dirs = _timestamp_dirs(cell)
                    run_dir = dirs[-1] if dirs else None
                if run_dir is None:
                    raise RuntimeError("training finished but run_dir not found")
                run_dir = _resolve_run_dir(run_dir)
            else:
                raise RuntimeError(f"unexpected cell status {cur!r}")

            assert run_dir is not None
            run_dir = _resolve_run_dir(run_dir)
            hcmd = holdout_cmd(
                cell, run_dir, device, grid_name, shard, workers=workers
            )
            holdout_exit, hout, herr = _run_logged(
                hcmd, log_dir / f"{cell.cell_id}.log", append=True
            )
            if holdout_exit != 0:
                raise RuntimeError(f"holdout failed exit={holdout_exit}")

            # Assert Dolly dataset in holdout JSON
            holdouts = list(Path(run_dir).rglob("instruction_holdout.json"))
            downstream = REPO_ROOT / "results" / "downstream_instruction"
            if downstream.is_dir():
                holdouts.extend(downstream.rglob("instruction_holdout.json"))
            ok = False
            for hp in holdouts:
                try:
                    payload = json.loads(hp.read_text(encoding="utf-8"))
                except Exception:
                    continue
                row = payload.get("row") or {}
                meta = payload.get("meta") or {}
                ckpt_val = str(row.get("checkpoint", "")) or str(
                    meta.get("checkpoint", "")
                )
                if not _checkpoint_matches_holdout(run_dir, ckpt_val):
                    continue
                ds = row.get("dataset") or meta.get("dataset")
                if ds != "databricks/databricks-dolly-15k":
                    raise RuntimeError(
                        f"holdout dataset mismatch: expected Dolly, got {ds!r}"
                    )
                ok = True
                break
            if not ok:
                raise RuntimeError("holdout JSON for this checkpoint not found after eval")

            last_status = "complete"
            _append_jsonl(
                jsonl_path,
                {
                    "cell_id": cell.cell_id,
                    "attempt": attempt,
                    "status": "complete",
                    "start": start,
                    "end": datetime.now(timezone.utc).isoformat(),
                    "duration_s": round(time.perf_counter() - t0, 3),
                    "train_exit": train_exit if train_exit is not None else 0,
                    "holdout_exit": holdout_exit,
                    "run_dir": str(run_dir),
                    "gpu_name": _gpu_name(),
                },
            )
            return "complete"
        except Exception as e:
            last_status = "failed"
            _append_jsonl(
                jsonl_path,
                {
                    "cell_id": cell.cell_id,
                    "attempt": attempt,
                    "status": "failed",
                    "error": str(e),
                    "start": start,
                    "end": datetime.now(timezone.utc).isoformat(),
                    "duration_s": round(time.perf_counter() - t0, 3),
                    "train_exit": train_exit,
                    "holdout_exit": holdout_exit,
                    "run_dir": str(run_dir) if run_dir else None,
                    "gpu_name": _gpu_name(),
                },
            )
            if attempt >= attempts:
                print(f"FAILED {cell.cell_id}: {e}")
                return "failed"
            print(f"Retry {attempt}/{max_retries} for {cell.cell_id}: {e}")
    return last_status


def _run_logged(
    cmd: List[str], log_path: Path, append: bool = False
) -> Tuple[int, str, str]:
    mode = "a" if append else "w"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, mode, encoding="utf-8") as log:
        log.write(f"\n$ {' '.join(cmd)}\n")
        log.flush()
        proc = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            text=True,
            capture_output=True,
        )
        log.write(proc.stdout or "")
        log.write(proc.stderr or "")
    return proc.returncode, proc.stdout or "", proc.stderr or ""


def _append_jsonl(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj) + "\n")


def main(argv: Optional[Sequence[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Run a partition-variance grid shard")
    parser.add_argument("--grid", required=True, help="Grid YAML path")
    parser.add_argument("--shard", type=int, default=0)
    parser.add_argument("--num-shards", type=int, default=1)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--production", action="store_true")
    parser.add_argument("--holdout-only", action="store_true")
    parser.add_argument("--max-retries", type=int, default=1)
    args = parser.parse_args(argv)

    grid_path = Path(args.grid)
    if not grid_path.is_absolute():
        grid_path = REPO_ROOT / grid_path
    grid = load_grid(grid_path)
    cells = enumerate_cells(grid)
    if int(grid.get("expected_runs", len(cells))) != len(cells):
        print(
            f"WARNING: expected_runs={grid.get('expected_runs')} "
            f"but enumerated {len(cells)}"
        )
    mine = shard_cells(cells, args.shard, args.num_shards)
    expected_rounds = int(grid.get("expected_rounds", 15))
    grid_overrides = list(grid.get("overrides") or [])

    if args.production:
        production_guard(grid)

    grid_name = str(grid.get("name", grid_path.stem))
    log_dir = REPO_ROOT / "logs" / f"{grid_name}_shard{args.shard}"
    jsonl_path = REPO_ROOT / "results" / "launch" / f"{grid_name}_shard{args.shard}.jsonl"

    print(
        f"Grid {grid_name}: {len(cells)} cells total, "
        f"shard {args.shard}/{args.num_shards} -> {len(mine)} cells"
    )
    if args.dry_run:
        for c in mine:
            print(
                f"  {c.cell_id}  {c.config}  "
                f"status={classify_cell(c, expected_rounds)}"
            )
        return

    counts: Dict[str, int] = {}
    if args.workers <= 1:
        for c in mine:
            st = run_one_cell(
                c,
                device=args.device,
                grid_name=grid_name,
                shard=args.shard,
                max_retries=args.max_retries,
                holdout_only=args.holdout_only,
                dry_run=False,
                log_dir=log_dir,
                jsonl_path=jsonl_path,
                expected_rounds=expected_rounds,
                overrides=grid_overrides,
                workers=args.workers,
            )
            counts[st] = counts.get(st, 0) + 1
    else:
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            futs = {
                ex.submit(
                    run_one_cell,
                    c,
                    device=args.device,
                    grid_name=grid_name,
                    shard=args.shard,
                    max_retries=args.max_retries,
                    holdout_only=args.holdout_only,
                    dry_run=False,
                    log_dir=log_dir,
                    jsonl_path=jsonl_path,
                    expected_rounds=expected_rounds,
                    overrides=grid_overrides,
                    workers=args.workers,
                ): c
                for c in mine
            }
            for fut in as_completed(futs):
                st = fut.result()
                counts[st] = counts.get(st, 0) + 1

    print("Summary:", counts)


if __name__ == "__main__":
    main()
