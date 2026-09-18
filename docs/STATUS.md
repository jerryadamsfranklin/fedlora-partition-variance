# STATUS

Last updated: 18 Sep 2026

Replace this file in the Claude Project whenever the state changes. Keep only one copy.

## Current phase

**Phase G complete.** Production grids closed: TinyLlama **75/75**, LLaMA-3.2-3B **45/45** (`grid_status.py` on Mac after final M3 sync). Freeze tag `freeze-v1` at `0812fcf`. Report: `docs/phase_g_report.md`.

## Done

- Tag `ijacsa-fork-point` in the old repo (local folder `federated-lora-experiments`), commit 96c40f7040313b8cd5d3ef3ea8362e5ccbcab981
- Task 01 complete: v0-import (9cbc63e) verified clean
- Phases B–E on main; `freeze-v1` at 0812fcf
- Phase F timing on Vast RTX 4090s: F1 29.3 min; F2 65.2 min / ~9 GB peak; F3 concurrency ratio 1.06× → workers 1; bytes match (TL 9011200, L3 9175040). Report: `docs/phase_f_report.md`
- Phase G production: tl 75 + l3 45 on 3× RTX 4090 (`--production --workers 1`); all `prod_v1`; Dolly holdouts present. Report: `docs/phase_g_report.md`

## Next

1. Phase H: implement and run `scripts/verify_varpart.py` (V1–V9); must exit 0
2. Phase I analysis (pre-registered) only after H passes
3. Destroy remaining Vast instance (M3 `1.193.139.139:39647`) after any personal backup sync
4. Phase J–M per plan (figures, lit audit, manuscript)

## Decisions made

- Venue: IJACSA, October issue (submit by 24 Sep); fall back to November if go/no-go fails on 21 Sep
- Two scales: TinyLlama-1.1B and LLaMA-3.2-3B (F2 gate passed on 4090)
- GPUs: Vast.ai on-demand RTX 4090; identical GPU model within a grid
- Phase F: `--workers 1` for TinyLlama (F3 throughput 1.06× &lt; 1.6×)
- Freeze authorized 16 Sep 2026; freeze-v1 tagged
- L3 holdout eval uses float16 (and sequential model load) to fit 24 GB; training provenance remained freeze-v1 / dirty=false (see phase_g_report)

## Findings to carry into the paper

- Alpha 0.1 partitions: active clients 9 to 10; effective clients 7 to 10 (TinyLlama); 4 of 10 seeds have at least one zero-step client (seed 2008 has two)
- Zero-step clients hold at most 11 samples; 23 samples in total across seeds
- Discarded trailing samples per seed: 27 to 60 (TinyLlama), 41 to 104 (LLaMA)
- Client sizes range from 2 to 1218 samples
- client.py steps only on complete accumulation blocks (no drop_last)
- As implemented, FFA-LoRA uploads A and B and downloads B only; state this in the setup section
- RTX 4090 TinyLlama ~29 min/run; LLaMA-3.2-3B ~65 min/run; peak ~9 GB for 3B flora timing
- Production medians: tl wall ~27 min; l3 wall ~51 min (run_meta); holdout dtype tl fp32 / l3 fp16

## Open items

- Phase H verifier not written yet
- Attorney / AI disclosure / Phase M overlap path
- Record L3 holdout dtype decision formally in `DECISIONS.md` if required

## Run progress

| Grid | Complete | Failed | Total | Notes |
|---|---|---|---|---|
| tl | **75** | 0 | 75 | G acceptance PASS |
| l3 | **45** | 0 | 45 | G acceptance PASS |

## Measured constants

| Item | Value |
|---|---|
| TinyLlama per-client upload, FedIT / FLoRA | 9,011,200 bytes (Phase D + F1 confirm) |
| TinyLlama per-client upload, FFA-LoRA | 9,011,200 upload; 3,244,032 download (Phase D) |
| LLaMA-3B per-client upload, FedIT / FLoRA | 9,175,040 bytes (measured F2) |
| TinyLlama minutes per run (4090) | ~29.3 train-only (F1); production median wall ~27 min |
| LLaMA-3B minutes per run, and GPU used | ~65.2 train-only (F2) on RTX 4090; peak ~9 GB; production median wall ~51 min |
| Workers per GPU (TinyLlama) | **1** (F3 gate) |
| Mac smoke cell (1 round, 300 samples, incl. holdout) | about 280 s; holdout-only about 136 s |
