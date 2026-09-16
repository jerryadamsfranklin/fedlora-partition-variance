"""Tests for partition-variance study configs."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.run_experiment import load_config

REPO = Path(__file__).resolve().parents[1]
VP = REPO / "config" / "vp"

METHODS = ("fedit", "ffa_lora", "flora")
MODELS = {
    "tl": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    "l3": "meta-llama/Llama-3.2-3B",
}
HETS = ("a01", "iid")


@pytest.mark.parametrize("model_key", list(MODELS))
@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize("het", HETS)
def test_vp_merged_config(model_key: str, method: str, het: str):
    path = VP / f"vp_{model_key}_{method}_{het}.yaml"
    assert path.is_file(), f"missing {path}"
    cfg = load_config(str(path))
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
    else:
        assert cfg["data"]["partition_method"] == "iid"
