# STATUS

Last updated: 20 Sep 2026

Replace this file in the Claude Project whenever the state changes. Keep only one copy.

## Current phase

Submission-ready. Read the final PDF end to end, then submit to IEEE Access via ScholarOne.

## Done

- 204 production cells, two models, three heterogeneity settings, all on torch 2.2.0+cu121 and RTX 4090; V1 to V12 pass
- Analysis I0 to I10 final on clean data; manuscript at 10 pages in ieeeaccess.cls, 27 verified references, author bio, ORCID in the author block
- Repo audit (O10): removed other-venue material and templates, neutralized the public status file, reorganized analysis logs and ops scripts, rewrote README, added docs/REPRODUCE.md, exported analysis/claims.csv
- O11: pinned environment verified on Linux (Python 3.12.14, python:3.12-slim-bookworm, amd64): 84 tests pass, analysis rebuilds over 204 cells, verifier 33/33. Regenerated CSVs match the archive at manuscript precision; last-digit BLAS differences documented rather than chased
- O12: committed the analysis fixes found during verification (LLaMA I1 scope p=6 per the analysis plan; comm.csv het schema and constant-active slope); main pushed; release v0.9.2
- O13: availability statement and V9 claim point at v0.9.2 (10.5281/zenodo.22862931); tip tagged `ieee-access-submitted-final` (earlier submission tags predate this pointer fix)
- Zenodo: concept DOI 10.5281/zenodo.22861074 resolves to v0.9.2; version DOI 10.5281/zenodo.22862931

## Next

1. Read the final PDF end to end
2. Submit via ScholarOne at ieeeaccess.ieee.org; record the manuscript ID here
3. Decision expected in roughly 4 to 8 weeks; outcomes are accept, reject with one resubmission, or reject

## Key results (final)

- tl alpha 0.1 (p=10): shares 0.508 / 0.469 / 0.023; sd_pair 0.00282; near-tie needs 206 paired draws
- tl alpha 0.5 (p=10): shares 0.277 / 0.682 / 0.042; total variance about 10x smaller; near-tie resolves (-0.00218, Holm p=3.2e-6)
- l3 alpha 0.1 (p=10): share_P 0.000 truncated [0, 0.329]; share_PM 0.992; sd_pair 0.00770; near-tie needs more than 1000 paired draws
- Lead finding: six to ten draws reverses the 3B top-two order and multiplies the interaction component by 2.66
- Stack effect: a torch build change shifted 3B held-out loss by 8.4e-4, larger than the 6.7e-4 method gap

## Open items

- ScholarOne manuscript ID once submitted
- APC discount request to the editorial office if accepted
- Other papers in flight: PeerJ CS survey status; OJ-CS decision pending
