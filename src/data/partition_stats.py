"""Partition statistics and label-source resolution (pure functions, no torch)."""

from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Optional, Sequence


def _hist(values) -> Dict[str, int]:
    c = Counter(str(v) for v in values)
    return {k: int(c[k]) for k in sorted(c)}


def resolve_label_source(
    columns: Sequence[str],
    partition_method: str,
    label_column: Optional[str],
    require_label: bool,
) -> str:
    """
    Resolve how labels will be obtained for partitioning.

    Returns "column" | "length_proxy" | "none".
    Raises SystemExit when label_skew requires a missing column.
    """
    if partition_method == "label_skew":
        if label_column is not None and label_column in columns:
            return "column"
        if require_label:
            raise SystemExit(
                f"ERROR: data.label_column={label_column!r} not in dataset columns "
                f"{list(columns)} and data.require_label_column is true."
            )
        return "length_proxy"
    return "none"


def compute_partition_stats(
    client_datasets,
    *,
    label_column: Optional[str],
    label_source: str,  # "column" | "length_proxy" | "none"
    partition_method: str,
    partition_alpha: Optional[float],
    data_seed: int,
    num_clients_configured: int,
) -> Dict[str, Any]:
    sizes = [int(len(ds)) for ds in client_datasets]
    per_client: List[Dict[str, int]] = []
    global_hist: Counter = Counter()
    for ds in client_datasets:
        if label_column and len(ds) > 0 and label_column in ds.column_names:
            h = _hist(ds[label_column])
        else:
            h = {}
        per_client.append(h)
        global_hist.update(h)
    return {
        "schema_version": 1,
        "data_seed": int(data_seed),
        "partition_method": partition_method,
        "partition_alpha": partition_alpha,
        "label_column": label_column,
        "label_source": label_source,
        "num_clients_configured": int(num_clients_configured),
        "active_clients": int(sum(1 for s in sizes if s > 0)),
        "client_sizes": sizes,
        "total_samples": int(sum(sizes)),
        "per_client_label_hist": per_client,
        "global_label_hist": {k: int(global_hist[k]) for k in sorted(global_hist)},
    }


def optimizer_steps_for_n(
    n: int,
    *,
    batch_size: int,
    grad_accum: int,
    local_epochs: int = 1,
) -> int:
    """
    Optimizer steps taken by FederatedClient for n samples.

    Matches client.py: DataLoader without drop_last; optimizer.step only when
    (batch_index + 1) % grad_accum == 0. Trailing incomplete accumulation blocks
    are discarded.
    """
    if n <= 0 or batch_size <= 0 or grad_accum <= 0 or local_epochs <= 0:
        return 0
    # ceil(n / batch_size) without float:
    num_batches = (n + batch_size - 1) // batch_size
    steps_per_epoch = num_batches // grad_accum
    return int(steps_per_epoch * local_epochs)


def discarded_trailing_samples(
    n: int,
    *,
    batch_size: int,
    grad_accum: int,
    local_epochs: int = 1,
) -> int:
    """
    Samples that never enter a completed accumulation block (per epoch), times epochs.

    For one epoch: samples in leftover batches after floor(ceil(n/batch)/accum)
    full accumulation blocks. Equivalent to n - used_batches * batch_size when
    used_batches < num_batches, else 0; when zero steps, all n are discarded.
    """
    if n <= 0 or batch_size <= 0 or grad_accum <= 0 or local_epochs <= 0:
        return 0
    num_batches = (n + batch_size - 1) // batch_size
    used_batches = (num_batches // grad_accum) * grad_accum
    if used_batches == 0:
        discarded_per_epoch = n
    elif used_batches >= num_batches:
        discarded_per_epoch = 0
    else:
        discarded_per_epoch = n - used_batches * batch_size
    return int(discarded_per_epoch * local_epochs)
