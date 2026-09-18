# STATUS

Last updated: 18 Sep 2026

Replace this file in the Claude Project whenever the state changes. Keep only one copy.

## Current phase

Phase J fixes applied and merged path ready; Phase L Setup draft on phase-j.

## Done

- Phases B to E on main; freeze-v1 at 0812fcf; freeze-v2 at 4f9fcf8 (eval-only float16 change)
- Phase F gates passed; Phase G complete (tl 75/75, l3 45/45); Phase H verifier exits 0 (V1 to V8, V11)
- Phase I complete; pair-level flip and observed-gap power addendum on main (33704cb)
- Phase J on phase-j (ba52816): Figs 1 to 3, Tabs 1 to 3 generated from analysis CSVs only
- Review in the Claude Project: all three tables trace to the CSVs; variance components reproduced independently; comm fit matches V6 exactly (max_abs_err 0)

## Results (verified)

- tl alpha 0.1: s2_P 4.09e-6 (0.508, CI 0.202 to 0.663), s2_PM 3.78e-6 (0.469), s2_E 1.89e-7 (0.023)
- l3 alpha 0.1: s2_P 3.28e-6 (0.227, CI 0.000 to 0.551), s2_PM 1.11e-5 (0.764, CI 0.443 to 0.990), s2_E 1.31e-7 (0.009)
- IID pooled: tl 6.40e-8 (ratio 2.96); l3 3.07e-7 (ratio 0.43, 2 df per method, descriptive only)
- Paired per-draw SD: tl 0.00282 (empirical 0.00276); l3 0.00473 (empirical 0.00461)
- Flip P(best) = P(full order): tl 0.55, 0.41, 0.38, 0.28 for k = 1, 2, 3, 5; l3 0.17, 0.27, 0.29 for k = 1, 2, 3. All flips are the fedit vs flora pair; separable pairs 0 of 20 and 0 of 12
- Draws for 80% power at the observed gaps: fedit vs flora needs 206 paired (tl) and 46 (l3); separable pairs need 3
- Method means at alpha 0.1: tl flora 1.6957 (SD 0.0013), fedit 1.6962 (0.0038), ffa_lora 1.7192 (0.0026); l3 fedit 1.8028 (0.0051), flora 1.8049 (0.0020), ffa_lora 1.8355 (0.0031). Holm: ffa_lora differs from both; fedit vs flora not significant
- Communication: tl fedit and flora 2320.3 to 2578.1 MB, ffa_lora 884.8 to 983.1; l3 2362.5 to 2625.0 and 992.3 to 1102.5; slope per active client matches V6 exactly
- Spearman: tl mean JS divergence rho 0.72 (p 0.019, n 10) but 0.086 at 3B; does not survive Holm across the 5 statistics
- I7: tl row 1 on partition share; l3 row 1 on flip probability only plus row 4; cross-scale row 6

## Next

1. Fast-forward phase-j into main (figure/table fixes + Setup draft)
2. Phase L: Related Work, Results, Discussion, Introduction, Abstract
3. Destroy M3 and revoke the GitHub and HF tokens
4. Jerry: JCR impact factor; attorney questions; AI disclosure version choice
5. Mon 21 Sep go/no-go; target submission Tue 22 Sep

## Framing rules for the manuscript

- Condition the flip claim on effect size: pairs separated by less than the per-draw paired SD are ordered near-randomly; gaps of about 0.023 (tl) and 0.031 (l3) were recovered in every draw; the observed near-tie would need 206 and 46 paired draws
- No partition main effect claim at 3B (s2_P CI includes 0); the 3B story is the interaction
- IID floor at 3B descriptive only (2 df per method)
- The l3 flip rise from k = 1 to k = 3 is a small-sample artifact (6 partitions, near-tie)
- RQ4 correlations exploratory, uncorrected, and not replicated at 3B
- Communication reported as measured, within method; no efficiency ranking
- No method recommendation
- Active clients only vary 9 to 10, so do not lean on that variable

## Decisions made

- Venue: IJACSA October cycle, target submission Tue 22 Sep; November fallback if go/no-go fails 21 Sep
- Two scales on RTX 4090, --workers 1; l3 holdout float16 (kept after the 4.1e-5 spot-check), tl float32
- freeze-v2 for the eval-only change; --max-retries 5 because of host instability
- Phase K literature audit dropped; motivate from cited published practice; no audit-derived counts
- Release statement covers results and metadata, not adapter weights (only 25 of 120 retained)
- Do not pay the IJACSA APC until the attorney confirms the venue counts

## Findings to carry into the paper

- Alpha 0.1: active clients 9 to 10; effective clients 7 to 10 (tl); zero-step clients hold at most 11 samples
- Discarded trailing samples per seed: 27 to 60 (tl), 41 to 104 (l3); client sizes 2 to 1218
- client.py steps only on complete accumulation blocks (no drop_last)
- FFA-LoRA as implemented uploads A and B, downloads B only
- Hardware: one RTX 4090 per run; production medians 27 min (tl) and 51 min (l3)
- Base loss 2.120666 (tl), 2.168946 (l3); three cells resumed from checkpoint, all inside their group range

## Open items

- JCR impact factor; attorney questions (IJACSA weight, IEEE Early Access)
- AI disclosure version choice (drafting support likely applies)
- M3 still up; destroy and revoke tokens
- Overlap check (Phase M): OLD is the local folder federated-lora-experiments
- V9 claims list unfilled until the manuscript numbers are fixed
- Local tooling: use .venv/bin/python

## Run progress

| Grid | Complete | Failed | Total |
|---|---|---|---|
| tl | 75 | 0 | 75 |
| l3 | 45 | 0 | 45 |
