# STATUS

Last updated: 18 Sep 2026

Replace this file in the Claude Project whenever the state changes. Keep only one copy.

## Current phase

Phase N pre-launch complete on phase-n / freeze-v3 (f3e773d). GPUs being rented; runbook is docs/PHASE_N_RUNBOOK.md. Phase O2b done (43fc0a7); O2c reference expansion done (refs.bib 27).

## Standing rule

Every change request goes into docs/IMPLEMENTATION_PLAN.md as a numbered phase with acceptance checks, then is executed from the plan.

## Done

- Phases B to M under freeze-v1 and freeze-v2: 120 runs, verifier exit 0, 7-page manuscript, overlap 0.082%
- Phase N: N1 to N4 (configs, grids, pre-registered I8 to I10, V12 pass), N5a to N5d (freeze_tag guard, partition preview, V7 pooling check, provenance)
- Partition preview: alpha 0.5 keeps 10 active clients in every seed; alpha 0.1 seeds 2007 to 2010 minimum 9 (seed 2008); both blocks 8 categories summing to 3000
- V7 pooling: base_loss 2.120666 (tl, 75 holdouts) and 2.168946 (l3, 45 holdouts) within 1e-6
- Phase O2b: gap claim narrowed; five new references verified (unlearning ICC, SAE benchmark, recommender seeds, JII non-IID assessment, FlowerTune)
- Phase O2c: thirteen foundation/context/stats references added with home sentences; refs.bib at 27; O2c-5 corrected Cho (FLoRA bib venue) and LoRA (S2/DBLP ICLR confirmation)

## Next

1. Rent 3 RTX 4090s (exact gpu_name gate, new read-only tokens, staggered launches); run tl_a05 shards 0 to 2, then l3_ext on the same boxes
2. First-cell gate: git_describe freeze-v3, gpu_name exact, base_loss 2.120666; stop on any drift
3. Sync adapters from the start; 84 adapters on the Mac before destroying any instance
4. Analysis I8 to I10, then Phase O rework for IEEE Access
5. Target submission Fri 26 Sep; hard stop on runs Mon 22 Sep

## Findings to carry into the paper

- Alpha 0.5 partitions keep all 10 clients active; alpha 0.1 yields 9 or 10. Report as a partition statistic alongside the variance components
- Gap claim names adjacent decompositions (unlearning seeds, benchmark variants, fixed-partition seed studies) rather than claiming none exist
- Cite the JII non-IID assessment as 2026, volume 50, article 101052

## Venue

- IEEE Access primary: about 20% acceptance, 4 weeks to decision, 4 to 6 weeks to publication, APC $2,160. Desk-screen risk mitigated by the Partition-Draw Reporting Protocol framing and the alpha gradient
- IJACSA fallback (November or December cycle); never both at once
- Odds after the addendum: desk reject 25 to 30%; publication before March 2027 roughly 45 to 55%

## Open items

- Cabells Predatory Reports check on IJACSA (fallback only)
- Attorney: IEEE Access and the scholarly-articles criterion; Early Access as publication for the OJ-CS paper
- ORCID, non-Gmail email, public repo plus Zenodo DOI
- prod_v1 adapters gone (25 of 120); retain every prod_v2 adapter
- Local tooling: use .venv/bin/python

## Run progress

| Grid | Complete | Total | Tag |
|---|---|---|---|
| tl (alpha 0.1 + IID) | 75 | 75 | prod_v1 |
| l3 (alpha 0.1 + IID) | 45 | 45 | prod_v1 |
| tl_a05 | 0 | 60 | prod_v2 |
| l3_ext | 0 | 24 | prod_v2 |
