# Changelog

All changes relative to the imported code, newest last.

Baseline test count at v0-import: 28 passed

- B1: write `partition_stats.json` after partitioning; fail loudly when
  `data.require_label_column` is true and the label column is missing
  (`resolve_label_source`); length-proxy fallback unchanged when not required.
- B2: `run_meta.json` records `git_dirty_tracked`, `git_describe`, `hardware`,
  and `wall_clock_s` after training; legacy `git_dirty` unchanged.
- B3: held-out Dolly formatter includes `### Context:` when present (matches
  training); JSON records `formatter_version=v2-dolly-context` and `eval_dtype`.
  Formatter test uses hard-coded strings from `client.py` (no FederatedClient
  construction).
- B4: add `scripts/make_vp_configs.py` (12 `config/vp/*.yaml`),
  `scripts/print_merged_config.py`, and `docs/merged_configs.txt`; list merge
  replaces base `target_modules` with q_proj/v_proj.
- B5: grids `grids/tl.yaml` and `grids/l3.yaml`, launcher `scripts/run_grid.py`,
  status tool `scripts/grid_status.py` (enumerate, shard, production guard).
- B6: add `scripts/vast_setup.sh` for Vast.ai instance bootstrap (clone freeze-v1,
  deps, HF login, prefetch, pytest).
- C: `scripts/inspect_partitions.py` and `docs/partition_preview.txt` for Dolly
  train[0:3000] label_skew alpha=0.1, seeds 2001 to 2010.
