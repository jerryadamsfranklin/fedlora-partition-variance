# STATUS

Last updated: 9 Oct 2026

Replace this file in the Claude Project whenever the state changes. Keep only one copy.
This file covers one paper: the partition-variance measurement study going to IEEE Access.

## Current phase

P13 merged (PDF sha256 85ac9764f82223d8f85fc3e90fb98d6147c298d392970c9981074d1eb1bcc0f2,
11 pages, 38 references). Author photo `manuscript/frank.jpg` (600×750, metadata-
stripped) and reference [5] Chatbot Arena capitalization. Next: R-release v1.1.0 on
Jerry's word and ScholarOne submission.

## Venue

IEEE Access, single-anonymized. Decisions: accept (minor edits permitted); reject with
updates required (one resubmission, same reviewers); reject final. About 20% acceptance;
about 4 weeks to decision, 4 to 6 weeks to publication. APC $2,160 billed after
acceptance. Practical cutoff December 2026 for a March 2027 filing.

## APC (checked 9 Oct)

- Billed after acceptance via CCC/RightsLink; no stated deadline for discount requests
- IEEE member 5%; member plus IEEE Society 20% ($432); NOT for Student or Graduate Student
  members, so Jerry would need regular membership; join before the acceptance invoice
- Low-income-country program does not apply (US)
- Hardship: email apcinquiries@ieee.org after acceptance, before paying; no guarantee

## Decisions (8 to 9 Oct)

- IEEE Access is the venue; TMLR is not the fallback
- Author photo included at submission so no layout change is needed after acceptance;
  the original photo is never committed, only the stripped 600 x 750 copy
- Next paper: broader scope for a higher-tier venue; its own scope and approval

## Submission package

- PDF: sha256 85ac9764f82223d8f85fc3e90fb98d6147c298d392970c9981074d1eb1bcc0f2
- Cover letter: preprint is reference [32]
- Plain-text abstract (232 words source / ~241 PDF), keywords, title unchanged
- R-release block: expected sha256 and base commit = the post-P13 PDF and merge commit

## Release state

- Concept DOI 10.5281/zenodo.22861074 (cited in the manuscript)
- Versions: 22861075 (v0.9.1), 22862931 (v0.9.2), 23226559 (v1.0.0, premature). All
  permanent; v1.0.0 tag not to be moved
- v1.1.0 to be cut only on Jerry's word

## Next

1. Jerry pastes R-release with sha256 85ac9764...; submit via ScholarOne; record the ID
2. Jerry edits Zenodo record 23226559 description to "superseded"; revoke campaign tokens
3. Decide on IEEE regular plus Computer Society membership before any acceptance invoice

## Open items

- Attorney: IEEE Access and the scholarly-articles criterion
- Three IJACSA project docs are obsolete and can be deleted

## Known residual risks (cannot be resolved by checking)

- Stage 3 desk screen: a measurement plus protocol, not a method
- Two scales, one dataset, one metric; the mechanistic argument in V-D addresses it
- NeurIPS page ranges for FLoRA and FedLLM-Bench not independently confirmed
