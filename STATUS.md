# STATUS

Last updated: 8 Oct 2026

Replace this file in the Claude Project whenever the state changes. Keep only one copy.
This file covers one paper: the partition-variance measurement study going to IEEE Access.

## Current phase

R-prep complete. Manuscript frozen at PDF sha256 74a4cb26... (unchanged). No tag, no
release. Awaiting Jerry's word for R-release (~10 minutes before ScholarOne submit).

## Venue

IEEE Access, single-anonymized. Binary decisions, about 20% acceptance. Stage 3 desk screen
is the dominant risk. APC $2,160. No page limit. Abstract 150 to 250 words. Practical
submission cutoff December 2026 for a March 2027 filing.

## Release rules (decided 8 Oct)

- Exactly one release, v1.0.0, cut by Jerry's call shortly before submitting
- No platform limit on releases, but each creates a permanent Zenodo version; the
  manuscript names v1.0.0, so a second release would mismatch the submitted PDF
- Submission does not wait on Zenodo: the manuscript cites concept DOI
  10.5281/zenodo.22861074, which already resolves; archive checks run after submitting
- The PDF sha256 at the tagged commit must equal 74a4cb26...

## Final state (signed off 8 Oct)

- 11 pages; 31 references verified at primary sources; abstract 241 words
- V9 44/44, every number computed from CSV and bite-tested; overlap 0%
- Layout gates pass; page 11 spacing measured by bbox (42.5 pt)
- Clean clone rebuilds runs.csv byte-identically and passes verify 44/44
- Novelty: no prior work separates partition and training seeds, decomposes, reports
  draws-needed, or conditions flip probability on effect size

## Next

1. On Jerry's word: R-release (set release date, tag v1.0.0, GitHub release)
2. Submit via ScholarOne with the sha256-matched PDF; plain-text abstract; cover letter
   names cited preprint arXiv:2609.13512 as a separate study with no reused results
3. After submitting: Zenodo checks; record version DOI in DECISIONS.md and the manuscript
   ID here
4. Revoke the campaign GitHub and HF tokens

## Open items

- Author photo (300 dpi, 1 x 1.25 in) for final files if accepted
- Attorney: IEEE Access and the scholarly-articles criterion
- APC discount request, if accepted
- Three IJACSA project docs are obsolete and can be deleted

## Known residual risks (not blocking)

- Measurement plus protocol, not a method; Stage 3 may read it as good practice
- Two scales, one dataset, one metric; the mechanistic argument in V-D addresses it
- NeurIPS page ranges for refs 2 and 29 not independently confirmed
