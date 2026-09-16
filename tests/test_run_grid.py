"""Tests for grid enumeration, sharding, and production guard."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from scripts.run_grid import (
    enumerate_cells,
    load_grid,
    production_guard,
    shard_cells,
)

REPO = Path(__file__).resolve().parents[1]


def test_tl_enumeration_count():
    cells = enumerate_cells(load_grid(REPO / "grids" / "tl.yaml"))
    assert len(cells) == 75


def test_l3_enumeration_count():
    cells = enumerate_cells(load_grid(REPO / "grids" / "l3.yaml"))
    assert len(cells) == 45


@pytest.mark.parametrize("n", [1, 3, 6])
def test_shards_partition_exactly_once(n: int):
    cells = enumerate_cells(load_grid(REPO / "grids" / "tl.yaml"))
    seen = []
    for shard in range(n):
        seen.extend(shard_cells(cells, shard, n))
    assert len(seen) == len(cells)
    assert {c.cell_id for c in seen} == {c.cell_id for c in cells}


def test_first_three_a01_are_methods_for_2001_7001():
    cells = enumerate_cells(load_grid(REPO / "grids" / "tl.yaml"))
    a01 = [c for c in cells if c.het == "a01"]
    first3 = a01[:3]
    assert [(c.method, c.data_seed, c.run_seed) for c in first3] == [
        ("fedit", 2001, 7001),
        ("ffa_lora", 2001, 7001),
        ("flora", 2001, 7001),
    ]


def test_production_guard_fails_untagged():
    with pytest.raises(SystemExit, match="freeze-v1"):
        production_guard(
            git_describe_exact=lambda: "v0-import",
            git_status_tracked=lambda: "",
            env={"HF_TOKEN": "x"},
        )


def test_production_guard_fails_dirty_or_missing_token():
    with pytest.raises(SystemExit, match="clean tracked"):
        production_guard(
            git_describe_exact=lambda: "freeze-v1",
            git_status_tracked=lambda: " M foo.py",
            env={"HF_TOKEN": "x"},
        )
    with pytest.raises(SystemExit, match="HF_TOKEN"):
        production_guard(
            git_describe_exact=lambda: "freeze-v1",
            git_status_tracked=lambda: "",
            env={},
        )


def test_orphan_folder_classified_separately(tmp_path, monkeypatch):
    from scripts import run_grid as rg

    cells = enumerate_cells(load_grid(REPO / "grids" / "tl.yaml"))
    cell = next(
        c
        for c in cells
        if c.het == "a01" and c.method == "fedit" and c.data_seed == 2001 and c.run_seed == 7001
    )
    # Point REPO_ROOT results under tmp
    monkeypatch.setattr(rg, "REPO_ROOT", tmp_path)
    orphan = (
        tmp_path
        / "results"
        / "raw"
        / cell.exp_name
        / cell.method
        / cell.seed_dir
        / cell.tag
        / "19990101_000000"
    )
    orphan.mkdir(parents=True)
    (orphan / "partition_stats.json").write_text('{"schema_version": 1}\n', encoding="utf-8")
    assert rg.classify_cell(cell) == "orphan"
