#!/usr/bin/env python3
"""Phase H verification for the partition-variance study.

Curated assertions V1-V11. Exit 0 only when V1-V8 and V11 pass.
V9 stays empty until Phase L. V10 prints a resume/retry census and never fails.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.run_grid import (  # noqa: E402
    Cell,
    _has_complete_results_json,
    _has_holdout,
    _timestamp_dirs,
    enumerate_cells,
    load_grid,
)

# Per-client upload payload bytes (Phases D and F).
PAYLOAD_FULL = {
    "tl": 9_011_200,  # A+B
    "l3": 9_175_040,
}
# FFA-LoRA: after round 0, A is frozen and only B is uploaded (matches measured prod).
PAYLOAD_B_ONLY = {
    "tl": 3_244_032,
    "l3": 3_670_016,
}
EXPECTED_EVAL_DTYPE = {
    "tl": "torch.float32",
    "l3": "torch.float16",
}
EXPECTED_MODEL = {
    "tl": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    "l3": "meta-llama/Llama-3.2-3B",
}
PROD_EVAL_SHA256 = "201b79752f63ccc06aab8c612c8fb450e9c7f18ee04fff2a31aaf6808458df30"
DOLLY = "databricks/databricks-dolly-15k"
MB = 1024 * 1024

# V9 filled in Phase L
CLAIMS: List[Dict[str, Any]] = []


class CheckResult:
    def __init__(self, vid: str) -> None:
        self.vid = vid
        self.failures: List[str] = []
        self.notes: List[str] = []

    def fail(self, msg: str) -> None:
        self.failures.append(msg)

    def note(self, msg: str) -> None:
        self.notes.append(msg)

    @property
    def ok(self) -> bool:
        return not self.failures


def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _complete_run_dirs(cell: Cell, expected_rounds: int = 15) -> List[Path]:
    out: List[Path] = []
    for d in _timestamp_dirs(cell):
        if not (d / "run_meta.json").is_file():
            continue
        if not (d / "partition_stats.json").is_file():
            continue
        if not _has_complete_results_json(d, expected_rounds):
            continue
        if not _has_holdout(d):
            continue
        out.append(d)
    return out


def _holdout_path_for(run_dir: Path) -> Optional[Path]:
    local = list(run_dir.rglob("instruction_holdout.json"))
    if local:
        return local[0]
    downstream = REPO_ROOT / "results" / "downstream_instruction"
    if not downstream.is_dir():
        return None
    parts = run_dir.parts
    try:
        i = parts.index("raw")
        mirror = downstream.joinpath(*parts[i + 1 :]) / "instruction_holdout.json"
        if mirror.is_file():
            return mirror
    except ValueError:
        pass
    return None


def resolve_holdout(run_dir: Path) -> Path:
    p = _holdout_path_for(run_dir)
    if p is None:
        raise FileNotFoundError(f"no instruction_holdout.json for {run_dir}")
    return p


def v1(cells: Sequence[Cell]) -> CheckResult:
    r = CheckResult("V1")
    for cell in cells:
        completes = _complete_run_dirs(cell)
        if len(completes) != 1:
            r.fail(
                f"{cell.cell_id}: expected exactly 1 complete prod_v1 run, got {len(completes)} "
                f"{[d.name for d in completes]}"
            )
    if r.ok:
        r.note(f"{len(cells)} cells each have exactly one complete prod_v1 run")
    return r


def v2(cells: Sequence[Cell], grid_name: str) -> CheckResult:
    r = CheckResult("V2")
    lib_keys: set = set()
    gpu_names: set = set()
    for cell in cells:
        run_dir = _complete_run_dirs(cell)[0]
        meta = _load_json(run_dir / "run_meta.json")
        if meta.get("git_describe") != "freeze-v1":
            r.fail(f"{cell.cell_id}: git_describe={meta.get('git_describe')!r} != freeze-v1")
        if meta.get("git_dirty_tracked") is not False:
            r.fail(
                f"{cell.cell_id}: git_dirty_tracked={meta.get('git_dirty_tracked')!r} (want false)"
            )
        if meta.get("device") != "cuda":
            r.fail(f"{cell.cell_id}: device={meta.get('device')!r} != cuda")
        hw = meta.get("hardware") or {}
        if not hw.get("gpu_name"):
            r.fail(f"{cell.cell_id}: hardware.gpu_name missing")
        gpu_names.add(hw.get("gpu_name"))
        lib_keys.add(
            (
                hw.get("torch"),
                hw.get("transformers"),
                hw.get("peft"),
                hw.get("datasets"),
            )
        )
    if len(lib_keys) != 1:
        r.fail(f"grid {grid_name}: library versions not identical: {lib_keys}")
    if len(gpu_names) != 1:
        r.fail(f"grid {grid_name}: gpu_name not identical: {gpu_names}")
    if r.ok:
        r.note(f"grid {grid_name}: libs={next(iter(lib_keys))} gpu={next(iter(gpu_names))}")
    return r


def v3(cells: Sequence[Cell], model_key: str) -> CheckResult:
    r = CheckResult("V3")
    expected_model = EXPECTED_MODEL[model_key]
    for cell in cells:
        run_dir = _complete_run_dirs(cell)[0]
        cfg_path = run_dir / "config_merged.yaml"
        if not cfg_path.is_file():
            r.fail(f"{cell.cell_id}: missing config_merged.yaml")
            continue
        with cfg_path.open() as f:
            cfg = yaml.safe_load(f)
        checks = [
            (("model", "name"), expected_model),
            (("lora", "r"), 16),
            (("lora", "lora_alpha"), 32),
            (("lora", "target_modules"), ["q_proj", "v_proj"]),
            (("federated", "num_rounds"), 15),
            (("federated", "num_clients"), 10),
            (("federated", "clients_per_round"), 10),
            (("federated", "aggregation_method"), cell.method),
            (("data", "dataset_name"), DOLLY),
            (("data", "max_samples"), 3000),
            (("data", "label_column"), "category"),
        ]
        if cell.het == "a01":
            checks.extend(
                [
                    (("data", "partition_method"), "label_skew"),
                    (("data", "partition_alpha"), 0.1),
                ]
            )
        else:
            checks.append((("data", "partition_method"), "iid"))
        for keys, want in checks:
            cur: Any = cfg
            for k in keys:
                cur = (cur or {}).get(k) if isinstance(cur, dict) else None
            if cur != want:
                r.fail(f"{cell.cell_id}: config {'.'.join(keys)}={cur!r} want {want!r}")
    if r.ok:
        r.note(f"{len(cells)} configs match Section 0 for model={model_key}")
    return r


def v4(cells: Sequence[Cell]) -> CheckResult:
    r = CheckResult("V4")
    for cell in cells:
        run_dir = _complete_run_dirs(cell)[0]
        ps = _load_json(run_dir / "partition_stats.json")
        if cell.het == "a01":
            if ps.get("label_source") != "column":
                r.fail(
                    f"{cell.cell_id}: label_source={ps.get('label_source')!r} want 'column'"
                )
            if ps.get("label_column") != "category":
                r.fail(
                    f"{cell.cell_id}: label_column={ps.get('label_column')!r} want 'category'"
                )
        else:
            if ps.get("label_source") != "none":
                r.fail(
                    f"{cell.cell_id}: label_source={ps.get('label_source')!r} want 'none' (iid)"
                )
        hist = ps.get("global_label_hist") or {}
        if len(hist) != 8:
            r.fail(f"{cell.cell_id}: global_label_hist has {len(hist)} keys, want 8")
        sizes = ps.get("client_sizes") or []
        if sum(sizes) != 3000:
            r.fail(f"{cell.cell_id}: sum(client_sizes)={sum(sizes)} want 3000")
        if ps.get("total_samples") != 3000:
            r.fail(f"{cell.cell_id}: total_samples={ps.get('total_samples')} want 3000")
    if r.ok:
        r.note("partition_stats label_source/hist/sizes OK for a01 and iid")
    return r


def v5(cells: Sequence[Cell]) -> CheckResult:
    r = CheckResult("V5")
    # group by (het, data_seed) -> list of (client_sizes, per_client_label_hist)
    by_seed: Dict[Tuple[str, int], List[Tuple[Any, Any, str]]] = defaultdict(list)
    for cell in cells:
        run_dir = _complete_run_dirs(cell)[0]
        ps = _load_json(run_dir / "partition_stats.json")
        key = (cell.het, cell.data_seed)
        by_seed[key].append(
            (ps.get("client_sizes"), ps.get("per_client_label_hist"), cell.cell_id)
        )
    for key, rows in by_seed.items():
        ref_sizes, ref_hist, ref_id = rows[0]
        for sizes, hist, cid in rows[1:]:
            if sizes != ref_sizes:
                r.fail(
                    f"data_seed={key}: client_sizes differ between {ref_id} and {cid}"
                )
            if hist != ref_hist:
                r.fail(
                    f"data_seed={key}: per_client_label_hist differ between {ref_id} and {cid}"
                )
    if r.ok:
        r.note(f"partition determinism OK across {len(by_seed)} (het, data_seed) groups")
    return r


def v6(cells: Sequence[Cell], model_key: str) -> CheckResult:
    r = CheckResult("V6")
    full = PAYLOAD_FULL[model_key]
    b_only = PAYLOAD_B_ONLY[model_key]
    for cell in cells:
        run_dir = _complete_run_dirs(cell)[0]
        ps = _load_json(run_dir / "partition_stats.json")
        active = int(ps["active_clients"])
        rounds = _load_json(run_dir / "results.json")
        if not isinstance(rounds, list):
            r.fail(f"{cell.cell_id}: results.json is not a list")
            continue
        prev = 0.0
        for i, row in enumerate(rounds):
            got_cum = float(row.get("upload_mb"))
            got_inc = got_cum - prev
            prev = got_cum
            if cell.method == "ffa_lora" and i > 0:
                payload = b_only
            else:
                payload = full
            expected_mb = active * payload / MB
            if not math.isclose(got_inc, expected_mb, rel_tol=0, abs_tol=1e-6):
                r.fail(
                    f"{cell.cell_id} round {i}: upload_increment={got_inc} want {expected_mb} "
                    f"(active={active} * {payload} B)"
                )
                break
    if r.ok:
        r.note(
            f"upload increments match active_clients * payload "
            f"(full={full} B; ffa post-r0 B-only={b_only} B)"
        )
    return r


def v7(cells: Sequence[Cell], model_key: str) -> CheckResult:
    r = CheckResult("V7")
    want_dtype = EXPECTED_EVAL_DTYPE[model_key]
    dtypes: set = set()
    base_losses: List[float] = []
    for cell in cells:
        run_dir = _complete_run_dirs(cell)[0]
        try:
            hp = resolve_holdout(run_dir)
        except FileNotFoundError as e:
            r.fail(str(e))
            continue
        payload = _load_json(hp)
        row = payload.get("row") or {}
        meta = payload.get("meta") or {}
        dataset = row.get("dataset") or meta.get("dataset")
        if dataset != DOLLY:
            r.fail(f"{cell.cell_id}: holdout dataset={dataset!r} want {DOLLY}")
        if int(row.get("heldout_start", -1)) != 3000:
            r.fail(f"{cell.cell_id}: heldout_start={row.get('heldout_start')} want 3000")
        if int(row.get("heldout_examples", -1)) != 500:
            r.fail(
                f"{cell.cell_id}: heldout_examples={row.get('heldout_examples')} want 500"
            )
        if int(row.get("max_seq_length", -1)) != 256:
            r.fail(
                f"{cell.cell_id}: max_seq_length={row.get('max_seq_length')} want 256"
            )
        fmt = row.get("formatter_version") or meta.get("formatter_version")
        if fmt != "v2-dolly-context":
            r.fail(f"{cell.cell_id}: formatter_version={fmt!r}")
        loss = float(row.get("tuned_loss"))
        if not math.isfinite(loss):
            r.fail(f"{cell.cell_id}: tuned_loss not finite: {loss}")
        dtype = row.get("eval_dtype") or meta.get("eval_dtype")
        dtypes.add(dtype)
        if dtype != want_dtype:
            r.fail(f"{cell.cell_id}: eval_dtype={dtype!r} want {want_dtype!r}")
        base_losses.append(float(row.get("base_loss")))
    if len(dtypes) != 1:
        r.fail(f"grid {model_key}: eval_dtype not identical within grid: {dtypes}")
    if base_losses:
        ref = base_losses[0]
        for i, b in enumerate(base_losses):
            if abs(b - ref) > 1e-6:
                r.fail(
                    f"grid {model_key}: base_loss varies beyond 1e-6: "
                    f"{ref} vs {b} (index {i})"
                )
                break
    if r.ok:
        r.note(
            f"{model_key}: eval_dtype={want_dtype}, base_loss={base_losses[0]:.10f} "
            f"identical within 1e-6"
        )
    return r


def v8(cells: Sequence[Cell]) -> CheckResult:
    r = CheckResult("V8")

    def walk(obj: Any, path: str) -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                walk(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                walk(v, f"{path}[{i}]")
        elif isinstance(obj, float):
            if math.isnan(obj) or math.isinf(obj):
                r.fail(f"{path}: non-finite float {obj}")

    for cell in cells:
        run_dir = _complete_run_dirs(cell)[0]
        walk(_load_json(run_dir / "results.json"), f"{cell.cell_id}/results.json")
    if r.ok:
        r.note("no NaN/inf in results.json")
    return r


def v9() -> CheckResult:
    r = CheckResult("V9")
    if not CLAIMS:
        r.note("CLAIMS empty (Phase L); not required for Phase H exit")
    return r


def v10(grid_names: Sequence[str]) -> CheckResult:
    """Resume/retry census. Never fails the run."""
    r = CheckResult("V10")
    launch_dir = REPO_ROOT / "results" / "launch"
    # Per grid/method aggregates
    # cells with attempt>1, resumed from checkpoint, failed attempts
    rows: List[Tuple[str, str, int, int, int, int]] = []
    for gname in grid_names:
        # Collect jsonl for this grid
        paths = sorted(launch_dir.glob(f"{gname}_shard*.jsonl"))
        by_cell: Dict[str, List[dict]] = defaultdict(list)
        for path in paths:
            for line in path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                rec = json.loads(line)
                if int(rec.get("attempt", 0)) == 0:
                    continue  # skip records
                by_cell[rec["cell_id"]].append(rec)

        # Also scan run_meta overrides.resume for completed runs in this grid
        from scripts.run_grid import load_grid as _lg, enumerate_cells as _ec

        grid = _lg(REPO_ROOT / "grids" / f"{gname}.yaml")
        cells = _ec(grid)
        method_cells: Dict[str, List[Cell]] = defaultdict(list)
        for c in cells:
            method_cells[c.method].append(c)

        for method, mcells in sorted(method_cells.items()):
            n_attempt_gt1 = 0
            n_resumed = 0
            n_failed_attempts = 0
            for cell in mcells:
                recs = by_cell.get(cell.cell_id, [])
                attempts = [int(x.get("attempt", 0)) for x in recs]
                if any(a > 1 for a in attempts):
                    n_attempt_gt1 += 1
                n_failed_attempts += sum(
                    1 for x in recs if x.get("status") == "failed"
                )
                # resume from run_meta of the complete dir
                completes = _complete_run_dirs(cell)
                if completes:
                    meta = _load_json(completes[0] / "run_meta.json")
                    resume = (meta.get("overrides") or {}).get("resume")
                    if resume:
                        n_resumed += 1
            rows.append(
                (
                    gname,
                    method,
                    len(mcells),
                    n_attempt_gt1,
                    n_resumed,
                    n_failed_attempts,
                )
            )

    print("\n=== V10 resume/retry census (informational; does not fail) ===")
    print(
        f"{'grid':<6} {'method':<10} {'cells':>5} {'attempt>1':>10} "
        f"{'resumed':>8} {'failed_atts':>11}"
    )
    for gname, method, n, a, res, fail in rows:
        print(f"{gname:<6} {method:<10} {n:>5} {a:>10} {res:>8} {fail:>11}")
    r.note(f"printed census for grids {list(grid_names)}")
    return r


def v11() -> CheckResult:
    r = CheckResult("V11")
    eval_path = REPO_ROOT / "scripts" / "evaluate_instruction_holdout.py"
    text = eval_path.read_text(encoding="utf-8")
    # Float16 change present in working tree / HEAD
    if 'eval_torch_dtype = "float16" if device == "cuda"' not in text and (
        'eval_torch_dtype = "float16"' not in text
    ):
        # allow auto branch form
        if "float16" not in text or "empty_cache" not in text:
            r.fail("float16 eval change not found in scripts/evaluate_instruction_holdout.py")
    if "empty_cache" not in text:
        r.fail("cuda empty_cache between tuned/base loads not found (sequential load)")

    # freeze-v2 tag should contain the production byte-for-byte script
    try:
        blob = subprocess.check_output(
            ["git", "show", "freeze-v2:scripts/evaluate_instruction_holdout.py"],
            cwd=str(REPO_ROOT),
        )
    except subprocess.CalledProcessError:
        r.fail("freeze-v2 tag missing or does not contain evaluate_instruction_holdout.py")
        return r
    sha = hashlib.sha256(blob).hexdigest()
    if sha != PROD_EVAL_SHA256:
        r.fail(
            f"freeze-v2 eval script sha256={sha} != production host sha256={PROD_EVAL_SHA256}"
        )
    else:
        r.note(f"freeze-v2 eval script matches GPU-host production sha256={PROD_EVAL_SHA256}")

    # Commit that introduced float16 relative to freeze-v1
    try:
        log = subprocess.check_output(
            [
                "git",
                "log",
                "--oneline",
                "freeze-v1..freeze-v2",
                "--",
                "scripts/evaluate_instruction_holdout.py",
            ],
            cwd=str(REPO_ROOT),
            text=True,
        ).strip()
    except subprocess.CalledProcessError as e:
        r.fail(f"git log freeze-v1..freeze-v2 failed: {e}")
        log = ""
    if not log:
        r.fail("no commit between freeze-v1 and freeze-v2 touches evaluate_instruction_holdout.py")
    else:
        r.note(f"float16 introduced in:\n{log}")

    # TinyLlama path: float16 change is CUDA-default only; TL holdouts recorded float32
    # Confirm TL JSONs are float32 (change did not alter their recorded dtype).
    tl_dtypes = set()
    for p in (REPO_ROOT / "results" / "downstream_instruction").glob(
        "vp_tl_*/**/instruction_holdout.json"
    ):
        row = _load_json(p).get("row") or {}
        tl_dtypes.add(row.get("eval_dtype"))
    if tl_dtypes and tl_dtypes != {"torch.float32"}:
        r.fail(f"TinyLlama holdouts eval_dtype unexpected: {tl_dtypes}")
    else:
        r.note("TinyLlama holdouts remain torch.float32 (pre-change / CPU-path equivalent)")

    return r


def run_for_grid(grid_path: Path) -> Tuple[str, str, List[Cell], List[CheckResult]]:
    grid = load_grid(grid_path)
    cells = enumerate_cells(grid)
    name = str(grid.get("name") or grid_path.stem)
    # infer model key
    from scripts.run_grid import model_from_pattern

    model_key = model_from_pattern(grid["config_pattern"])
    results = [
        v1(cells),
        v2(cells, name),
        v3(cells, model_key),
        v4(cells),
        v5(cells),
        v6(cells, model_key),
        v7(cells, model_key),
        v8(cells),
    ]
    return name, model_key, cells, results


def main() -> None:
    parser = argparse.ArgumentParser(description="Partition-variance Phase H verifier")
    parser.add_argument(
        "--grids",
        nargs="+",
        required=True,
        help="Grid YAML paths (e.g. grids/tl.yaml grids/l3.yaml)",
    )
    args = parser.parse_args()

    all_results: List[CheckResult] = []
    grid_names: List[str] = []

    for g in args.grids:
        path = Path(g)
        if not path.is_absolute():
            path = REPO_ROOT / path
        name, model_key, cells, results = run_for_grid(path)
        grid_names.append(name)
        print(f"\n======== grid {name} ({model_key}, {len(cells)} cells) ========")
        for res in results:
            status = "PASS" if res.ok else "FAIL"
            print(f"[{status}] {res.vid}")
            for n in res.notes:
                print(f"       {n}")
            for f in res.failures:
                print(f"       FAIL: {f}")
            all_results.append(res)

    print("\n======== cross-grid ========")
    for res in (v9(), v10(grid_names), v11()):
        # V9 and V10 never fail the exit criteria for Phase H; V11 must pass
        if res.vid == "V9":
            status = "SKIP" if not CLAIMS else ("PASS" if res.ok else "FAIL")
        elif res.vid == "V10":
            status = "INFO"
        else:
            status = "PASS" if res.ok else "FAIL"
        print(f"[{status}] {res.vid}")
        for n in res.notes:
            print(f"       {n}")
        for f in res.failures:
            print(f"       FAIL: {f}")
        all_results.append(res)

    # Exit criteria: V1-V8 and V11 must pass; V9 unfilled OK; V10 informational
    blocking = [
        res
        for res in all_results
        if res.vid not in ("V9", "V10") and not res.ok
    ]
    if blocking:
        print(f"\nVERIFY FAILED: {len(blocking)} blocking check(s)")
        sys.exit(1)
    print("\nVERIFY OK: V1-V8 and V11 passed (V9 deferred, V10 informational)")
    sys.exit(0)


if __name__ == "__main__":
    main()
