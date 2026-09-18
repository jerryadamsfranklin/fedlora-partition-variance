# STATUS

Last updated: 18 Sep 2026

Replace this file in the Claude Project whenever the state changes. Keep only one copy.

## Current phase

Phase L drafting on phase-l. Full prose draft complete (Abstract through Discussion). Phase M next after Abstract review.

## Done

- Phases B to E on main; freeze-v1 at 0812fcf; freeze-v2 at 4f9fcf8
- Phase F gates passed; Phase G complete (tl 75/75, l3 45/45); Phase H verifier exits 0
- Phase I complete with pair-level flip and observed-gap power addendum; Phase J figures 505 pt, 8 pt minimum fonts
- Setup, Results, Related Work, Discussion drafted, verified, revised
- All external citations verified against primary sources
- Introduction revised: softened absence claims; held-out loss scale; recommendation in contributions; byte-accounting cite logged
- Abstract drafted (180--200 words): question, design, three headlines, recommendation, no method recommendation
- DECISIONS: cite arXiv:2609.13512 (Franklin) in third person in Setup Communication because measured-payload accounting follows that preprint

## Next

1. Review Abstract; then Phase M: SAI template, anonymization, V9 claims list, overlap check, typography, final verifier run
2. Destroy M3 after syncing available adapters; revoke the GitHub and HF tokens
3. Jerry: JCR impact factor; attorney questions; AI disclosure version choice
4. Mon 21 Sep go/no-go; target submission Tue 22 Sep

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
- Cross-scale comparisons are confounded (instruction-tuned versus base model; float32 versus float16 base weights)
- Where the interaction dominates, pairing on partitions buys little
- No prevalence claims about the literature: cite specific papers, never "usually" or "most papers"

## Decisions made

- Venue: IJACSA October cycle, target submission Tue 22 Sep; November fallback if go/no-go fails 21 Sep
- Two scales on RTX 4090, --workers 1; l3 holdout float16, tl float32
- freeze-v2 for the eval-only change; --max-retries 5 because of host instability
- Phase K literature audit dropped; motivate from cited published practice; no audit-derived counts
- Release statement covers results and metadata, not adapter weights
- Do not pay the IJACSA APC until the attorney confirms the venue counts
- Cite arXiv:2609.13512 in third person where measured-payload byte accounting is used (Setup)

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
