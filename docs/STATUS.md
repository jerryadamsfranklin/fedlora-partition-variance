# STATUS

Last updated: 18 Sep 2026

Replace this file in the Claude Project whenever the state changes. Keep only one copy.

## Current phase

Phase H complete (verifier exits 0 on V1 to V8 and V11; V9 pending Phase L). Phase I starting on branch phase-i.

## Done

- Phases B to E on main; `freeze-v1` at 0812fcf
- Phase F on RTX 4090: F1 29.3 min; F2 65.2 min, ~9 GB peak; F3 ratio 1.06x so workers 1; bytes match
- Phase G: tl 75/75 and l3 45/45 complete, all prod_v1, all freeze-v1 with clean tracked tree, single GPU model per grid, identical library versions
- Phase H: verify_varpart.py V1 to V8 and V11 PASS; V4 scoped (a01 column, iid none); V7 checks eval_dtype identical within grid; V10 resume/retry census
- Float16 holdout decision settled: max |fp16-fp32| tuned_loss 4.1e-5, about 250x below the 0.01 effect scale; no l3 re-eval needed
- Eval provenance: production eval sha256 201b7975...; freeze-v2 tags 4f9fcf8 (eval-only float16 change); TinyLlama holdout path unchanged (float32)

## Next

1. Commit the float32 spot-check artifacts; add the float16 DECISIONS row; resume-cell range check into phase_h_report; fast-forward phase-h into main
2. Phase I on branch phase-i per ANALYSIS_PLAN.md (I0 to I6), then report which I7 row the results select
3. Destroy M3 after the spot-check files are committed and all 120 adapters are confirmed on the Mac
4. Phase J figures and tables; Phase L manuscript (Setup and Related Work can start now)
5. Jerry: JCR impact factor figure; attorney question on IJACSA weight; choose the AI disclosure version

## Decisions made

- Venue: IJACSA October cycle, submit by 24 Sep (target Tuesday 22 Sep); November fallback if go/no-go fails on 21 Sep
- Two scales on RTX 4090, --workers 1
- L3 holdout eval uses float16 with sequential load; TinyLlama holdouts float32; kept after the spot-check
- freeze-v2 tags the eval-only change; --max-retries 5 used instead of 1 because of host instability
- Phase K literature audit dropped; motivate from cited published practice; no audit-derived counts may appear in the paper
- Communication compared only within method across partitions; methods not ranked by bytes
- Do not pay the IJACSA APC until the attorney confirms the venue counts

## Findings to carry into the paper

- Alpha 0.1 partitions: active clients 9 to 10; effective clients 7 to 10 (TinyLlama); 4 of 10 seeds have at least one zero-step client (seed 2008 has two)
- Zero-step clients hold at most 11 samples; discarded trailing samples 27 to 60 (TinyLlama), 41 to 104 (LLaMA); client sizes 2 to 1218
- client.py steps only on complete accumulation blocks (no drop_last)
- FFA-LoRA as implemented uploads A and B, downloads B only
- Hardware: single RTX 4090 per run; production median wall 27 min (tl) and 51 min (l3)
- Held-out base loss 2.120666 (tl) and 2.168946 (l3); tuned ranges 1.691 to 1.723 (tl) and 1.790 to 1.839 (l3)
- l3 holdout in float16; float32 spot-check shows differences of at most 4.1e-5
- Three cells resumed from checkpoint (1 tl flora, 2 l3 flora); disclose with the range check
- Frame the contribution as a measurement result plus reporting recommendations

## Open items

- Literature audit dropped: rewrite the Introduction motivation from cited papers
- JCR impact factor for IJACSA; attorney question on venue weight; attorney question on IEEE Early Access
- AI disclosure version choice (drafting support likely applies)
- M3 still running; destroy after commits and adapter check
- Revoke GitHub and HF tokens after M3 is destroyed
- Overlap check (Phase M): OLD is the local folder federated-lora-experiments
- Local tooling: use .venv/bin/python

## Run progress

| Grid | Complete | Failed | Total |
|---|---|---|---|
| tl | 75 | 0 | 75 |
| l3 | 45 | 0 | 45 |

## Measured constants

| Item | Value |
|---|---|
| TinyLlama per-client upload, FedIT / FLoRA | 9,011,200 bytes |
| TinyLlama per-client upload, FFA-LoRA | 9,011,200 upload; 3,244,032 download |
| LLaMA-3B per-client upload, FedIT / FLoRA | 9,175,040 bytes |
| TinyLlama minutes per run (4090) | 29.3 (F1); production median 27.1 |
| LLaMA-3B minutes per run (4090) | 65.2 (F2); production median 51.1; peak ~9 GB |
| Workers per GPU (TinyLlama) | 1 |
| Holdout eval dtype | tl float32; l3 float16 |
