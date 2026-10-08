# STATUS

Last updated: 8 Oct 2026

Replace this file in the Claude Project whenever the state changes. Keep only one copy.
This file covers one paper: the partition-variance measurement study going to IEEE Access.

## Current phase

P11 merged. I7 distinguish-scales clause restored; LLaMA p=10 and TinyLlama α=0.5 pairwise
tables committed; Holm contrasts registered in V9 (51/51). Awaiting Jerry's read-through
of the P11 PDF. No release work until Jerry says so.

## Venue

IEEE Access, single-anonymized. Binary decisions, about 20% acceptance. Stage 3 desk screen
is the dominant risk. APC $2,160. No page limit. Abstract 150 to 250 words. Practical
submission cutoff December 2026 for a March 2027 filing.

## Review method (agreed 8 Oct)

- No "signed off" or "ready" claims; each review states what was checked and what was not
- Final pass uses a fixed checklist: every number vs data, internal consistency,
  cross-references, claims about other papers vs sources, venue rules, mandates, every
  rendered page
- Stopping rule: after the final pass, only errors of fact, internal contradictions, or
  venue-rule violations reopen the manuscript

## Release state

- Zenodo concept DOI 10.5281/zenodo.22861074 (cited in the manuscript)
- Versions: 22861075 (v0.9.1), 22862931 (v0.9.2), 23226559 (v1.0.0, premature, P3-era).
  All permanent; the v1.0.0 tag is not to be moved
- Manuscript names v1.1.0 as the submitted snapshot; v1.1.0 is created only on Jerry's word
- After release: mark v1.0.0 superseded on GitHub and Zenodo (Jerry edits the 23226559
  description; same DOI)
- Standing rule for Cursor: no tag, release, or Zenodo action without Jerry saying
  "release"; every report lists tag and release actions

## Next

1. Jerry's read-through of the P11 PDF
2. On Jerry's word: R-release v1.1.0, then submit via ScholarOne with the sha256-matched
   PDF; plain-text abstract; cover letter names cited preprint arXiv:2609.13512 as a
   separate study with no reused results
3. Mark v1.0.0 superseded; record the v1.1.0 DOI and manuscript ID; revoke campaign tokens

## Open items

- Author photo (300 dpi, 1 x 1.25 in) for final files if accepted
- Attorney: IEEE Access and the scholarly-articles criterion
- APC discount request, if accepted
- Three IJACSA project docs are obsolete and can be deleted

## Known residual risks (not blocking)

- Measurement plus protocol, not a method; Stage 3 may read it as good practice
- Two scales, one dataset, one metric; the mechanistic argument in V-D addresses it
- NeurIPS page ranges for refs 2 and 29 not independently confirmed
