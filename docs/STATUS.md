# STATUS

Last updated: 18 Sep 2026

Replace this file in the Claude Project whenever the state changes. Keep only one copy.

## Current phase

Phase I complete and verified independently against runs.csv. Pair-level flip addendum in progress on phase-i, then Phase J (figures and tables).

## Done

- Phases B to E on main; freeze-v1 at 0812fcf; freeze-v2 at 4f9fcf8 (eval-only float16 change)
- Phase F gates passed on RTX 4090; Phase G complete (tl 75/75, l3 45/45)
- Phase H: verifier exits 0 on V1 to V8 and V11; V10 census; 3 resumed cells all inside their group range
- Float16 holdout kept: max |fp16-fp32| 4.1e-5
- Phase I (I0 to I6) computed; I1, I2, I4, I5 and the I3 simulation reproduced independently in the Claude Project

## Results (verified)

- tl alpha 0.1: s2_P 4.09e-6 (0.508), s2_PM 3.78e-6 (0.469), s2_E 1.89e-7 (0.023); no truncation
- l3 alpha 0.1: s2_P 3.28e-6 (0.227, CI includes 0), s2_PM 1.11e-5 (0.764), s2_E 1.31e-7 (0.009)
- IID pooled: tl 6.40e-8 (ratio 2.96); l3 3.07e-7 (ratio 0.43, only 2 df per method, descriptive only)
- Paired per-draw SD: tl 0.00282 (empirical 0.00276); l3 0.00473 (empirical 0.00461)
- Flip P(best) = P(full order): tl 0.55, 0.41, 0.37, 0.29 for k = 1, 2, 3, 5; l3 0.17, 0.27, 0.29 for k = 1, 2, 3
- All flips occur in the fedit vs flora pair (gap 0.00055 tl, 0.00201 l3). Separable pairs (about 0.023 tl, 0.031 l3) never flipped: 0 of 20 and 0 of 12 single draws
- Draws for 80% power: tl paired 5 / 3 / 3 / 2 and l3 paired 10 / 5 / 3 / 3 for Delta 0.005 / 0.01 / 0.02 / 0.05
- Method means at alpha 0.1: tl flora 1.6957, fedit 1.6962, ffa_lora 1.7192; l3 fedit 1.8029, flora 1.8049, ffa_lora 1.8355. Holm: ffa_lora differs from both; fedit vs flora not significant in either model
- I6: tl mean JS divergence rho 0.72 (p 0.019, n 10), exploratory and uncorrected; communication fit matches V6 exactly; ranges tl fedit/flora 2320 to 2578 MB, ffa_lora 885 to 983 MB
- I7 rows selected: row 1 (both models), row 4 (l3 interaction), row 6 (overlapping cross-scale CIs)

## Next

1. Pair-level flip table and observed-gap power rows; two DECISIONS entries; fast-forward phase-i into main
2. Phase J: Figs 1 to 3, Tabs 1 to 3, LaTeX tables from CSVs only
3. Sync remaining adapters from M3, then destroy it and revoke the GitHub and HF tokens
4. Phase L manuscript: Setup and Related Work can be drafted now
5. Jerry: JCR impact factor; attorney question on venue weight; AI disclosure version

## Framing rules for the manuscript

- Condition the flip claim on effect size: pairs separated by less than the per-draw paired SD are ordered near-randomly; a gap of about 0.023 was recovered in every draw
- No partition main effect claim at 3B (s2_P CI includes 0); the 3B story is the interaction
- IID floor at 3B is descriptive only; no claim that alpha 0.1 residual variance is below it
- The l3 flip rise from k=1 to k=3 is a small-sample artifact (6 partitions, near-tie)
- RQ4 correlations are exploratory and uncorrected
- Communication reported as measured, within method; no efficiency ranking
- No method recommendation

## Decisions made

- Venue: IJACSA October cycle, target submission Tuesday 22 Sep; November fallback if go/no-go fails 21 Sep
- Two scales on RTX 4090, --workers 1; l3 holdout float16, tl float32
- freeze-v2 for the eval-only change; --max-retries 5 because of host instability
- Phase K literature audit dropped; motivate from cited published practice; no audit-derived counts in the paper
- Do not pay the IJACSA APC until the attorney confirms the venue counts

## Findings to carry into the paper

- Alpha 0.1 partitions: active clients 9 to 10; effective clients 7 to 10 (TinyLlama); zero-step clients hold at most 11 samples
- Discarded trailing samples per seed: 27 to 60 (tl), 41 to 104 (l3); client sizes 2 to 1218
- client.py steps only on complete accumulation blocks (no drop_last)
- FFA-LoRA as implemented uploads A and B, downloads B only
- Hardware: one RTX 4090 per run; production median wall 27 min (tl), 51 min (l3)
- Base loss 2.120666 (tl), 2.168946 (l3)
- Three cells resumed from checkpoint, all within their group range

## Open items

- Adapter weights: only 25 of 120 on the Mac; sync from M3 before destroying, and note in the artifact statement if incomplete
- JCR impact factor; attorney questions (IJACSA weight, IEEE Early Access)
- AI disclosure version choice
- Revoke GitHub and HF tokens after M3 is destroyed
- Overlap check (Phase M): OLD is the local folder federated-lora-experiments
- Local tooling: use .venv/bin/python

## Run progress

| Grid | Complete | Failed | Total |
|---|---|---|---|
| tl | 75 | 0 | 75 |
| l3 | 45 | 0 | 45 |
