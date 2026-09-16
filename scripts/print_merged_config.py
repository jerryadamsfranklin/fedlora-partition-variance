#!/usr/bin/env python3
"""Load a config through run_experiment.load_config and print the merged result."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.run_experiment import load_config  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Print merged YAML config")
    parser.add_argument("config", nargs="+", help="Config path(s) relative to repo root")
    args = parser.parse_args()
    for cfg in args.config:
        path = cfg if os.path.isabs(cfg) else str(REPO_ROOT / cfg)
        merged = load_config(path)
        print(f"===== {cfg} =====")
        yaml.safe_dump(merged, sys.stdout, sort_keys=False)
        print()


if __name__ == "__main__":
    main()
