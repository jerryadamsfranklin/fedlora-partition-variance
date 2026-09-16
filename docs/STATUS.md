# STATUS

Last updated: 16 Sep 2026

Replace this file in the Claude Project whenever the state changes. Keep only one copy.

## Current phase

Phase C addendum complete on branch phase-c. Awaiting review before fast-forward into main. Do not start Phase D until continue.

## Done

- Tag `ijacsa-fork-point` in the old repo (local folder `federated-lora-experiments`), commit 96c40f7040313b8cd5d3ef3ea8362e5ccbcab981
- Task 01 complete: v0-import (9cbc63e) verified clean; skeleton abc4d20; baseline tests db0a7c2 (28 passed)
- Phase B on main (2393d04..ec68b81), 55 tests passing; full-diff review passed
- Docs branch docs-phase-b-decision fast-forwarded into main (ec68b81..da78869)
- Phase C checks: Dolly train[0:3000] has 8 categories summing to 3000; held-out overlap 0; minimum active clients 9 (seeds 2005, 2008), all other seeds 10
- Phase C addendum: effective clients and discarded trailing samples reported; DECISIONS.md and plan I6/limitations updated; seed 2008 has 2 zero-step active clients on both models

## Next

1. Review Phase C addendum report, then fast-forward phase-c into main
2. Phase D on branch phase-d: Mac smoke tests; report must include run_grid.py source, docs/merged_configs.txt, and grid_status handling of orphan run folders
3. Phase E freeze only after B, C, D reviewed and run_grid.py plus merged configs approved

## Decisions made

- Venue: IJACSA, October issue (submit by 24 Sep); fall back to November if go/no-go fails on 21 Sep
- Two scales: TinyLlama-1.1B (primary) and LLaMA-3.2-3B (replication, subject to the Phase F timing gate)
- GPUs: Vast.ai, on-demand RTX 4090; A100 or L40S only if 3B does not fit
- Cursor runs one phase at a time; freeze-v1 only on explicit "freeze"; GPU renting and launches done by Jerry
- Phase B stays on main (no history rewrite). From Phase C: one branch per phase, fast-forward merge after review, never force-push
- B3 formatter test uses hard-coded strings copied from client.py (allowed by plan)
- Pre-freeze plan amendment: add effective clients (at least one optimizer step) and discarded trailing samples as pre-registered partition statistics; add the accumulation-block limitation to the paper

## Findings to carry into the paper

- Active clients vary only between 9 and 10 across the 10 alpha 0.1 seeds, so active-client count has little explanatory range (RQ4) and communication totals differ for only 2 partitions
- client.py steps only on complete accumulation blocks (no drop_last): TinyLlama clients with n<=12 and LLaMA clients with n<=14 upload the unchanged global adapter; trailing partial blocks are discarded
- Seed 2008 has 2 zero-step active clients under both TinyLlama (4x4) and LLaMA (2x8); seeds 2001, 2003, 2009 have 1 each; effective federation size therefore varies more than active-client count

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
