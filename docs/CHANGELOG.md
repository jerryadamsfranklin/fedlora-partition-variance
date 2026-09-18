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
- C addendum: effective clients and discarded trailing samples (optimizer steps
  only on complete accumulation blocks); pre-registered in I6 and limitations.
- D: Mac smoke tests (docs/smoke_report.md); classify orphan run folders in
  run_grid/grid_status; TinyLlama per-client upload 9,011,200 bytes (FedIT/FLoRA;
  FFA upload same, download B-only 3,244,032).
- D fix: shard by (het, data_seed, run_seed) group so all methods share a GPU;
  tl counts 27/24/24 and l3 15/15/15 for three shards.
- G/H: LLaMA holdout eval uses float16 on CUDA and frees the tuned model before
  loading the base (sequential load); TinyLlama holdouts remain float32.
- H: `scripts/verify_varpart.py` (V1-V11); V4 scoped by het; V7 records eval_dtype;
  V10 resume/retry census; V11 eval-script provenance vs freeze-v2.
- H close: float32 spot-check evidence committed; Phase K audit dropped in DECISIONS.
- I: `scripts/analysis/build_runs_table.py` and `analyze_variance.py` (I0 to I6);
  outputs under `analysis/*.csv`.
- I addendum: pair-level flip table (`rank_flip_pairs.csv`) and observed-gap power rows.
- J: `make_figures.py` (Figs 1 to 3, pair panel on Fig 2) and `make_tables.py` (Tabs 1 to 3).
- J fix: figures at 505 pt full width with >=8 pt fonts; Tab1 LoRA alpha notation;
  Tab2 design p/m/r and no-truncation note; I7 claim wording for l3 near-tie.
- L: draft Setup section (`manuscript/sections/03_setup.tex`).
- N1-N4: TinyLlama alpha 0.5 configs (15 total); grids `tl_a05` and `l3_ext`;
  ANALYSIS_PLAN I8 to I10; V12 training-path freeze check; tag `freeze-v3`.
  Holdout eval restored to the freeze-v2 blob so V12 can pin prod_v2 eval.
- N5 runbook: `docs/PHASE_N_RUNBOOK.md` (RTX 4090 name gate, stagger, tl then l3).
