# STATUS

Last updated: 16 Sep 2026

Replace this file in the Claude Project whenever the state changes. Keep only one copy.

## Current phase

Phase D (Mac smoke tests): complete on branch phase-d. Awaiting review. Do not merge and do not freeze.

## Done

- Tag `ijacsa-fork-point` in the old repo (local folder `federated-lora-experiments`), commit 96c40f7040313b8cd5d3ef3ea8362e5ccbcab981
- Task 01 complete: v0-import (9cbc63e) verified clean; skeleton abc4d20; baseline tests db0a7c2 (28 passed)
- Phase B on main (2393d04..ec68b81), full-diff review passed; docs branch merged (da78869)
- Phase C + addendum fast-forwarded into main (ab4e69e)
- Phase D smokes on MPS: three methods (seed 2001, 300 samples, 1 round) + seed-2008 full FedIT 1-round; holdout JSON Dolly + v2-dolly-context; orphan classification added; smoke raw deleted

## Next

1. Review Phase D report (smoke_report.md, run_grid.py, grid_status.py, merged_configs.txt, orphan handling, dry-run shards)
2. After approval, fast-forward phase-d into main
3. Confirm what any started GPU instance is running; production is not allowed before freeze-v1
4. Phase E freeze only after Phase D and the launcher review pass

## Decisions made

- Venue: IJACSA, October issue (submit by 24 Sep); fall back to November if go/no-go fails on 21 Sep
- Two scales: TinyLlama-1.1B (primary) and LLaMA-3.2-3B (replication, subject to the Phase F timing gate)
- GPUs: Vast.ai, on-demand RTX 4090; A100 or L40S only if 3B does not fit
- Cursor runs one phase at a time; freeze-v1 only on explicit "freeze"; GPU renting and launches done by Jerry
- Phase B stays on main (no history rewrite). From Phase C: one branch per phase, fast-forward merge after review, never force-push
- B3 formatter test uses hard-coded strings copied from client.py (allowed by plan)
- Pre-freeze plan amendment: effective clients and discarded trailing samples added as pre-registered partition statistics; accumulation-block limitation added to the paper

## Findings to carry into the paper

- Alpha 0.1 partitions (seeds 2001-2010): active clients 9 to 10; effective clients 7 to 10 (TinyLlama) with 4 of 10 seeds having at least one zero-step client (seed 2008 has two)
- Zero-step clients hold at most 11 samples (under 0.4% weight each; 23 samples in total across seeds)
- Discarded trailing samples per seed: 27 to 60 (TinyLlama, 0.9% to 2.0%), 41 to 104 (LLaMA, up to 3.5%)
- Client sizes range from 2 to 1218 samples across seeds
- client.py steps only on complete accumulation blocks (no drop_last)
- TinyLlama per-client upload: 9,011,200 bytes (FedIT/FLoRA); FFA-LoRA upload same, download/broadcast 3,244,032 bytes

## Open items

- GPU instance started before freeze: identify what it is running (no Vast host/check commands available in this Cursor session)
- Attorney: does an IJACSA publication carry weight, given the publisher's history?
- Attorney: does IEEE Early Access with a DOI count as published for the OJ-CS paper?
- AI disclosure: choose the declaration version that matches actual use
- Private repo access for Vast instances: deploy key or fine-grained token (needed before Phase F)
- Overlap check (Phase M): set OLD to the local folder federated-lora-experiments
- Timing and peak-memory fields cover only the resumed segment for resumed runs; treat as partial in analysis
- partition_stats.json is written before training; crashed runs leave orphan folders (now classified as orphan by grid_status)
- Local tooling: use .venv/bin/python; plain git commit via /usr/bin/git if the wrapper fails

## Run progress

| Grid | Complete | Failed | Total |
|---|---|---|---|
| tl | 0 | 0 | 75 |
| l3 | 0 | 0 | 45 |

## Measured constants (fill in during Phases D and F)

| Item | Value |
|---|---|
| TinyLlama per-client upload, FedIT / FLoRA | 9,011,200 bytes (measured, smoke) |
| TinyLlama per-client upload, FFA-LoRA | 9,011,200 bytes upload; 3,244,032 bytes download/broadcast |
| LLaMA-3B per-client upload, FedIT / FLoRA | expected 9,175,040 bytes |
| LLaMA-3B per-client upload, FFA-LoRA | |
| TinyLlama minutes per run (4090) | |
| LLaMA-3B minutes per run, and GPU used | |
| Workers per GPU (TinyLlama) | |
