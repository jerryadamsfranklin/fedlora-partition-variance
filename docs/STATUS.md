# STATUS

Last updated: 18 Sep 2026

Replace this file in the Claude Project whenever the state changes. Keep only one copy.

## Current phase

Phase N on phase-n. N1 to N4 complete; freeze-v3 tagged. Awaiting launch approval for N5 (84 prod_v2 runs).

## Standing rule

Every change request goes into docs/IMPLEMENTATION_PLAN.md as a numbered phase with acceptance checks, and is executed from the plan. No ad-hoc execution.

## Venue decision

- Target: IEEE Access. JCR-indexed, single-anonymized review, binary decisions, about 20% acceptance, 4 weeks average to decision, 4 to 6 weeks to publication, APC $2,160 (discount request planned)
- Main risk: Stage 3 desk screening requires a clear advance over the state of the art; mitigated by naming the Partition-Draw Reporting Protocol and by the alpha gradient
- Fallback: IJACSA November or December cycle. Never submit to both at once (Access rejects duplicates at Stage 2)
- Odds after the addendum: desk reject 25 to 30%; publication before March 2027 roughly 45 to 55%
- IJACSA dossier: publisher in the archived Beall's List, not in DOAJ, JUFO level 0, FWCI 0.34, but Scopus and ESCI indexed. Cabells check still outstanding

## Contribution naming

The Partition-Draw Reporting Protocol, spelled out, no acronym (PDR, PDP, PVR, PDA all collide with common engineering terms). Three steps: report the number of partition draws with partition seeds separate from training seeds; pair method comparisons on the same draws; report the minimum detectable difference.

## Done

- Phases B to M complete under freeze-v1 and freeze-v2: 120 runs, verifier exit 0, full 7-page manuscript, typography clean, overlap 0.082% against the OJ-CS body
- Phase N and Phase O added to the plan; SCOPE.md updated for alpha 0.5 and l3 extension
- N1: 15 configs (3 × tl a05); config tests pass
- N2: grids/tl_a05.yaml (60) and grids/l3_ext.yaml (24); shard counts 21/21/18 and 9/9/6; group-shard tests pass
- N3: ANALYSIS_PLAN I8 to I10 plus four outcome-to-claim rows
- N4: V12 implemented; freeze-v3 tagged; training path empty freeze-v1..freeze-v3; eval pinned freeze-v2..freeze-v3

## Next

1. N5: update production_guard for freeze-v3 / prod_v2; launch 84 runs on 3 RTX 4090s
2. N6 DECISIONS rows; sync with adapters retained; N7 MixedLM and refs after runs
3. Analysis I8 to I10; Phase O Access rework
4. Target submission Fri 26 Sep; hard stop on runs Mon 22 Sep

## Framing rules for the manuscript

- Lead with the protocol as the contribution
- Condition the flip claim on effect size (paired SD 0.00282 tl, 0.00473 l3; near-tie needs 206 and 46 paired draws; separable pairs need 3)
- Report whatever the alpha gradient shows, per the pre-registered rows
- No partition main effect claim at 3B unless the p=10 interval excludes zero
- RQ4 exploratory, uncorrected, not replicated at 3B
- Communication as measured, within method; no efficiency ranking
- No method recommendation
- Cross-scale comparisons confounded (instruction-tuned versus base; float32 versus float16 base weights)
- No prevalence claims about the literature

## Open items

- Cabells Predatory Reports check on IJACSA (fallback only)
- Attorney: does IEEE Access satisfy the scholarly-articles criterion; does IEEE Early Access count as published for the OJ-CS paper
- refs.bib to about 25 entries, each verified
- ORCID and real email for the Access submission; public repo plus Zenodo DOI
- prod_v1 adapters are gone (25 of 120); keep every prod_v2 adapter
- Local tooling: use .venv/bin/python

## Run progress

| Grid | Complete | Total | Tag |
|---|---|---|---|
| tl (alpha 0.1 + IID) | 75 | 75 | prod_v1 |
| l3 (alpha 0.1 + IID) | 45 | 45 | prod_v1 |
| tl_a05 | 0 | 60 | prod_v2 |
| l3_ext | 0 | 24 | prod_v2 |
