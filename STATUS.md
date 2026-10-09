# STATUS

Last updated: 9 Oct 2026

Replace this file in the Claude Project whenever the state changes. Keep only one copy.

## Current phase

Phase C1 (repo cleanup, branch pruning) resumed after C1a passed. Branches deleted only
if contained in main or an archive/* tag. Release on hold until Jerry says "release".

## Venue

IEEE Access only. Single-anonymized; Accept / Reject with updates (one resubmission) /
Reject. Abstract 150 to 250 words. APC $2,160 billed after acceptance. Never dual-submit.
Practical submission cutoff December 2026 for March 2027 filing.

## Done

- All production runs on torch 2.2.0+cu121 RTX 4090; runs.csv 204 rows; V2 passes
- Analysis per ANALYSIS_PLAN I1 to I10 (p=10 primary per I10); pairwise CSVs added
- Manuscript final: main.pdf sha256 91ace178...5e22b4, 11 pages, 38 refs, abstract 241
  words, preprint is ref [32]; bio, photo, AI disclosure, declarations done
- Verifier 51/51 (V12 PASS after rewrite); layout gates G1 to G3; typography checks;
  clean-clone gate passes
- All 38 references verified; uncited claims fixed (P12); novelty search clean
- Zenodo concept DOI 10.5281/zenodo.22861074; CITATION.cff uses concept DOI
- Backups before C1: mirror, bundle, backup/pre-author-rewrite-de20c25
- C1a: 9 Oct filter-branch rewrite accepted; trees identical (de20c25/daec4f6, 106
  commits each); no tokens or keys in any ref; 8 archive/* tags pushed (3 freeze
  originals, pre-rewrite main, 4 release originals); PROVENANCE mapping, DECISIONS row,
  REPRODUCE note in 482575a; releases unchanged (4)
- run_meta SHAs: 7cff2a4 x141, 0812fcf x128, f3e773d x1, all reachable via archive tags

## Key results (from repo CSVs; V9 registered)

- l3 p=10 fedit vs flora: +0.00067, CI [-0.00622, +0.00757], Holm 0.830 (null)
- l3 p=10 FFA contrasts: Holm 2.77e-6 and 6.08e-10
- tl alpha 0.5 near-tie resolves: -0.00218, Holm 3.22e-6

## Next

1. C1 resume: containment check, prune contained branches, file cleanup, README and
   REPRODUCE fixes, remove instance IPs from tip, K1 to K8
2. Review C1-R2 reports (270 run_meta breakdown, tree-match uniqueness) and any
   non-contained branches
3. On "release": v1.1.0 from post-C1 main; verify PDF sha 91ace178
4. Submit via ScholarOne: plain-text abstract, keywords, cover letter; record manuscript ID

## Open items

- Revoke campaign GitHub and HF tokens (recommended now)
- Zenodo record 23226559 (v1.0.0, premature): mark superseded after v1.1.0
- Website title inconsistency (Intel, Nokia, DCG titles) before submission
- IEEE membership plus Society for APC discount, decide before acceptance invoice;
  hardship request to apcinquiries@ieee.org only after acceptance
- Attorney: Early Access as publication

## Standing rules

- No tag, release, or Zenodo action without Jerry saying "release"
- No further history rewrites, no force-push; never delete C1 backups
- Every change logged in docs/IMPLEMENTATION_PLAN.md as a phase with checks
- Do not edit aggregator or training-loop code; existing tags are never moved
