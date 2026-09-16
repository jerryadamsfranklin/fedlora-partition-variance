# STATUS

Last updated: 16 Sep 2026

Replace this file in the Claude Project whenever the state changes. Keep only one copy.

## Current phase

Phase B (code changes): complete. Stopped for review before Phase C.

## Done

- Tag `ijacsa-fork-point` in the old repo (local folder `federated-lora-experiments`), commit 96c40f7040313b8cd5d3ef3ea8362e5ccbcab981, matches origin/main
- Task 01 complete after reset: three checks passed (file list identical, hash check clean, v0-import is root commit naming the fork SHA)
- New repo history: 9cbc63e v0-import (unmodified import), abc4d20 skeleton, db0a7c2 baseline test count; main pushed to origin
- Docs: IMPLEMENTATION_PLAN.md and STATUS.md committed under docs/
- Phase B0 to B6 complete (one commit each; pytest after each). Final suite: 55 passed

## Next

1. Review Phase B report, especially diffs to `scripts/run_experiment.py` and `scripts/evaluate_instruction_holdout.py`
2. Reply "continue" only after that review to start Phase C (partition preview)
3. Phase D Mac smoke tests; Phase E freeze only after B, C, D reviewed

## Decisions made

- Venue: IJACSA, October issue (submit by 24 Sep); fall back to November if go/no-go fails on 21 Sep
- Two scales: TinyLlama-1.1B (primary) and LLaMA-3.2-3B (replication, subject to the Phase F timing gate)
- GPUs: Vast.ai, on-demand RTX 4090; A100 or L40S only if 3B does not fit
- Cursor runs one phase at a time and stops for review; freeze-v1 tag only on explicit "freeze"; GPU renting and launches done by Jerry
- Old-repo local path for Phase M: `federated-lora-experiments`

## Open items

- Attorney: does an IJACSA publication carry weight, given the publisher's history?
- Attorney: does IEEE Early Access with a DOI count as published for the OJ-CS paper?
- AI disclosure: choose the declaration version that matches actual use
- Private repo access for Vast instances: deploy key or fine-grained token (needed before Phase F)
- Overlap check (Phase M): set OLD to the local folder federated-lora-experiments

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
