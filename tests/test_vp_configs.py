"""Tests for partition-variance study configs."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
VP = REPO / "config" / "vp"

METHODS = ("fedit", "ffa_lora", "flora")
MODELS = {
    "tl": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    "l3": "meta-llama/Llama-3.2-3B",
}
# 15 files: tl × 3 methods × {a01,a05,iid} + l3 × 3 methods × {a01,iid}
CONFIGS = [
    ("tl", method, het)
    for method in METHODS
    for het in ("a01", "a05", "iid")
] + [
    ("l3", method, het)
    for method in METHODS
    for het in ("a01", "iid")
]


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(base)
    for key, val in override.items():
        if isinstance(val, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], val)
        else:
            out[key] = val
    return out


def load_config(path: str) -> Dict[str, Any]:
    """YAML `_inherit` merge without importing run_experiment (avoids torch)."""
    abs_path = os.path.abspath(path)
    with open(abs_path, encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}
    inherit = config.pop("_inherit", None)
    if inherit:
        base = load_config(os.path.join(os.path.dirname(abs_path), inherit))
        config = _deep_merge(base, config)
    return config


def test_exactly_fifteen_vp_configs():
    assert len(CONFIGS) == 15
    paths = sorted(p.name for p in VP.glob("vp_*.yaml"))
    expected = sorted(f"vp_{m}_{meth}_{h}.yaml" for m, meth, h in CONFIGS)
    assert paths == expected


@pytest.mark.parametrize("model_key,method,het", CONFIGS)
def test_vp_merged_config(model_key: str, method: str, het: str):
    path = VP / f"vp_{model_key}_{method}_{het}.yaml"
    assert path.is_file(), f"missing {path}"
    cfg = load_config(str(path))
    assert cfg["experiment"]["name"] == f"vp_{model_key}_{method}_{het}"
    assert cfg["lora"]["target_modules"] == ["q_proj", "v_proj"]
    assert cfg["model"]["name"] == MODELS[model_key]
    assert cfg["federated"]["num_rounds"] == 15
    assert cfg["federated"]["num_clients"] == 10
    assert cfg["federated"]["clients_per_round"] == 10
    assert cfg["federated"]["aggregation_method"] == method
    assert cfg["data"]["dataset_name"] == "databricks/databricks-dolly-15k"
    assert cfg["data"]["max_samples"] == 3000
    assert cfg["data"]["label_column"] == "category"
    assert cfg["data"]["require_label_column"] is True
    if het == "a01":
        assert cfg["data"]["partition_method"] == "label_skew"
        assert float(cfg["data"]["partition_alpha"]) == 0.1
    elif het == "a05":
        assert cfg["data"]["partition_method"] == "label_skew"
        assert float(cfg["data"]["partition_alpha"]) == 0.5
    else:
        assert cfg["data"]["partition_method"] == "iid"
