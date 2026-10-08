# STATUS

Last updated: 8 Oct 2026

Replace this file in the Claude Project whenever the state changes. Keep only one copy.
This file covers one paper: the partition-variance measurement study going to IEEE Access.

## Current phase

P9 merged (metadata for 54 extension cells committed; biography `plus 1fil` cancelled
locally; clean-clone gate passed). Awaiting Jerry sign-off on the P9 PDF and M1/M2
reports. Phase R ON HOLD. Manuscript text unchanged since P7 (zero word-diff ops vs
142f38cb).

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
  with \raggedbottom's \vfil, splitting slack and centering the biography; cancelled with
  `\vspace{0pt plus -1fil}` before `\begin{IEEEbiographynophoto}`
- Untracked dirs: 54 extension cells' raw metadata and downstream holdouts (19 to 20 Sep,
  freeze-v3.1, torch 2.2.0+cu121) were produced but never git-added; now committed (P9)

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
LaTeX artifacts gitignored, \raggedbottom added; P9 metadata completeness + bio fil cancel
+ clean-clone gate

## Next

1. Sign-off on the P9 PDF and the clean-clone report
2. Phase R: metadata check, tag v1.0.0, GitHub release, Zenodo ingest, three checks,
   report version DOI and PDF sha256
3. Submit via ScholarOne with the sha256-matched PDF; plain-text abstract; cover letter
   names cited preprint arXiv:2609.13512 as a separate study with no reused results
4. Record the manuscript ID; revoke campaign GitHub and HF tokens

## Open items

- Author photo (300 dpi, 1 x 1.25 in) for final files if accepted
- Attorney: IEEE Access and the scholarly-articles criterion
- APC discount request, if accepted
- Three IJACSA project docs are obsolete and can be deleted

## Known residual risks (not blocking)

- Measurement plus protocol, not a method; Stage 3 may read it as good practice
- Two scales, one dataset, one metric; the mechanistic argument in V-D addresses it
- NeurIPS page ranges for refs 2 and 29 not independently confirmed
