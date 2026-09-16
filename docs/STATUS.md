# STATUS

Last updated: 16 Sep 2026

Replace this file in the Claude Project whenever the state changes. Keep only one copy.

## Current phase

Phase D (Mac smoke tests): checks passed on phase-d (0503fca, 59 tests). Blocking fix in progress: group-level sharding. Launcher source review pending. No freeze-v1.

## Done

- Tag `ijacsa-fork-point` in the old repo (local folder `federated-lora-experiments`), commit 96c40f7040313b8cd5d3ef3ea8362e5ccbcab981
- Task 01 complete: v0-import (9cbc63e) verified clean
- Phase B on main, full-diff review passed
- Phase C and addendum approved and fast-forwarded into main (da78869..ab4e69e)
- Phase D smoke checks passed: category label source, no length proxy, empty clients handled for all methods, held-out uses Dolly with v2-dolly-context, provenance fields present, seed 2008 sizes match preview, seed 2008 upload equals 9 x 9,011,200 B
- Orphan folders reported separately by grid_status.py

## Next

1. Phase D fix on phase-d: shard by (het, data_seed, run_seed) group; tests for shard coverage, same-shard groups, per-shard counts (tl 27/24/24, l3 15/15/15); plan B5 and V2 updated; two DECISIONS.md entries
2. Upload phase_d_review.zip; review run_grid.py, grid_status.py, merged_configs.txt
3. Fast-forward phase-d into main, then Phase E (pre-registration and freeze-v1) on explicit "freeze"
4. Confirm what the started Vast instance is running; only timing runs allowed before freeze

## Decisions made

- Venue: IJACSA, October issue (submit by 24 Sep); fall back to November if go/no-go fails on 21 Sep
- Two scales: TinyLlama-1.1B (primary) and LLaMA-3.2-3B (replication, subject to the Phase F timing gate)
- GPUs: Vast.ai, on-demand RTX 4090; A100 or L40S only if 3B does not fit
- Cursor runs one phase at a time; freeze-v1 only on explicit "freeze"; GPU renting and launches done by Jerry
- Phase B stays on main (no history rewrite). From Phase C: one branch per phase, fast-forward merge after review, never force-push
- Pre-freeze amendment: effective clients and discarded trailing samples are pre-registered partition statistics
- Pre-freeze amendment: shard whole (het, data_seed, run_seed) groups so all methods of a group share a GPU; V2 requires identical gpu_name within a grid
- Communication compared only within method across partitions; methods not ranked by bytes

## Findings to carry into the paper

- Alpha 0.1 partitions: active clients 9 to 10; effective clients 7 to 10 (TinyLlama); 4 of 10 seeds have at least one zero-step client (seed 2008 has two)
- Zero-step clients hold at most 11 samples; 23 samples in total across seeds
- Discarded trailing samples per seed: 27 to 60 (TinyLlama), 41 to 104 (LLaMA)
- Client sizes range from 2 to 1218 samples
- client.py steps only on complete accumulation blocks (no drop_last)
- As implemented, FFA-LoRA uploads A and B and downloads B only; state this in the setup section

## Open items

- Vast instance started before freeze: identify what it is running
- Attorney: does an IJACSA publication carry weight, given the publisher's history?
- Attorney: does IEEE Early Access with a DOI count as published for the OJ-CS paper?
- AI disclosure: choose the declaration version that matches actual use
- Private repo access for Vast instances: deploy key or fine-grained token (needed before Phase F)
- Overlap check (Phase M): set OLD to the local folder federated-lora-experiments
- Timing and peak-memory fields cover only the resumed segment for resumed runs; treat as partial in analysis
- Local tooling: use .venv/bin/python; plain git commit via /usr/bin/git if the wrapper fails

## Run progress

| Grid | Complete | Failed | Total |
|---|---|---|---|
| tl | 0 | 0 | 75 |
| l3 | 0 | 0 | 45 |

## Measured constants (fill in during Phases D and F)

| Item | Value |
|---|---|
| TinyLlama per-client upload, FedIT / FLoRA | 9,011,200 bytes (measured, Phase D) |
| TinyLlama per-client upload, FFA-LoRA | 9,011,200 bytes upload; 3,244,032 bytes download (measured, Phase D) |
| LLaMA-3B per-client upload, FedIT / FLoRA | expected 9,175,040 bytes |
| LLaMA-3B per-client upload, FFA-LoRA | |
| TinyLlama minutes per run (4090) | |
| LLaMA-3B minutes per run, and GPU used | |
| Workers per GPU (TinyLlama) | |
