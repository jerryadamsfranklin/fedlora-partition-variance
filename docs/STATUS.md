# STATUS

Last updated: 16 Sep 2026

Replace this file in the Claude Project whenever the state changes. Keep only one copy.

## Current phase

Phase B (code changes): implemented and pushed (main at ec68b81, 55 tests passing). Awaiting full-diff review before Phase C.

## Done

- Tag `ijacsa-fork-point` in the old repo (local folder `federated-lora-experiments`), commit 96c40f7040313b8cd5d3ef3ea8362e5ccbcab981
- Task 01 complete: v0-import (9cbc63e) verified clean; skeleton abc4d20; baseline tests db0a7c2 (28 passed)
- Phase B commits on main: 2393d04 plan/status, 27a0b3a B0, 97d6782 B1, 0132f29 B2, ef334ac B3, fd9bf6d B4, 5ce965b B5, 32ee5c4 B6, ec68b81 status
- Partial review of B1/B2/B3: label gate precedes proxy branch; Dolly formatter matches client.py; run_meta written after training

## Next

1. Full un-elided diff of run_experiment.py, evaluate_instruction_holdout.py, partition_stats.py, and related tests reviewed in the Claude Project
2. Log the Phase B direct-to-main decision in DECISIONS.md
3. Phase C on branch phase-c (partition preview), then Phase D on branch phase-d (Mac smoke tests); fast-forward merge after each review
4. Phase E freeze only after B, C, D reviewed

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
