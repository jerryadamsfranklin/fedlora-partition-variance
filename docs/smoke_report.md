# Smoke report (Phase D)

Date: 16 Sep 2026  
Branch: `phase-d`  
Device: Apple M4 Pro, MPS  
Model: TinyLlama/TinyLlama-1.1B-Chat-v1.0

## Runs

| Run | Config | data_seed | max_samples | rounds | output |
|---|---|---|---|---|---|
| FedIT smoke | vp_tl_fedit_a01 | 2001 | 300 | 1 | `results/raw/vp_tl_fedit_a01/fedit/seed_2001_run7001/smoke/20260916_020603` |
| FFA-LoRA smoke | vp_tl_ffa_lora_a01 | 2001 | 300 | 1 | `results/raw/vp_tl_ffa_lora_a01/ffa_lora/seed_2001_run7001/smoke/20260916_021159` |
| FLoRA smoke | vp_tl_flora_a01 | 2001 | 300 | 1 | `results/raw/vp_tl_flora_a01/flora/seed_2001_run7001/smoke/20260916_021423` |
| FedIT zero-step exercise | vp_tl_fedit_a01 | 2008 | 3000 (full) | 1 | `results/raw/vp_tl_fedit_a01/fedit/seed_2008_run7001/smoke/20260916_021833` |
| Holdout | evaluate_instruction_holdout | start 3000, n=20 | | | under `results/downstream_instruction/.../instruction_holdout.json` |

Smoke `results/raw` trees were deleted after recording (plan preference).

## Acceptance table

| Check | Result | Evidence |
|---|---|---|
| Label source | PASS | All three smokes: `label_source=column`, `label_column=category` |
| No proxy | PASS | No `instruction-length buckets` in `logs/smoke/*.log` |
| Empty clients | PASS | All three methods finished with `active_clients=9` (one empty client at max_samples=300) |
| Bytes | PASS | Round-1 `upload_mb=77.34375` with active=9 => **9,011,200 bytes/client** for FedIT and FLoRA (matches expected). FFA-LoRA **upload** also 9,011,200 bytes/client; **download** is B-only at 3,244,032 bytes/client (`broadcast_bytes_per_client`) |
| Held-out | PASS | JSON: `dataset=databricks/databricks-dolly-15k`, `formatter_version=v2-dolly-context`, finite losses (tuned 2.0752, base 2.2109) |
| Provenance | PASS | `run_meta.json` has `git_dirty_tracked`, `hardware` (`mps: true`), `wall_clock_s` |
| Seed-2008 sizes | PASS | `client_sizes` exact match to Phase C preview `[2, 409, 0, 308, 327, 11, 229, 825, 758, 131]` |
| Seed-2008 upload | PASS | active=9, `upload_mb=77.34375` = 9 x 9,011,200 bytes (zero-step clients still upload) |

## Measured TinyLlama per-client upload constants

| Method | Per-client upload (bytes) | Notes |
|---|---|---|
| FedIT | 9,011,200 | matches expected |
| FLoRA | 9,011,200 | matches expected |
| FFA-LoRA | 9,011,200 upload; 3,244,032 download/broadcast | upload still full A+B in this codebase |

## Orphan-folder handling

`classify_cell` now returns `orphan` when a timestamp dir has `partition_stats.json` but no complete `results.json` and no `checkpoints/latest.pt`. `grid_status.py` prints `orphan=` in the summary.

Synthetic tree demo: 74 fresh, 1 orphan (`tl_fedit_a01_d2001_r7001`).

## Dry-run sharding (`grids/tl.yaml`, `--num-shards 3`)

| Shard | Cells |
|---|---|
| 0 | 25 |
| 1 | 25 |
| 2 | 25 |
| Total | 75 |

## Notes

- Holdout console banner briefly printed a default dataset name in one path; the written JSON correctly records Dolly.
- Smoke outputs under `results/raw/**/smoke/` deleted after this report.
