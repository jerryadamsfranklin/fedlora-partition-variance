# STATUS

Last updated: 16 Sep 2026

Replace this file in the Claude Project whenever the state changes. Keep only one copy.

## Current phase

Phase C (partition preview): complete on branch phase-c. Awaiting review before fast-forward into main. Do not start Phase D until continue.

## Done

- Tag `ijacsa-fork-point` in the old repo (local folder `federated-lora-experiments`), commit 96c40f7040313b8cd5d3ef3ea8362e5ccbcab981
- Task 01 complete: v0-import (9cbc63e) verified clean; skeleton abc4d20; baseline tests db0a7c2 (28 passed)
- Phase B on main (2393d04..ec68b81), 55 tests passing
- Phase B full-diff review passed: label gate before proxy branch, fail-loud on missing category column, partition draw unchanged, Dolly held-out formatter matches training, run_meta provenance correct
- Phase B direct-to-main decision logged in DECISIONS.md (branch docs-phase-b-decision, da78869, fast-forwarded into main)
- Phase C: partition preview for seeds 2001 to 2010 at alpha 0.1; minimum active_clients=9; global hist 8 categories sum 3000; holdout index overlap PASS

## Next

1. Review Phase C report (partition_preview.txt, min active clients, global hist, holdout overlap); then fast-forward merge phase-c into main
2. Phase D on branch phase-d: Mac smoke tests; report must include run_grid.py source, docs/merged_configs.txt, and grid_status handling of orphan run folders
3. Phase E freeze only after B, C, D reviewed and run_grid.py plus merged configs approved

## Decisions made

- Venue: IJACSA, October issue (submit by 24 Sep); fall back to November if go/no-go fails on 21 Sep
- Two scales: TinyLlama-1.1B (primary) and LLaMA-3.2-3B (replication, subject to the Phase F timing gate)
- GPUs: Vast.ai, on-demand RTX 4090; A100 or L40S only if 3B does not fit
- Cursor runs one phase at a time; freeze-v1 only on explicit "freeze"; GPU renting and launches done by Jerry
- Phase B stays on main (no history rewrite). From Phase C: one branch per phase, fast-forward merge after review, never force-push
- B3 formatter test uses hard-coded strings copied from client.py (allowed by plan)

## Open items

- Attorney: does an IJACSA publication carry weight, given the publisher's history?
- Attorney: does IEEE Early Access with a DOI count as published for the OJ-CS paper?
- AI disclosure: choose the declaration version that matches actual use
- Private repo access for Vast instances: deploy key or fine-grained token (needed before Phase F)
- Overlap check (Phase M): set OLD to the local folder federated-lora-experiments
- Timing and peak-memory fields cover only the resumed segment for resumed runs; treat as partial in analysis
- partition_stats.json is written before training; crashed runs leave orphan folders (completeness keyed on results.json with 15 rounds)
- Review run_grid.py and docs/merged_configs.txt before freeze
- Local tooling: use .venv/bin/python; plain git commit via /usr/bin/git if the wrapper fails

## Run progress

| Grid | Complete | Failed | Total |
|---|---|---|---|
| tl | 0 | 0 | 75 |
| l3 | 0 | 0 | 45 |

## Measured constants (fill in during Phases D and F)

| Item | Value |
|---|---|
| TinyLlama per-client upload, FedIT / FLoRA | expected 9,011,200 bytes |
| TinyLlama per-client upload, FFA-LoRA | |
| LLaMA-3B per-client upload, FedIT / FLoRA | expected 9,175,040 bytes |
| LLaMA-3B per-client upload, FFA-LoRA | |
| TinyLlama minutes per run (4090) | |
| LLaMA-3B minutes per run, and GPU used | |
| Workers per GPU (TinyLlama) | |
