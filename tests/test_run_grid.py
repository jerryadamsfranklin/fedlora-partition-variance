"""Tests for grid enumeration, sharding, and production guard."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from scripts.run_grid import (
    _checkpoint_matches_holdout,
    _results_key,
    enumerate_cells,
    group_key,
    holdout_cmd,
    load_grid,
    production_guard,
    run_one_cell,
    shard_cells,
    train_cmd,
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


@pytest.mark.parametrize("n", [1, 3, 6])
def test_group_methods_share_shard(n: int):
    cells = enumerate_cells(load_grid(REPO / "grids" / "tl.yaml"))
    shard_by_cell = {}
    for shard in range(n):
        for cell in shard_cells(cells, shard, n):
            shard_by_cell[cell.cell_id] = shard
    by_group: dict[tuple, set[int]] = {}
    for cell in cells:
        by_group.setdefault(group_key(cell), set()).add(shard_by_cell[cell.cell_id])
    for group, shards in by_group.items():
        assert len(shards) == 1, f"group {group} split across shards {shards}"


def test_tl_shard_run_counts_for_three_shards():
    cells = enumerate_cells(load_grid(REPO / "grids" / "tl.yaml"))
    counts = [len(shard_cells(cells, shard, 3)) for shard in range(3)]
    assert counts == [27, 24, 24]


def test_l3_shard_run_counts_for_three_shards():
    cells = enumerate_cells(load_grid(REPO / "grids" / "l3.yaml"))
    counts = [len(shard_cells(cells, shard, 3)) for shard in range(3)]
    assert counts == [15, 15, 15]


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
            {},
            git_points_at=lambda: ["v0-import"],
            git_status_tracked=lambda: "",
            env={"HF_TOKEN": "x"},
        )


def test_production_guard_passes_with_multiple_tags_including_freeze():
    production_guard(
        {},
        git_points_at=lambda: ["release-candidate", "freeze-v1", "other"],
        git_status_tracked=lambda: "",
        env={"HF_TOKEN": "x"},
    )


def test_production_guard_fails_when_grid_has_overrides():
    with pytest.raises(SystemExit, match="overrides"):
        production_guard(
            {"overrides": ["federated.num_rounds=1"]},
            git_points_at=lambda: ["freeze-v1"],
            git_status_tracked=lambda: "",
            env={"HF_TOKEN": "x"},
        )


def test_production_guard_fails_dirty_or_missing_token():
    with pytest.raises(SystemExit, match="clean tracked"):
        production_guard(
            {},
            git_points_at=lambda: ["freeze-v1"],
            git_status_tracked=lambda: " M foo.py",
            env={"HF_TOKEN": "x"},
        )
    with pytest.raises(SystemExit, match="HF_TOKEN"):
        production_guard(
            {},
            git_points_at=lambda: ["freeze-v1"],
            git_status_tracked=lambda: "",
            env={},
        )


def test_results_key_normalizes_relative_absolute_and_workspace_paths():
    run_rel = "results/raw/vp_tl_fedit_a01/fedit/seed_2001_run7001/smoke/20260101_120000"
    ckpt_rel = f"{run_rel}/final_adapter_state.pt"
    ckpt_abs = f"/Users/me/proj/{ckpt_rel}"
    ckpt_workspace = f"/workspace/proj/{ckpt_rel}"
    assert _results_key(ckpt_rel) == ckpt_rel
    assert _results_key(ckpt_abs) == ckpt_rel
    assert _results_key(ckpt_workspace) == ckpt_rel
    run_dir = Path(f"/Users/me/proj/{run_rel}")
    for ckpt in (ckpt_rel, ckpt_abs, ckpt_workspace):
        assert _checkpoint_matches_holdout(run_dir, ckpt)


def test_retry_loop_skips_training_when_classify_returns_complete(tmp_path, monkeypatch):
    from scripts import run_grid as rg

    cells = enumerate_cells(load_grid(REPO / "grids" / "tl.yaml"))
    cell = next(
        c
        for c in cells
        if c.het == "a01" and c.method == "fedit" and c.data_seed == 2001 and c.run_seed == 7001
    )
    monkeypatch.setattr(rg, "REPO_ROOT", tmp_path)
    calls = {"train": 0}

    def fake_train(*args, **kwargs):
        calls["train"] += 1
        return ["train"]

    classify_calls = {"n": 0}

    def fake_classify(cell, expected_rounds=15):
        classify_calls["n"] += 1
        if classify_calls["n"] == 1:
            return "needs_holdout"
        return "complete"

    monkeypatch.setattr(rg, "train_cmd", fake_train)
    monkeypatch.setattr(rg, "classify_cell", fake_classify)
    monkeypatch.setattr(
        rg,
        "find_run_dir",
        lambda cell, prefer, expected_rounds=15: tmp_path / "run",
    )
    monkeypatch.setattr(
        rg,
        "_run_logged",
        lambda cmd, log_path, append=False: (0, "Output: results/raw/x\n", ""),
    )

    log_dir = tmp_path / "logs"
    jsonl_path = tmp_path / "launch.jsonl"
    status = run_one_cell(
        cell,
        device="cpu",
        grid_name="tl",
        shard=0,
        max_retries=1,
        holdout_only=False,
        dry_run=False,
        log_dir=log_dir,
        jsonl_path=jsonl_path,
    )
    assert status == "complete"
    assert calls["train"] == 0


def test_holdout_cmd_uses_per_cell_csv_when_workers_gt_one():
    cells = enumerate_cells(load_grid(REPO / "grids" / "tl.yaml"))
    cell = cells[0]
    run_dir = REPO / "results" / "raw" / "dummy"
    cmd = holdout_cmd(cell, run_dir, "cpu", "tl", 0, workers=2)
    assert "holdout_tl_shard0_" in cmd[-2]
    assert cell.cell_id in cmd[-2]


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
