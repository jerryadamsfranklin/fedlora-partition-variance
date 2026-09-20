# STATUS

Last updated: 20 Sep 2026

Replace this file in the Claude Project whenever the state changes. Keep only one copy.

## Current phase

Phase N complete and verified on clean data. N9 stack-effect measured. Manuscript review bundle next (Jerry targeted O5 patches); no blind results rewrite until then. All GPU work is finished.

## Venue

IEEE Access primary, IJACSA fallback. Single-anonymized, no anonymization. About 20% overall acceptance; for this paper roughly 45 to 50% published at Access, with Stage 3 desk screening the dominant risk. APC $2,160. Never submit to both at once.

## Done

- Phases B to M: 120 prod_v1 runs, complete manuscript drafted, overlap 0.082% against the OJ-CS body
- Phase N: 84 prod_v2 runs; N6 holdout repair; N7 stack census; N8 retrain of 54 cells on torch 2.2.0+cu121
- N8-5: V1, V2, V2-cross-tag, V7, V12 all PASS across 204 cells and all tags (four duplicate completes quarantined first)
- N8-6: I8, I9, I10 recomputed on clean data; pre-registered outcome rows unchanged
- N8-7, N8-8: DECISIONS rows appended; live IP and host IPs redacted in a forward commit
- N9: paired stack-effect on 54 quarantined vs retrained cells (`analysis/stack_effect.csv`)
- Vast instances destroyed (Jerry)
- Repo public; 27 references verified; phase-n pushed through N8-8

## Verified results (clean, final unless the analysis changes)

- tl alpha 0.1 (p=10): shares 0.508 / 0.469 / 0.023; s2_P 4.09e-6; sd_pair 0.00282; near-tie needs 206 paired draws
- tl alpha 0.5 (p=10): shares 0.2766 / 0.6817 / 0.0416; share_P CI includes zero; absolute variance about 20x smaller than alpha 0.1; near-tie resolves (+0.00218, p=3.2e-6)
- I9: all three share differences include zero (pre-registered row "gradient absent")
- l3 alpha 0.1 (p=10): share_P 0.000 truncated, CI [0, 0.329]; share_PM 0.992; s2_PM 2.944e-5; sd_pair 0.00770
- LEAD FINDING: the l3 top-two order reverses between p=6 (fedit ahead 0.00201) and p=10 (flora ahead 0.00067), neither significant, and the interaction component is 2.66x larger at p=10 than p=6. At six draws you would report the wrong ordering and underestimate interaction variance
- Near-tie at 3B now needs more than 1000 paired draws
- N9 stack effect: tl a05 mean Δ ≈ −8.5e-8 (vs sd_pair 0.00108); l3 a01 mean Δ ≈ 8.4e-4 (vs sd_pair 0.00770)

## Next

1. Deliver manuscript_review zip for Jerry O5 patches (Results first)
2. Apply Jerry replacement blocks; regenerate figures/tables; refresh V9; verifier exit 0
3. Finish O3 and O4: ieeeaccess.cls template, ORCID, email, Zenodo concept DOI
4. Final checks: typography, overlap, references, PDF read-through
5. Jerry: revoke campaign tokens; enable Zenodo then cut v0.9.1

## Framing rules for the manuscript

- Lead with the Partition-Draw Reporting Protocol, demonstrated by the partition-count sensitivity result
- Condition every ranking claim on effect size; report the minimum detectable difference
- No partition main effect claim at 3B; report truncation
- The shares comparison across alpha is pre-registered; the absolute-variance contrast is post hoc and labeled
- RQ4 exploratory, uncorrected, not replicated at 3B
- Communication as measured, within method; no efficiency ranking
- No method recommendation
- Cross-scale comparisons confounded (instruction-tuned versus base; float32 versus float16 base weights)
- No prevalence claims about the literature
- Disclose: freeze-v3.1 eval hotfix, 15 repaired holdouts, the 54-cell retrain with the N9 number, four quarantined duplicates, the retry census, and the MixedLM cross-check status

## Open items

- Zenodo DOI, ORCID, submission email (blocking submission)
- Full ieeeaccess.cls template
- Cabells Predatory Reports check on IJACSA (fallback only)
- Attorney: IEEE Access and the scholarly-articles criterion; Early Access as publication for the OJ-CS paper
- LoRA and Cho bib entries still need primary-source confirmation
- Human skim of plan, DECISIONS, PROVENANCE, overlap_check.py for quoted OJ-CS content

## Run progress

| Grid | Complete | Total | Tag |
|---|---|---|---|
| tl a01 + IID | 75 | 75 | prod_v1 |
| l3 a01 + IID | 45 | 45 | prod_v1 |
| tl_a05 | 60 | 60 | prod_v2 |
| l3_ext | 24 | 24 | prod_v2 |
