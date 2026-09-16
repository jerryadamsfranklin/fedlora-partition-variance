#!/usr/bin/env python3
"""Generate partition-variance study configs under config/vp/."""

from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "config" / "vp"

METHODS = ("fedit", "ffa_lora", "flora")
MODELS = {
    "tl": {
        "inherit": "../base_config_4layers.yaml",
        "label": "TinyLlama-1.1B",
    },
    "l3": {
        "inherit": "../base_config_llama3_3b.yaml",
        "label": "LLaMA-3.2-3B",
    },
}
HETS = {
    "a01": {
        "partition_method": "label_skew",
        "partition_alpha": 0.1,
        "het_label": "alpha0.1",
    },
    "iid": {
        "partition_method": "iid",
        "partition_alpha": None,
        "het_label": "iid",
    },
}


def render(model_key: str, method: str, het_key: str) -> str:
    model = MODELS[model_key]
    het = HETS[het_key]
    lines = [
        f'_inherit: {model["inherit"]}',
        "",
        "experiment:",
        f'  name: "vp_{model_key}_{method}_{het_key}"',
        (
            f'  description: "Partition-variance study | {method} | '
            f'{model["label"]} | Dolly-3k | {het["het_label"]}"'
        ),
        "",
        "lora:",
        "  r: 16",
        "  lora_alpha: 32",
        "  lora_dropout: 0.1",
        '  target_modules: ["q_proj", "v_proj"]',
        "",
        "federated:",
        f'  aggregation_method: "{method}"',
        "  num_rounds: 15",
        "  num_clients: 10",
        "  clients_per_round: 10",
        "",
        "data:",
        '  dataset_name: "databricks/databricks-dolly-15k"',
        '  dataset_split: "train"',
        "  max_samples: 3000",
        f'  partition_method: "{het["partition_method"]}"',
    ]
    if het["partition_alpha"] is not None:
        lines.append(f'  partition_alpha: {het["partition_alpha"]}')
    lines.extend(
        [
            '  label_column: "category"',
            "  require_label_column: true",
            "  eval_split: null",
            "  eval_samples: 300",
            "",
            "checkpointing:",
            "  save_every: 5",
            "  keep_last_n: 1",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for model_key in MODELS:
        for method in METHODS:
            for het_key in HETS:
                name = f"vp_{model_key}_{method}_{het_key}.yaml"
                path = OUT_DIR / name
                path.write_text(render(model_key, method, het_key), encoding="utf-8")
                written.append(path.relative_to(REPO_ROOT).as_posix())
    print(f"Wrote {len(written)} configs:")
    for p in written:
        print(f"  {p}")


if __name__ == "__main__":
    main()
