# STATUS

Last updated: 17 Sep 2026

Replace this file in the Claude Project whenever the state changes. Keep only one copy.

## Current phase

Phase F complete (gates passed). Phase G started: `tl` shards 0 and 1 on two RTX 4090s (`--workers 1`). Shard 2 and LLaMA grid not started yet. Freeze tag `freeze-v1` at 0812fcf.

## Done

- Tag `ijacsa-fork-point` in the old repo (local folder `federated-lora-experiments`), commit 96c40f7040313b8cd5d3ef3ea8362e5ccbcab981
- Task 01 complete: v0-import (9cbc63e) verified clean
- Phases B–E on main; `freeze-v1` at 0812fcf
- Phase F timing on Vast RTX 4090s: F1 29.3 min; F2 65.2 min / ~9 GB peak; F3 concurrency ratio 1.06× → workers 1; bytes match (TL 9011200, L3 9175040). Report: `docs/phase_f_report.md`
- Phase G launched: tl shard 0 (27 cells) and shard 1 (24 cells), `--production --workers 1`

## Next

1. Add Vast credits; keep both instances running; rent a third 4090 for `tl` shard 2
2. Sync results to Mac every few hours; monitor `grid_status.py`
3. After `tl` complete (or in parallel with spare GPUs), launch `grids/l3.yaml` on identical RTX 4090 `gpu_name`
4. Phase H verification when grids complete

## Decisions made

- Venue: IJACSA, October issue (submit by 24 Sep); fall back to November if go/no-go fails on 21 Sep
- Two scales: TinyLlama-1.1B and LLaMA-3.2-3B (F2 gate passed on 4090)
- GPUs: Vast.ai on-demand RTX 4090; identical GPU model within a grid
- Phase F: `--workers 1` for TinyLlama (F3 throughput 1.06× &lt; 1.6×)
- Freeze authorized 16 Sep 2026; freeze-v1 tagged

## Findings to carry into the paper

- Alpha 0.1 partitions: active clients 9 to 10; effective clients 7 to 10 (TinyLlama); 4 of 10 seeds have at least one zero-step client (seed 2008 has two)
- Zero-step clients hold at most 11 samples; 23 samples in total across seeds
- Discarded trailing samples per seed: 27 to 60 (TinyLlama), 41 to 104 (LLaMA)
- Client sizes range from 2 to 1218 samples
- client.py steps only on complete accumulation blocks (no drop_last)
- As implemented, FFA-LoRA uploads A and B and downloads B only; state this in the setup section
- RTX 4090 TinyLlama ~29 min/run; LLaMA-3.2-3B ~65 min/run; peak ~9 GB for 3B flora timing

## Open items

- Vast credits for full Phase G (~40 GPU-hours tl + ~51 l3 including holdout)
- Third 4090 for tl shard 2
- Attorney / AI disclosure / Phase M overlap path
- Held-out eval adds ~2–3 GPU-min per production cell

## Run progress

| Grid | Complete | Failed | Total | Notes |
|---|---|---|---|---|
| tl | (in progress) | 0 | 75 | shards 0+1 running; shard 2 pending |
| l3 | 0 | 0 | 45 | after tl capacity / third+ GPUs |

## Measured constants

| Item | Value |
|---|---|
| TinyLlama per-client upload, FedIT / FLoRA | 9,011,200 bytes (Phase D + F1 confirm) |
| TinyLlama per-client upload, FFA-LoRA | 9,011,200 upload; 3,244,032 download (Phase D) |
| LLaMA-3B per-client upload, FedIT / FLoRA | 9,175,040 bytes (measured F2) |
| TinyLlama minutes per run (4090) | ~29.3 train-only (F1); use ~32 with holdout |
| LLaMA-3B minutes per run, and GPU used | ~65.2 train-only (F2) on RTX 4090; peak ~9 GB |
| Workers per GPU (TinyLlama) | **1** (F3 gate) |
| Mac smoke cell (1 round, 300 samples, incl. holdout) | about 280 s; holdout-only about 136 s |
