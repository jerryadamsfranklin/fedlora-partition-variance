# STATUS

Last updated: 20 Sep 2026

Replace this file in the Claude Project whenever the state changes. Keep only one copy.

## Current phase

Phase N8-5/N8-6 complete on the merged 204-cell set. N8-7/N8-8 hygiene in progress. Results prose (Phase O) unblocked for drafting from the clean N8-6 table; still no dual-submit.

## Venue

IEEE Access primary, IJACSA fallback. Single-anonymized review, no anonymization. About 20% overall acceptance; for this paper roughly 45 to 50% published at Access, with Stage 3 desk screening the dominant risk. APC $2,160. Never submit to both at once.

## Done

- Phases B to M under freeze-v1 and freeze-v2: 120 prod_v1 runs, verifier exit 0, complete manuscript drafted, overlap 0.082% against the OJ-CS body
- Phase N: 84 prod_v2 runs under freeze-v3.1; N6 repaired 15 LLaMA holdouts
- N7: census found 54 drifted-stack cells; analysis bugs fixed
- N8: 54 cells quarantined and retrained on 3 gated 4090s; manifest verified (54 complete, no duplicates, stack pin uniform); group integrity PASS; 11.2% hour spread
- N8-5: V1, V2, V2-cross-tag, V7, V12 PASS on tl+l3+tl_a05+l3_ext (204 cells)
- N8-6: `analysis/runs.csv` rebuilt (204); I8/I9/I10 recomputed; side-by-side at `analysis/n8_6_side_by_side.md`
- Repo public; release v0.9.0-n8-prep tagged; public repo scan found no credentials
- 27 references, all cited and verified

## Results status: clean N8-6 (use these)

Pre-registered rows selected (unchanged from 19 Sep text, recomputed on clean data):

- I8/I9: Gradient absent — all three difference CIs include zero; alpha 0.1 findings generalize over this range.
- I10: At p=10, LLaMA partition-share CI still includes zero; keep interaction-dominated 3B story; p=6 remains sensitivity.
- I10 note: s2_P truncated at zero at p=10; report trunc_P=True alongside the share CI.

**l3 top-two reversal SURVIVES retrain:** p=6 FedIT ahead of FLoRA by 0.00201; p=10 FLoRA ahead by 0.00067. Near-tie needs more than 1000 paired draws (was 953 on drifted).

Stable (prod_v1, unaffected): tl alpha 0.1 shares 0.508 / 0.469 / 0.023; s2_P 4.09e-6; sd_pair 0.00282; near-tie needs 206 paired draws.

## Next

1. N8-7: DECISIONS rows for the retrain and the superseded comparison (append)
2. N8-8: confirm IP/path redacts; forward commit
3. Phase O: Results, Discussion, Abstract, Conclusion; regenerate figures and tables; refresh V9
4. Jerry: destroy Taiwan 51661379 if still up; revoke campaign GitHub/HF tokens; enable Zenodo and cut v0.9.1 for the concept DOI

## Framing rules for the manuscript

- Lead with the Partition-Draw Reporting Protocol as the contribution
- Condition the flip claim on effect size; report the minimum detectable difference
- No partition main effect claim at 3B while the interval includes zero; report truncation
- The shares comparison across alpha is pre-registered; the absolute-variance comparison is post hoc and labeled as such
- RQ4 exploratory, uncorrected, not replicated at 3B
- Communication as measured, within method; no efficiency ranking
- No method recommendation
- Cross-scale comparisons confounded (instruction-tuned versus base; float32 versus float16 base weights)
- No prevalence claims about the literature
- Disclose: freeze-v3.1 mid-grid eval hotfix, 15 repaired LLaMA holdouts, the torch-stack retrain and what it confounded, the retry census, and the MixedLM cross-check status

## Open items

- Zenodo DOI, ORCID, submission email (blocking submission)
- Full ieeeaccess.cls template still needed
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
