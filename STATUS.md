# STATUS

Last updated: 8 Oct 2026

Replace this file in the Claude Project whenever the state changes. Keep only one copy.
This file covers one paper: the partition-variance measurement study going to IEEE Access.

## Current phase

P8 merged at `b27ec33` (PDF sha256 142f38cb...). Manuscript text unchanged since P7 (zero
diff ops). Two blockers before release: (1) page-11 gap still ~25 lines; Cursor's check
counted pdftotext blank lines instead of measuring the page; (2) 54 extension cells' run
metadata and holdouts were never committed, so a clean clone cannot rebuild runs.csv or
pass V1. P9 (metadata commit + clean-clone gate + layout fix) handed to Cursor. Phase R ON
HOLD.

## Venue

IEEE Access, single-anonymized. Binary decisions, about 20% acceptance. Stage 3 desk screen
is the dominant risk. APC $2,160. No page limit. Abstract 150 to 250 words. Practical
submission cutoff December 2026 for a March 2027 filing.

## Decisions (8 Oct)

- Commit per-run metadata for all cells missing from the repo (weights excluded), so the
  availability statement is true and a clean clone reproduces runs.csv and the verifier
- Do not edit ieeeaccess.cls; cancel the biography's "plus 1fil" locally in main.tex
- Layout checks measure rendered geometry (pdftotext -bbox), never blank-line counts
- Accept 11 pages; one release only, v1.0.0, citing concept DOI 10.5281/zenodo.22861074

## Root causes recorded

- Page-11 gap: the class's \vskip 4\baselineskip plus 1fil before the biography competes
  with \raggedbottom's \vfil, splitting slack and centering the biography
- Untracked dirs: 54 extension cells' raw metadata and downstream holdouts (19 to 20 Sep,
  freeze-v3.1, torch 2.2.0+cu121) were produced but never git-added; the O11 Linux run
  verified the environment against the local tree, not repository completeness

## Final manuscript state (text frozen since P7)

- 31 references verified at primary sources; abstract 241 words; 11 pages
- V9 44/44, all claims computed from CSV and bite-tested; overlap 0%; fonts embedded
- Layout gates: no overfull hbox > 1pt, all caption text present, table row counts
- Novelty: no prior work separates partition and training seeds, decomposes, reports
  draws-needed, or conditions flip probability on effect size

## Done (7 to 8 Oct)

P1 `ae7e1c9` references and Limitations; P2 `7b67182` novelty; P3 `bb19d0e` IID-ratio
provenance; P4 abstract 297 to 241; P5 `8c08fb4` float citations; P6 regressions fixed and
layout gates; P7 `4ac7546` "eight", \balance removed; P8 `b27ec33` untracked dirs explained,
LaTeX artifacts gitignored, \raggedbottom added

## Next

1. Cursor runs P9: identify the committed file pattern; commit metadata for all missing
   cells after a secret/PII scan and a 50 MB size gate; clean-clone gate (runs.csv
   byte-identical, verify 44/44, stack_effect identical); cancel the biography stretch;
   measure page 11 by bbox
2. Sign-off on the P9 PDF and the clean-clone report
3. Phase R: metadata check, tag v1.0.0, GitHub release, Zenodo ingest, three checks,
   report version DOI and PDF sha256
4. Submit via ScholarOne with the sha256-matched PDF; plain-text abstract; cover letter
   names cited preprint arXiv:2609.13512 as a separate study with no reused results
5. Record the manuscript ID; revoke campaign GitHub and HF tokens

## Open items

- Author photo (300 dpi, 1 x 1.25 in) for final files if accepted
- Attorney: IEEE Access and the scholarly-articles criterion
- APC discount request, if accepted
- Three IJACSA project docs are obsolete and can be deleted

## Known residual risks (not blocking)

- Measurement plus protocol, not a method; Stage 3 may read it as good practice
- Two scales, one dataset, one metric; the mechanistic argument in V-D addresses it
- NeurIPS page ranges for refs 2 and 29 not independently confirmed
