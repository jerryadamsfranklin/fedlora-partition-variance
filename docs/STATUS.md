# STATUS

Last updated: 18 Sep 2026

Replace this file in the Claude Project whenever the state changes. Keep only one copy.

## Current phase

Phase L drafting on phase-l. Setup, Results, Related Work done. Discussion revised; Introduction drafted for review; Abstract next.

## Done

- Phases B to E on main; freeze-v1 at 0812fcf; freeze-v2 at 4f9fcf8
- Phase F gates passed; Phase G complete (tl 75/75, l3 45/45); Phase H verifier exits 0
- Phase I complete with pair-level flip and observed-gap power addendum; Phase J figures 505 pt, 8 pt minimum fonts
- Setup and Results drafted, verified, revised
- Related Work drafted and corrected; all external citations verified against primary sources
- Discussion revised: unpaired power correction (206 vs 416; 46 vs 57; interaction enters paired difference twice), limitations (two scales, 10 clients, 15 rounds, accumulation blocks), cross-scale confounds, wording
- Introduction drafted (~600 words): FFA/FLoRA motivating practice, RQ1--RQ3, contributions, roadmap

## Next

1. Review Introduction; then draft Abstract (180 to 200 words)
2. Phase M: SAI template, anonymization, V9 claims list, overlap check, typography
3. Destroy M3 after syncing available adapters; revoke the GitHub and HF tokens
4. Jerry: JCR impact factor; attorney questions; AI disclosure version choice
5. Mon 21 Sep go/no-go; target submission Tue 22 Sep

## Framing rules for the manuscript

- Condition the flip claim on effect size (paired SD 0.00282 tl, 0.00473 l3; near-tie needs 206 and 46 paired draws; separable pairs need 3)
- No partition main effect claim at 3B; the 3B story is the interaction (0.764)
- IID floor at 3B descriptive only (2 df per method)
- The l3 flip rise from k = 1 to k = 3 is a small-sample artifact
- RQ4 exploratory, uncorrected, not replicated at 3B
- Communication as measured, within method; no efficiency ranking
- No method recommendation
- MixedLM cross-check partial; moment estimates primary
- Position against FFA-LoRA's across-run SDs: prior work reports run variance; this paper decomposes it
- Cross-scale comparisons are confounded: TinyLlama-1.1B-Chat is instruction-tuned while LLaMA-3.2-3B is a base model, and base weights are float32 versus float16
- Where the interaction dominates, pairing on partitions buys little

## Decisions made

- Venue: IJACSA October cycle, target submission Tue 22 Sep; November fallback if go/no-go fails 21 Sep
- Two scales on RTX 4090, --workers 1; l3 holdout float16, tl float32
- freeze-v2 for the eval-only change; --max-retries 5 because of host instability
- Phase K literature audit dropped; motivate from cited published practice; no audit-derived counts
- Release statement covers results and metadata, not adapter weights
- Do not pay the IJACSA APC until the attorney confirms the venue counts

## Open items

- JCR impact factor; attorney questions (IJACSA weight, IEEE Early Access)
- AI disclosure: drafting support applies
- M3 still up; destroy and revoke tokens
- Overlap check (Phase M): OLD is the local folder federated-lora-experiments
- V9 claims list unfilled until manuscript numbers are final
- Local tooling: use .venv/bin/python

## Run progress

| Grid | Complete | Failed | Total |
|---|---|---|---|
| tl | 75 | 0 | 75 |
| l3 | 45 | 0 | 45 |
