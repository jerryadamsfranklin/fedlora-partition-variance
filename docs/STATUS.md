# STATUS

Last updated: 16 Sep 2026

Replace this file in the Claude Project whenever the state changes. Keep only one copy.

## Current phase

Phase D complete pending commit and full test run. Phase E (pre-registration and freeze-v1) authorized; Cursor to execute after cleanup, full pytest, and fast-forward merge.

## Done

- Tag `ijacsa-fork-point` in the old repo (local folder `federated-lora-experiments`), commit 96c40f7040313b8cd5d3ef3ea8362e5ccbcab981
- Task 01 complete: v0-import (9cbc63e) verified clean
- Phase B on main, full-diff review passed
- Phase C and addendum on main (ab4e69e)
- Phase D smoke checks passed; group-level sharding; merged configs, grid_status.py, orphan handling approved
- Launcher fixes F1 to F5 implemented; end-to-end smoke grid on Mac passed: E1 (3 complete, attempt 1, one folder each), E2 (rerun trains nothing), E3 (holdout-only rerun in same folder), E4 (status correct at a different absolute path); tests/test_run_grid.py 19 passed

## Next

1. Cursor: delete smoke outputs, full pytest (>= 69), commit and push phase-d, fast-forward into main
2. Phase E: docs/ANALYSIS_PLAN.md from current Phase I (with I0 and amended I6), Phase J, I7; tag freeze-v1; record SHA
3. Set up repo access for Vast (deploy key or read-only token)
4. Phase F timing on Vast (same GPU model across instances of a grid)
5. Confirm what the earlier Vast instance is running; stop it unless it is a timing run

## Decisions made

- Venue: IJACSA, October issue (submit by 24 Sep); fall back to November if go/no-go fails on 21 Sep
- Two scales: TinyLlama-1.1B (primary) and LLaMA-3.2-3B (replication, subject to the Phase F timing gate)
- GPUs: Vast.ai, on-demand RTX 4090; A100 or L40S only if 3B does not fit; identical GPU model within a grid
- Cursor runs one phase at a time; GPU renting and launches done by Jerry
- Phase B stays on main (no history rewrite). From Phase C: one branch per phase, fast-forward merge after review, never force-push
- Pre-freeze amendments: effective clients and discarded trailing samples pre-registered; whole-group sharding; V2 requires identical gpu_name within a grid; communication compared only within method
- Pre-freeze launcher fixes: path normalization, no retraining of complete cells, freeze tag check via --points-at, per-cell CSV with workers>1, smoke-grid support; run table built from holdout JSON only; jsonl attempt-0 lines are skip records and ignored
- Freeze authorized 16 Sep 2026

## Findings to carry into the paper

- Alpha 0.1 partitions: active clients 9 to 10; effective clients 7 to 10 (TinyLlama); 4 of 10 seeds have at least one zero-step client (seed 2008 has two)
- Zero-step clients hold at most 11 samples; 23 samples in total across seeds
- Discarded trailing samples per seed: 27 to 60 (TinyLlama), 41 to 104 (LLaMA)
- Client sizes range from 2 to 1218 samples
- client.py steps only on complete accumulation blocks (no drop_last)
- As implemented, FFA-LoRA uploads A and B and downloads B only; state this in the setup section

## Open items

- Vast instance started before freeze: identify what it is running; stop unless timing
- Attorney: does an IJACSA publication carry weight, given the publisher's history?
- Attorney: does IEEE Early Access with a DOI count as published for the OJ-CS paper?
- AI disclosure: choose the declaration version that matches actual use
- Private repo access for Vast instances: deploy key or fine-grained token (needed before Phase F)
- Overlap check (Phase M): set OLD to the local folder federated-lora-experiments
- Timing and peak-memory fields cover only the resumed segment for resumed runs; treat as partial in analysis
- Held-out eval recomputes base loss per cell (about half of Mac smoke time); include about 2 to 3 GPU-minutes per cell in Phase G sizing
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
| Mac smoke cell (1 round, 300 samples, incl. holdout) | about 280 s; holdout-only about 136 s |
