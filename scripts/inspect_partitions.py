#!/usr/bin/env python3
"""Inspect Dolly Dirichlet partitions for data seeds 2001 to 2010 (Phase C)."""

from __future__ import annotations

import io
import sys
from collections import Counter
from pathlib import Path

from datasets import load_dataset

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.data.data_partitioner import DataPartitioner
from src.data.partition_stats import compute_partition_stats, resolve_label_source

DATA_SEEDS = list(range(2001, 2011))
NUM_CLIENTS = 10
ALPHA = 0.1
LABEL_COLUMN = "category"
TRAIN_END = 3000
HOLDOUT_START = 3000
HOLDOUT_END = 3500
MIN_ACTIVE = 3


def main() -> None:
    out = io.StringIO()

    def p(msg: str = "") -> None:
        print(msg)
        out.write(msg + "\n")

    p("Phase C partition preview")
    p("dataset: databricks/databricks-dolly-15k")
    p(f"train slice: train[0:{TRAIN_END}]")
    p(f"holdout slice: train[{HOLDOUT_START}:{HOLDOUT_END}]")
    p(f"partition: label_skew alpha={ALPHA} label_column={LABEL_COLUMN} num_clients={NUM_CLIENTS}")
    p(f"data seeds: {DATA_SEEDS[0]} to {DATA_SEEDS[-1]}")
    p()

    full = load_dataset("databricks/databricks-dolly-15k", split="train")
    train_ds = full.select(range(0, TRAIN_END))
    holdout_ds = full.select(range(HOLDOUT_START, min(HOLDOUT_END, len(full))))

    # Global category histogram on the training slice
    global_hist = Counter(str(v) for v in train_ds[LABEL_COLUMN])
    global_hist = {k: int(global_hist[k]) for k in sorted(global_hist)}
    p("Global category histogram (train[0:3000]):")
    for k, v in global_hist.items():
        p(f"  {k}: {v}")
    p(f"  categories={len(global_hist)}  sum={sum(global_hist.values())}")
    p()

    # Held-out overlap check (index ranges)
    train_idx = set(range(0, TRAIN_END))
    holdout_idx = set(range(HOLDOUT_START, HOLDOUT_START + len(holdout_ds)))
    overlap = train_idx & holdout_idx
    p("Held-out overlap check (row indices):")
    p(f"  train indices: 0..{TRAIN_END - 1} (n={len(train_idx)})")
    p(f"  holdout indices: {HOLDOUT_START}..{HOLDOUT_START + len(holdout_ds) - 1} (n={len(holdout_idx)})")
    p(f"  overlap count: {len(overlap)}")
    if overlap:
        p("  FAIL: training and held-out index ranges overlap")
        raise SystemExit(1)
    p("  PASS: no index overlap")
    p()

    # Same label-source gate as the runner
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

    active_by_seed = {}
    for seed in DATA_SEEDS:
        partitioner = DataPartitioner(train_ds, num_clients=NUM_CLIENTS, seed=seed)
        client_datasets = partitioner.label_skew_partition(
            label_column=LABEL_COLUMN,
            alpha=ALPHA,
        )
        stats = compute_partition_stats(
            client_datasets,
            label_column=LABEL_COLUMN,
            label_source=label_source,
            partition_method="label_skew",
            partition_alpha=ALPHA,
            data_seed=seed,
            num_clients_configured=NUM_CLIENTS,
        )
        active_by_seed[seed] = stats["active_clients"]
        p(f"=== data_seed={seed}  active_clients={stats['active_clients']}  total={stats['total_samples']} ===")
        p(f"client_sizes: {stats['client_sizes']}")
        for i, hist in enumerate(stats["per_client_label_hist"]):
            p(f"  client {i}: size={stats['client_sizes'][i]}  hist={hist}")
        p(f"global_label_hist: {stats['global_label_hist']}")
        p()

    min_active = min(active_by_seed.values())
    min_seeds = [s for s, a in active_by_seed.items() if a == min_active]
    p("Summary active_clients by seed:")
    for seed in DATA_SEEDS:
        p(f"  {seed}: {active_by_seed[seed]}")
    p(f"minimum active_clients across seeds: {min_active} (seeds {min_seeds})")
    p()

    # Acceptance checks
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
    preview_path.write_text(out.getvalue(), encoding="utf-8")
    p(f"Wrote {preview_path.relative_to(REPO_ROOT)}")

    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
