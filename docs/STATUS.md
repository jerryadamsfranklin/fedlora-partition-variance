# STATUS

Last updated: 18 Sep 2026

Replace this file in the Claude Project whenever the state changes. Keep only one copy.

## Current phase

Phase M on phase-m. Template verified against thesai.org ZIP (letterpaper confirmed), header fixed, step 6 reference check done. Awaiting PDF review before fast-forward and tag.

## Done

- Phases B to E on main; freeze-v1 at 0812fcf; freeze-v2 at 4f9fcf8
- Phase F gates passed; Phase G complete (tl 75/75, l3 45/45); Phase H verifier exits 0
- Phase I complete; Phase J figures 505 pt, 8 pt minimum fonts
- Phase L complete and merged into main (8031a74)
- Phase M steps 1 to 5: SAI template assembly (7 pages), V9 complete (25 claims), verifier exit 0, seven review fixes, anonymization (author and title metadata empty, GenAI declaration version b, no username paths in figures), typography clean across 12 files, overlap 0.082% vs OJ-CS body and 0.000% vs supplement (target under 5%)
- IJACSA format and submission requirements filed as docs/IJACSA_FORMAT_AND_SUBMISSION.md
- Official LaTeX ZIP and copyright PDF stored under manuscript/template/; paper size matches (`conference, letterpaper`); left header now "(IJACSA) ..."; rebuild still 7 pages
- Phase M checklist adds signed copyright form and non-Gmail email plus ORCID
- Step 6: nine refs verified against primary sources; FFA-LoRA OpenReview ID corrected (DPIGDbSsbV to NLPzL6HWNl)

## Next

1. Review the final PDF here, then fast-forward phase-m into main and tag ijacsa-submitted-v1
2. Mon 21 Sep go/no-go; target submission Tue 22 Sep

## Blocking before submission

- Attorney confirmation that an IJACSA publication carries weight, before the GBP 800 APC
- Signed IJACSA copyright form (blank copy in manuscript/template/IJACSA_Copyright.pdf; complete and sign before send)
- Real author email for the submission form; prefer an address on jerryadamsfranklin.com over Gmail, since IJACSA discourages Gmail; ORCID iD ready
- Affiliation stays "Independent Researcher"

## Framing rules for the manuscript

- Condition the flip claim on effect size (paired SD 0.00282 tl, 0.00473 l3; near-tie needs 206 and 46 paired draws; separable pairs need 3)
- No partition main effect claim at 3B; the 3B story is the interaction (0.764)
- IID floor at 3B descriptive only (2 df per method)
- The l3 flip rise from k = 1 to k = 3 is a small-sample artifact
- RQ4 exploratory, uncorrected, not replicated at 3B
- Communication as measured, within method; no efficiency ranking
- No method recommendation
- MixedLM cross-check partial; moment estimates primary
- Cross-scale comparisons confounded (instruction-tuned versus base; float32 versus float16 base weights)
- Where the interaction dominates, pairing on partitions buys little
- No prevalence claims about the literature: cite specific papers, never "usually", "rarely", or "most papers"

## Decisions made

- Venue: IJACSA October cycle, target submission Tue 22 Sep; November fallback if go/no-go fails 21 Sep
- Two scales on RTX 4090, --workers 1; l3 holdout float16, tl float32
- freeze-v2 for the eval-only change; --max-retries 5 because of host instability
- Phase K literature audit dropped; no audit-derived counts
- Release statement covers results and metadata, not adapter weights
- Byte accounting cites arXiv:2609.13512 in the third person, without naming the author in the text
- Generative AI declaration: plan version (b)

## Open items

- JCR impact factor figure for IJACSA (read from Clarivate)
- Attorney question on IEEE Early Access counting as published for the OJ-CS paper
- M3 still up; destroy and revoke the GitHub and HF tokens
- Local tooling: use .venv/bin/python

## Run progress

| Grid | Complete | Failed | Total |
|---|---|---|---|
| tl | 75 | 0 | 75 |
| l3 | 45 | 0 | 45 |
