# IJACSA format and submission reference

Verified 18 Sep 2026 from thesai.org (Call for Papers, Author Guidelines, Downloads pages) and from published IJACSA article PDFs. Re-check before submitting; SAI changes these pages without notice.

## 1. Where the official template lives

thesai.org/Home/Downloads carries four items:

| Item | Use |
|---|---|
| Word Paper Format | .doc template, "paper format approved by The Science and Information (SAI) Organization" |
| Latex Paper Format | LaTeX template (ZIP), for papers prepared in LaTeX |
| IJACSA Copyright | Form to send completed and signed with the manuscript |
| IJACSA Archives | Past issues, useful as formatting reference |

The download links are served through a handler script rather than static file URLs, so they must be clicked from the Downloads page in a browser. Keep the downloaded ZIP in the repo under `manuscript/template/` so the format used is reproducible.

## 2. Format as observed in published IJACSA papers

The SAI LaTeX format is an IEEEtran-based two-column layout. Published articles show:

- Two columns, Times-family serif, roughly 10 pt body
- Running header: "(IJACSA) International Journal of Advanced Computer Science and Applications, Vol. X, No. Y, Year"
- Footer: "www.ijacsa.thesai.org" centered, with "N | P a g e" at the right
- Title centered, author block below with affiliation and email
- "Abstract—" run-in label, then "Keywords—" with semicolon-separated terms
- Roman numeral section headings (I, II, III), numbered subsections
- Numbered IEEE-style references in square brackets
- Figure captions below figures ("Fig. 1."), table captions above tables ("TABLE I.") in small caps

A minimal preamble consistent with this:

```latex
\documentclass[conference]{IEEEtran}   % paper size per the downloaded template
\usepackage{graphicx,amsmath,amssymb,booktabs,cite,url,hyperref,fancyhdr,balance}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\footnotesize (IJACSA) International Journal of Advanced Computer Science and Applications,}
\fancyhead[R]{\footnotesize Vol.\ , No.\ , 2026}
\fancyfoot[C]{www.ijacsa.thesai.org}
\fancyfoot[R]{\thepage \ $|$ P a g e}
\bibliographystyle{IEEEtran}
```

Prefer the values in the downloaded template over anything written from memory, including paper size.

## 3. Rules that carry rejection risk

| Rule | Source |
|---|---|
| Main body at most 10 pages, excluding references, tables, and figures | Call for Papers |
| No more than 25% previously published material by the same authors, all cited | Author Guidelines |
| No multiple submissions; nothing under review elsewhere | Call for Papers |
| Figures and tables placed where they appear in the text, never as separate files | Author Guidelines |
| Figures and images must be clear and easy to view | Author Guidelines |
| Citations, quotations, diagrams, tables, and maps must be accurate | Author Guidelines |
| Manuscript proofread before submission; no changes during review; minor revisions only after acceptance | Author Guidelines |
| Double-blind review by at least three reviewers | Call for Papers |
| Any GenAI use declared in the manuscript; GenAI cannot be an author; ideas, arguments, results, and conclusions must be the authors' | Author Guidelines |
| Non-compliance with the GenAI policy is treated as academic misconduct and can lead to removal of published work | Author Guidelines |
| Accepted formats: .docx, .doc, .pdf, LaTeX | Author Guidelines |
| Institutional email encouraged, not Gmail, Yahoo, or 163.com; valid ORCID iD encouraged | Author Guidelines |
| Plagiarism screening with iThenticate | Call for Papers |
| APC on acceptance, paid only through the secure link on thesai.org | Call for Papers |

## 4. Double-blind anonymization

- No author name, affiliation, acknowledgments, funding identifiers, or repository link in the review copy
- Code availability reads: "Code and run artifacts will be released upon acceptance."
- Self-citations in the third person; avoid "as we showed in [n]" and avoid naming the author in the text
- Strip PDF metadata: `\hypersetup{pdfauthor={}, pdftitle={}}`, then confirm with `pdfinfo`
- Check figure files for embedded absolute paths or usernames
- Author details go in the submission form and the camera-ready version only

## 5. Submission mechanics

- Submit at thesai.org/Publications/Submit?code=IJACSA
- Email subject format requested by the submission page: `IJACSA Paper Submission : "Paper Title"`
- Cover letter names the research domain; for this paper it should also name the related preprint (arXiv:2609.13512) and state that the present study uses new experiments, different methods, and a different research question
- Send the completed and signed IJACSA copyright form with the manuscript
- October 2026 issue (Vol. 17 No. 10): submission due 25 Sep 2026, review notification 15 Oct 2026, publication 31 Oct 2026

## 6. Fees (18 Sep 2026)

| Category | APC |
|---|---|
| Standard author | GBP 800 |
| Student author | GBP 750 |
| Reviewer-author | GBP 750 |
| Hard copy and certificate (optional) | GBP 100 |

Do not pay until the immigration attorney confirms an IJACSA publication carries weight.

## 7. Pre-submission checklist

- [ ] Official template ZIP downloaded from thesai.org and stored in `manuscript/template/`; paper size and class options match it
- [ ] Main body within 10 pages, excluding references, tables, and figures
- [ ] Figures and tables inline, legible at final size, fonts at least 8 pt
- [ ] Abstract and keywords in the template's format
- [ ] Section numbering and reference style match published IJACSA articles
- [ ] Review copy fully anonymized; PDF metadata empty, verified with `pdfinfo`
- [ ] Declaration on Generative AI present and accurate
- [ ] Overlap against the author's own prior work under the 25% limit, and all overlapping content cited
- [ ] Every reference verified against its primary source
- [ ] ORCID iD ready; non-Gmail email available if possible
- [ ] Signed copyright form attached
- [ ] Cover letter names the research domain and the related preprint
