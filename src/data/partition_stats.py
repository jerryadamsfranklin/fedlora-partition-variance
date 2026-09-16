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
