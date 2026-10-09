# STATUS

Last updated: 9 Oct 2026

Replace this file in the Claude Project whenever the state changes. Keep only one copy.

## Current phase

Phase C1 (repo cleanup, branch pruning) stopped at C1-2: main and tags were rewritten
on 9 Oct with git filter-branch (author identity, co-author trailers). Phase C1a issued:
accept the rewrite, prove trees identical, secret-scan, push archive/* tags for original
commits, document the mapping, then resume C1. Release on hold until Jerry says "release".

## Venue

IEEE Access only. Single-anonymized; Accept / Reject with updates (one resubmission) /
Reject. Abstract 150 to 250 words. APC $2,160 billed after acceptance. Never dual-submit.
Practical submission cutoff December 2026 for March 2027 filing.

## Done

- All production runs on torch 2.2.0+cu121 RTX 4090; runs.csv 204 rows; V2 passes
- Analysis per ANALYSIS_PLAN I1 to I10 (p=10 primary per I10); pairwise CSVs added
- Manuscript final: main.pdf sha256 91ace178...5e22b4, 11 pages, 38 refs, abstract 241
  words, preprint is ref [32]; bio, photo, AI disclosure, declarations done
- Verifier 51/51 (V1 to V12, V9 claim map, bite-tested); layout gates G1 to G3;
  typography checks; clean-clone gate (Python 3.12 venv) passes
- All 38 references verified against primary sources; uncited claims fixed (P12)
- Novelty search: no prior partition-vs-training-seed decomposition found
- Zenodo concept DOI 10.5281/zenodo.22861074; CITATION.cff uses concept DOI
- Backups of repo before C1: mirror and bundle (verified), backup/pre-author-rewrite-de20c25

## Key results (from repo CSVs; V9 registered)

- l3 p=10 fedit vs flora: +0.00067, CI [-0.00622, +0.00757], Holm 0.830 (null)
- l3 p=10 FFA contrasts: Holm 2.77e-6 and 6.08e-10
- tl alpha 0.5 near-tie resolves: -0.00218, Holm 3.22e-6

## Next

1. Jerry confirms the 9 Oct rewrite was his request, then Cursor runs C1a
2. Review C1a-1c table and V12 line before any branch deletion
3. Resume C1: prune to main only, file cleanup, README and REPRODUCE fixes, K1 to K8
4. On "release": v1.1.0 from post-C1 main; verify PDF sha 91ace178
5. Submit via ScholarOne: plain-text abstract, keywords, cover letter; record manuscript ID

## Open items

- Revoke campaign GitHub and HF tokens (recommended now, not after submission)
- Zenodo record 23226559 (v1.0.0, premature): mark superseded after v1.1.0
- Website title inconsistency (Intel, Nokia, DCG titles) before submission
- IEEE membership plus Society for APC discount, decide before acceptance invoice;
  hardship request to apcinquiries@ieee.org only after acceptance
- Attorney: Early Access as publication

## Standing rules

- No tag, release, or Zenodo action without Jerry saying "release" (C1a archive tags
  carry an explicit one-off authorization)
- No further history rewrites, no force-push
- Every change logged in docs/IMPLEMENTATION_PLAN.md as a phase with checks
- Do not edit aggregator or training-loop code; v1.0.0 tag is not moved
