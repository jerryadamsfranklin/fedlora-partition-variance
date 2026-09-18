#!/usr/bin/env python3
"""Inspect Dolly Dirichlet partitions (Phase C / Phase N5b)."""

from __future__ import annotations

import argparse
import io
import os
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import yaml
from datasets import load_dataset

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.data.data_partitioner import DataPartitioner
from src.data.partition_stats import (
    compute_partition_stats,
    discarded_trailing_samples,
    optimizer_steps_for_n,
    resolve_label_source,
)

NUM_CLIENTS = 10
LABEL_COLUMN = "category"
TRAIN_END = 3000
HOLDOUT_START = 3000
HOLDOUT_END = 3500
MIN_ACTIVE = 3

TL_CFG = "config/vp/vp_tl_flora_a01.yaml"
L3_CFG = "config/vp/vp_l3_flora_a01.yaml"


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(base)
    for key, val in override.items():
        if isinstance(val, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], val)
        else:
            out[key] = val
    return out


def load_config(path: str) -> Dict[str, Any]:
    abs_path = os.path.abspath(path)
    with open(abs_path, encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}
    inherit = config.pop("_inherit", None)
    if inherit:
        base = load_config(os.path.join(os.path.dirname(abs_path), inherit))
        config = _deep_merge(base, config)
    return config


def _train_hparams(cfg_path: str) -> Tuple[int, int, int]:
    cfg = load_config(str(REPO_ROOT / cfg_path))
    train = cfg.get("training") or {}
    batch = int(train["batch_size"])
    accum = int(train["gradient_accumulation_steps"])
    epochs = int(train.get("local_epochs", 1))
    return batch, accum, epochs


def _effective_stats(
    sizes: Sequence[int],
    *,
    batch_size: int,
    grad_accum: int,
    local_epochs: int,
) -> Dict[str, object]:
    steps = [
        optimizer_steps_for_n(
            int(n),
            batch_size=batch_size,
            grad_accum=grad_accum,
            local_epochs=local_epochs,
        )
        for n in sizes
    ]
    discarded = [
        discarded_trailing_samples(
            int(n),
            batch_size=batch_size,
            grad_accum=grad_accum,
            local_epochs=local_epochs,
        )
        for n in sizes
    ]
    active_mask = [int(n) > 0 for n in sizes]
    zero_step_active = sum(
        1 for n, s, a in zip(sizes, steps, active_mask) if a and s == 0
    )
    effective = sum(1 for s in steps if s > 0)
    return {
        "steps": steps,
        "discarded": discarded,
        "zero_step_active": zero_step_active,
        "effective_clients": effective,
        "discarded_total": int(sum(discarded)),
    }


def _parse_seeds(spec: str) -> List[int]:
    spec = spec.strip()
    if "-" in spec and "," not in spec:
        a, b = spec.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x) for x in spec.split(",") if x.strip()]


def run_preview(
    *,
    alpha: float,
    seeds: Sequence[int],
    title: str,
    append: bool,
) -> None:
    out = io.StringIO()

    def p(msg: str = "") -> None:
        print(msg)
        out.write(msg + "\n")

    tl_batch, tl_accum, tl_epochs = _train_hparams(TL_CFG)
    l3_batch, l3_accum, l3_epochs = _train_hparams(L3_CFG)
    assert (tl_batch, tl_accum) == (4, 4), (
        f"TinyLlama expected batch x accum 4x4, got {tl_batch}x{tl_accum}"
    )
    assert (l3_batch, l3_accum) == (2, 8), (
        f"LLaMA expected batch x accum 2x8, got {l3_batch}x{l3_accum}"
    )
    assert tl_epochs == 1 and l3_epochs == 1, (
        f"expected local_epochs=1, got tl={tl_epochs} l3={l3_epochs}"
    )

    p(title)
    p("dataset: databricks/databricks-dolly-15k")
    p(f"train slice: train[0:{TRAIN_END}]")
    p(f"holdout slice: train[{HOLDOUT_START}:{HOLDOUT_END}]")
    p(
        f"partition: label_skew alpha={alpha} label_column={LABEL_COLUMN} "
        f"num_clients={NUM_CLIENTS}"
    )
    p(f"data seeds: {seeds[0]} to {seeds[-1]} ({len(seeds)} seeds)")
    p(
        f"TinyLlama train hparams from {TL_CFG}: "
        f"batch={tl_batch} grad_accum={tl_accum} local_epochs={tl_epochs}"
    )
    p(
        f"LLaMA train hparams from {L3_CFG}: "
        f"batch={l3_batch} grad_accum={l3_accum} local_epochs={l3_epochs}"
    )
    p(
        "optimizer_steps = floor(ceil(n/batch) / grad_accum) * local_epochs "
        "(matches client.py: step only on complete accumulation blocks)"
    )
    p()

    full = load_dataset("databricks/databricks-dolly-15k", split="train")
    train_ds = full.select(range(0, TRAIN_END))
    holdout_ds = full.select(range(HOLDOUT_START, min(HOLDOUT_END, len(full))))

    global_hist = Counter(str(v) for v in train_ds[LABEL_COLUMN])
    global_hist = {k: int(global_hist[k]) for k in sorted(global_hist)}
    p("Global category histogram (train[0:3000]):")
    for k, v in global_hist.items():
        p(f"  {k}: {v}")
    p(f"  categories={len(global_hist)}  sum={sum(global_hist.values())}")
    p()

    train_idx = set(range(0, TRAIN_END))
    holdout_idx = set(range(HOLDOUT_START, HOLDOUT_START + len(holdout_ds)))
    overlap = train_idx & holdout_idx
    p("Held-out overlap check (row indices):")
    p(f"  train indices: 0..{TRAIN_END - 1} (n={len(train_idx)})")
    p(
        f"  holdout indices: {HOLDOUT_START}..{HOLDOUT_START + len(holdout_ds) - 1} "
        f"(n={len(holdout_idx)})"
    )
    p(f"  overlap count: {len(overlap)}")
    if overlap:
        p("  FAIL: training and held-out index ranges overlap")
        raise SystemExit(1)
    p("  PASS: no index overlap")
    p()

    label_source = resolve_label_source(
        train_ds.column_names,
        "label_skew",
        LABEL_COLUMN,
        require_label=True,
    )
    p(f"label_source={label_source}")
    if label_source != "column":
        raise SystemExit(f"ERROR: expected label_source=column, got {label_source!r}")
    p()

    active_by_seed: Dict[int, int] = {}
    summary_rows: List[Dict[str, object]] = []

    for seed in seeds:
        partitioner = DataPartitioner(train_ds, num_clients=NUM_CLIENTS, seed=seed)
        client_datasets = partitioner.label_skew_partition(
            label_column=LABEL_COLUMN,
            alpha=alpha,
        )
        stats = compute_partition_stats(
            client_datasets,
            label_column=LABEL_COLUMN,
            label_source=label_source,
            partition_method="label_skew",
            partition_alpha=alpha,
            data_seed=seed,
            num_clients_configured=NUM_CLIENTS,
        )
        sizes = list(stats["client_sizes"])
        active_by_seed[seed] = stats["active_clients"]
        active_sizes = sorted(s for s in sizes if s > 0)
        med = statistics.median(active_sizes) if active_sizes else float("nan")

        tl = _effective_stats(
            sizes, batch_size=tl_batch, grad_accum=tl_accum, local_epochs=tl_epochs
        )
        l3 = _effective_stats(
            sizes, batch_size=l3_batch, grad_accum=l3_accum, local_epochs=l3_epochs
        )

        summary_rows.append(
            {
                "seed": seed,
                "active": stats["active_clients"],
                "sizes_asc": active_sizes,
                "min": min(active_sizes) if active_sizes else 0,
                "median": med,
                "max": max(active_sizes) if active_sizes else 0,
                "tl_zero": tl["zero_step_active"],
                "tl_eff": tl["effective_clients"],
                "tl_disc": tl["discarded_total"],
                "l3_zero": l3["zero_step_active"],
                "l3_eff": l3["effective_clients"],
                "l3_disc": l3["discarded_total"],
            }
        )

        p(
            f"=== data_seed={seed}  active_clients={stats['active_clients']}  "
            f"total={stats['total_samples']} ==="
        )
        p(f"client_sizes: {sizes}")
        p(
            f"active sizes ascending: {active_sizes}  "
            f"min={min(active_sizes) if active_sizes else 'n/a'}  "
            f"median={med}  "
            f"max={max(active_sizes) if active_sizes else 'n/a'}"
        )
        for i, hist in enumerate(stats["per_client_label_hist"]):
            p(
                f"  client {i}: size={sizes[i]}  "
                f"tl_steps={tl['steps'][i]}  l3_steps={l3['steps'][i]}  "
                f"tl_discarded={tl['discarded'][i]}  l3_discarded={l3['discarded'][i]}  "
                f"hist={hist}"
            )
        p(
            f"TinyLlama: effective_clients={tl['effective_clients']}  "
            f"zero_step_active={tl['zero_step_active']}  "
            f"discarded_total={tl['discarded_total']}"
        )
        p(
            f"LLaMA: effective_clients={l3['effective_clients']}  "
            f"zero_step_active={l3['zero_step_active']}  "
            f"discarded_total={l3['discarded_total']}"
        )
        p(f"global_label_hist: {stats['global_label_hist']}")
        p()

    min_active = min(active_by_seed.values())
    min_seeds = [s for s, a in active_by_seed.items() if a == min_active]
    p("Summary active_clients by seed:")
    for seed in seeds:
        p(f"  {seed}: {active_by_seed[seed]}")
    p(f"minimum active_clients across seeds: {min_active} (seeds {min_seeds})")
    p()

    p("Per-seed effective-client / discarded-sample table:")
    p(
        "seed  active  sizes_asc (min/med/max)  "
        "tl_zero  tl_eff  tl_disc  l3_zero  l3_eff  l3_disc"
    )
    for row in summary_rows:
        p(
            f"{row['seed']}  {row['active']}  "
            f"{row['sizes_asc']} ({row['min']}/{row['median']}/{row['max']})  "
            f"{row['tl_zero']}  {row['tl_eff']}  {row['tl_disc']}  "
            f"{row['l3_zero']}  {row['l3_eff']}  {row['l3_disc']}"
        )
    seeds_tl_ge2 = [r["seed"] for r in summary_rows if int(r["tl_zero"]) >= 2]
    seeds_l3_ge2 = [r["seed"] for r in summary_rows if int(r["l3_zero"]) >= 2]
    p(f"seeds with >=2 TinyLlama zero-step active clients: {seeds_tl_ge2}")
    p(f"seeds with >=2 LLaMA zero-step active clients: {seeds_l3_ge2}")
    p()

    ok = True
    if len(global_hist) != 8 or sum(global_hist.values()) != 3000:
        p(
            f"FAIL: global histogram expected 8 categories summing to 3000; "
            f"got categories={len(global_hist)} sum={sum(global_hist.values())}"
        )
        ok = False
    else:
        p("PASS: global category histogram has 8 categories and sums to 3000")

    if min_active < MIN_ACTIVE:
        p(
            f"STOP: minimum active_clients={min_active} < {MIN_ACTIVE}. "
            "Record in DECISIONS.md before freezing; do not patch silently."
        )
        ok = False
    else:
        p(f"PASS: minimum active_clients={min_active} >= {MIN_ACTIVE}")

    preview_path = REPO_ROOT / "docs" / "partition_preview.txt"
    body = out.getvalue()
    if append and preview_path.is_file():
        prev = preview_path.read_text(encoding="utf-8")
        preview_path.write_text(prev.rstrip() + "\n\n" + body, encoding="utf-8")
        p(f"Appended {preview_path.relative_to(REPO_ROOT)}")
    else:
        preview_path.write_text(body, encoding="utf-8")
        p(f"Wrote {preview_path.relative_to(REPO_ROOT)}")

    if not ok:
        raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--alpha", type=float, default=0.1)
    parser.add_argument(
        "--seeds",
        default="2001-2010",
        help="Inclusive range A-B or comma-separated list",
    )
    parser.add_argument("--title", default="Phase C partition preview")
    parser.add_argument(
        "--append",
        action="store_true",
        help="Append to docs/partition_preview.txt instead of overwriting",
    )
    args = parser.parse_args()
    seeds = _parse_seeds(args.seeds)
    run_preview(
        alpha=args.alpha,
        seeds=seeds,
        title=args.title,
        append=args.append,
    )


if __name__ == "__main__":
    main()
