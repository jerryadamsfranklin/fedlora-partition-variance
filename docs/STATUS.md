# STATUS

Last updated: 18 Sep 2026

Replace this file in the Claude Project whenever the state changes. Keep only one copy.

## Current phase

Phase L drafting. Setup and Results drafted on phase-l (294b72c); four Results revisions pending. Related Work next.

## Done

- Phases B to E on main; freeze-v1 at 0812fcf; freeze-v2 at 4f9fcf8 (eval-only float16 change)
- Phase F gates passed; Phase G complete (tl 75/75, l3 45/45); Phase H verifier exits 0 (V1 to V8, V11)
- Phase I complete, plus the pair-level flip and observed-gap power addendum
- Phase J fixes on main (0669f93): all figures 505 pt wide, minimum font 8 pt; i7 claims wording; Tab 2 design parameters; Tab 1 alpha notation
- Setup section drafted and reviewed (six fixes applied, pre-registration and variance-model paragraphs added, refs.bib started with verified FedIT, FFA-LoRA, FLoRA cites)
- Results drafted (~1030 words) and verified in the Claude Project: Holm p values, CIs, Wilson widths, unpaired n, and the FFA-LoRA byte accounting all reproduce

## Next

1. Apply the four Results revisions (mixed-model disclosure, FFA-LoRA byte wording, flip-equality explanation, unpaired pointer) plus the DECISIONS row on the MixedLM partition component
2. Draft Related Work (about 500 words), then Discussion, Introduction, Abstract
3. Phase M: SAI template, anonymization, V9 claims list, overlap check, typography, references
4. Destroy M3; revoke the GitHub and HF tokens
5. Jerry: JCR impact factor; attorney questions; AI disclosure version choice
6. Mon 21 Sep go/no-go; target submission Tue 22 Sep

## Framing rules for the manuscript

- Condition the flip claim on effect size: pairs below the per-draw paired SD (0.00282 tl, 0.00473 l3) are ordered near-randomly; gaps of about 0.023 and 0.031 were recovered in every draw; the near-tie needs 206 (tl) and 46 (l3) paired draws
- No partition main effect claim at 3B (s2_P CI includes 0); the 3B story is the interaction (0.764)
- IID floor at 3B descriptive only (2 df per method)
- The l3 flip rise from k = 1 to k = 3 is a small-sample artifact
- RQ4 exploratory, uncorrected, not replicated at 3B
- Communication reported as measured, within method; no efficiency ranking
- No method recommendation
- Active clients vary only 9 to 10
- MixedLM cross-check is partial; moment estimates are primary

## Decisions made

- Venue: IJACSA October cycle, target submission Tue 22 Sep; November fallback if go/no-go fails 21 Sep
- Two scales on RTX 4090, --workers 1; l3 holdout float16 (kept after the 4.1e-5 spot-check), tl float32
- freeze-v2 for the eval-only change; --max-retries 5 because of host instability
- Phase K literature audit dropped; motivate from cited published practice; no audit-derived counts
- Release statement covers results and metadata, not adapter weights (25 of 120 retained)
- Do not pay the IJACSA APC until the attorney confirms the venue counts

## Open items

- JCR impact factor; attorney questions (IJACSA weight, IEEE Early Access)
- AI disclosure version choice (drafting support applies if Claude drafts prose)
- M3 still up; destroy and revoke tokens
- Overlap check (Phase M): OLD is the local folder federated-lora-experiments
- V9 claims list unfilled until manuscript numbers are final
- Every reference must be verified against its primary source before use
- Local tooling: use .venv/bin/python

## Run progress

| Grid | Complete | Failed | Total |
|---|---|---|---|
| tl | 75 | 0 | 75 |
| l3 | 45 | 0 | 45 |
