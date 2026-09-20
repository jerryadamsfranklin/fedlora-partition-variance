# STATUS

Last updated: 20 Sep 2026

Replace this file in the Claude Project whenever the state changes. Keep only one copy.

## Current phase

Manuscript tagged `ieee-access-submitted-v1` on `main` at `e21251c` (10 pages, verifier exit 0, typography clean). Ready for ScholarOne submission to IEEE Access. Record the manuscript ID here after submit.

## Venue

IEEE Access. Single-anonymized, no anonymization. About 20% overall acceptance; my estimate for this paper is roughly 45 to 50% published, with Stage 3 desk screening the dominant risk. APC $2,160 (5% IEEE member / 20% society member discount available). IJACSA is the fallback; never submit to both at once.

## Done

- 204 production cells across two models and three settings; all on torch 2.2.0+cu121, RTX 4090; V1 to V12 pass
- Analysis I0 to I10 complete on clean data; pre-registered outcome rows selected
- Manuscript in ieeeaccess.cls: abstract, six sections, three tables, three figures, 27 verified references, author bio
- Repo public with MIT license; release v0.9.1; concept DOI 10.5281/zenodo.22861074; version DOI 10.5281/zenodo.22861075
- ORCID 0009-0006-8470-8349 in the author block, .zenodo.json, and CITATION.cff
- Corresponding email in manuscript: jerry.adamsf@gmail.com (domain address preferred if routing is ready)
- Public repo scan clean at HEAD (no tokens; IPs redacted forward, history not rewritten)
- `phase-o` fast-forwarded into `main`; tag `ieee-access-submitted-v1`

## Next

1. Optional: switch corresponding email to a jerryadamsfranklin.com address before submit
2. Confirm ORCID public visibility lists Independent Researcher and, ideally, the arXiv preprint
3. Submit via ScholarOne at ieeeaccess.ieee.org; record the manuscript ID in STATUS
4. Expect a decision in 4 to 8 weeks; no revision cycle, only accept, reject-with-one-resubmission, or reject

## Key results (final)

- tl alpha 0.1 (p=10): shares 0.508 / 0.469 / 0.023; sd_pair 0.00282; near-tie needs 206 paired draws
- tl alpha 0.5 (p=10): shares 0.277 / 0.682 / 0.042; total variance about 10x smaller; near-tie resolves (-0.00218, Holm p=3.2e-6)
- l3 alpha 0.1 (p=10): share_P 0.000 truncated [0, 0.329]; share_PM 0.992; sd_pair 0.00770; near-tie needs more than 1000 paired draws
- Lead finding: six to ten draws reverses the 3B top-two order and multiplies the interaction component by 2.66
- Stack effect: torch build shifted 3B held-out loss by 8.4e-4, larger than the 6.7e-4 method gap

## Open items

- Domain email (optional but preferred)
- ScholarOne manuscript ID once submitted
- APC discount request to the editorial office if accepted
- If rejected: IJACSA fallback, and the OJ-CS paper's own decision is still pending
