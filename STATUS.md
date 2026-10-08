# STATUS

Last updated: 8 Oct 2026

Replace this file in the Claude Project whenever the state changes. Keep only one copy.
This file covers one paper: the partition-variance measurement study going to IEEE Access.

## Current phase

P10 text corrections merged. Awaiting Claude's check of the changed sentences and Jerry's
own read-through of the P10 PDF. No release work until Jerry says so.

## Venue

IEEE Access, single-anonymized. Binary decisions, about 20% acceptance. Stage 3 desk screen
is the dominant risk. APC $2,160. No page limit. Abstract 150 to 250 words. Practical
submission cutoff December 2026 for a March 2027 filing.

## Release state

- Zenodo concept DOI 10.5281/zenodo.22861074 (cited in the manuscript)
- Versions: 22861075 (v0.9.1), 22862931 (v0.9.2), 23226559 (v1.0.0, premature, P3-era
  manuscript, lacks 54 cells' metadata). All permanent; v1.0.0 tag is not to be moved
- Submission snapshot will be v1.1.0, created only on Jerry's word
- After release: mark v1.0.0 superseded on GitHub (release notes) and Zenodo (Jerry edits
  the 23226559 description; same DOI)
- Standing rule for Cursor: no tag, release, or Zenodo action without Jerry saying
  "release"; every report lists tag and release actions

## Final manuscript state (post-P10)

- 11 pages; 31 references; abstract 231 source words; PDF sha256 9e0e9ec0…
- V9 46/46 (added gap_to_sdpair_tl=8, gap_to_sdpair_l3=4; availability v1.1.0)
- Layout gates pass; page-11 bbox gap 42.5 pt
- Clean clone (fresh Python 3.12 venv) rebuilds runs.csv byte-identically, verify 44/44
  (pre-P10); novelty claim unchanged

## Next

1. Claude checks the changed sentences and re-renders the pages
2. Jerry's own read-through of the P10 PDF
3. On Jerry's word: R-release v1.1.0, then submit via ScholarOne with the sha256-matched
   PDF; plain-text abstract; cover letter names cited preprint arXiv:2609.13512 as a
   separate study with no reused results
4. Mark v1.0.0 superseded; record the v1.1.0 DOI and manuscript ID; revoke campaign tokens

## Open items

- Author photo (300 dpi, 1 x 1.25 in) for final files if accepted
- Attorney: IEEE Access and the scholarly-articles criterion
- APC discount request, if accepted
- Three IJACSA project docs are obsolete and can be deleted

## Known residual risks (not blocking)

- Measurement plus protocol, not a method; Stage 3 may read it as good practice
- Two scales, one dataset, one metric; the mechanistic argument in V-D addresses it
- NeurIPS page ranges for refs 2 and 29 not independently confirmed
