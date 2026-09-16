"""Tests for partition_stats and require_label_column behavior."""

from __future__ import annotations

import pytest
from datasets import Dataset

from src.data.data_partitioner import DataPartitioner
from src.data.partition_stats import (
    compute_partition_stats,
    resolve_label_source,
)


def _make_category_dataset(n: int = 200, n_cats: int = 8) -> Dataset:
    cats = [f"c{i % n_cats}" for i in range(n)]
    return Dataset.from_dict(
        {
            "instruction": [f"inst-{i}" for i in range(n)],
            "response": [f"resp-{i}" for i in range(n)],
            "category": cats,
        }
    )


def test_label_skew_stats_sum_and_hist():
    ds = _make_category_dataset(200, 8)
    parts = DataPartitioner(ds, 10, seed=2001).label_skew_partition("category", 0.1)
    stats = compute_partition_stats(
        parts,
        label_column="category",
        label_source="column",
        partition_method="label_skew",
        partition_alpha=0.1,
        data_seed=2001,
        num_clients_configured=10,
    )
    assert sum(stats["client_sizes"]) == 200
    assert sum(stats["global_label_hist"].values()) == 200
    assert stats["active_clients"] == sum(1 for s in stats["client_sizes"] if s > 0)


def test_partition_determinism_across_seeds():
    ds = _make_category_dataset(200, 8)

    def _stats(seed: int):
        parts = DataPartitioner(ds, 10, seed=seed).label_skew_partition("category", 0.1)
        return compute_partition_stats(
            parts,
            label_column="category",
            label_source="column",
            partition_method="label_skew",
            partition_alpha=0.1,
            data_seed=seed,
            num_clients_configured=10,
        )

    a = _stats(2001)
    b = _stats(2001)
    c = _stats(2002)
    assert a["client_sizes"] == b["client_sizes"]
    assert a["per_client_label_hist"] == b["per_client_label_hist"]
    assert a["client_sizes"] != c["client_sizes"] or a["per_client_label_hist"] != c[
        "per_client_label_hist"
    ]


def test_resolve_label_source_require_raises():
    with pytest.raises(SystemExit, match="require_label_column"):
        resolve_label_source(
            columns=["instruction", "response"],
            partition_method="label_skew",
            label_column="category",
            require_label=True,
        )


def test_resolve_label_source_column_and_proxy():
    assert (
        resolve_label_source(
            ["category", "instruction"],
            "label_skew",
            "category",
            True,
        )
        == "column"
    )
    assert (
        resolve_label_source(
            ["instruction"],
            "label_skew",
            "category",
            False,
        )
        == "length_proxy"
    )
    assert resolve_label_source(["category"], "iid", "category", True) == "none"
