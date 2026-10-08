# Implementation plan (archive)

Campaign phases A–O are complete and their narrative scaffolding was removed from
the public tree. Remaining work is manuscript finalization before `v1.0.0`.

## Phase P1: reference correction, limitations reframing, availability statement

Repo: fedlora-partition-variance
Branch: p1-refs-tone (create from current main)

RULES
- Add this phase to docs/IMPLEMENTATION_PLAN.md verbatim as a numbered phase BEFORE
  editing anything, then execute from the plan. No ad-hoc execution.
- Do not edit anything under analysis/ or results/. No aggregator or training-loop code.
- Do NOT tag, do NOT cut a release, do NOT touch Zenodo in this phase. See P1-12.
- Stop immediately on any failed acceptance check and report which check failed.
- Match on the quoted text, not on line numbers. Line numbers are hints only and may be
  off by one or two from your working tree.

----------------------------------------------------------------------
P1-1  manuscript/refs.bib: delete the entire dror2018hitchhiker entry.
      Reason: Dror et al. 2018 is cited for the Holm correction, but that paper states
      "we do not deal with the problem of drawing valid conclusions from multiple
      comparisons" and names only Bonferroni. It does not support the claim.

      Add this entry in its place:

@article{holm1979sequential,
  title={A simple sequentially rejective multiple test procedure},
  author={Holm, Sture},
  journal={Scandinavian Journal of Statistics},
  volume={6},
  number={2},
  pages={65--70},
  year={1979}
}

----------------------------------------------------------------------
P1-2  manuscript/sections/04_results.tex (around line 64):
      replace   \cite{dror2018hitchhiker}
      with      \cite{holm1979sequential}

      Then confirm: grep -rn "dror2018hitchhiker" manuscript/ returns nothing.

----------------------------------------------------------------------
P1-3  manuscript/refs.bib: replace these four entries entirely. Note that
      cho2024hetlora loses the author "Barnes, Matt", because the EMNLP 2024 archival
      version has five authors while the 2023 workshop version had six.

@inproceedings{yang2025federatedlora,
  title={Federated Low-Rank Adaptation for Foundation Models: A Survey},
  author={Yang, Yiyuan and Long, Guodong and Lu, Qinghua and Zhu, Liming and Jiang, Jing and Zhang, Chengqi},
  booktitle={Proceedings of the Thirty-Fourth International Joint Conference on Artificial Intelligence (IJCAI-25)},
  pages={10779--10787},
  year={2025}
}

@inproceedings{cho2024hetlora,
  title={Heterogeneous {LoRA} for Federated Fine-tuning of On-Device Foundation Models},
  author={Cho, Yae Jee and Liu, Luyang and Xu, Zheng and Fahrezi, Aldi and Joshi, Gauri},
  booktitle={Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing},
  pages={12903--12913},
  year={2024},
  doi={10.18653/v1/2024.emnlp-main.717}
}

@article{rodriguez2026recseeds,
  title={Training seeds and model-selection stability in recommender-system evaluation},
  author={Rodriguez, Juan Manuel and Lesota, Oleg and Tommasel, Antonela},
  journal={arXiv preprint arXiv:2609.02499},
  year={2026},
  note={Accepted at ACM RecSys 2026, Research and Practice Notes}
}

@inproceedings{ye2024fedllmbench,
  title={{FedLLM-Bench}: Realistic Benchmarks for Federated Learning of Large Language Models},
  author={Ye, Rui and Ge, Rui and Zhu, Xinyu and Chai, Jingyi and Du, Yaxin and Liu, Yang and Wang, Yanfeng and Chen, Siheng},
  booktitle={Advances in Neural Information Processing Systems 37: Datasets and Benchmarks Track},
  pages={111106--111130},
  year={2024}
}

----------------------------------------------------------------------
P1-4  manuscript/sections/02_related_work.tex (around line 24):
      This is the only LaTeX em dash (---) in the manuscript and it violates the
      project's no-em-dash rule.

      FIND:
stacks heterogeneous-rank adapters---contrasting with zero-padding heterogeneous LoRA~\cite{cho2024hetlora}---and compares

      REPLACE WITH:
stacks heterogeneous-rank adapters, in contrast with zero-padding heterogeneous LoRA~\cite{cho2024hetlora}, and compares

----------------------------------------------------------------------
P1-5  manuscript/sections/02_related_work.tex (around line 27):
      Accuracy fix. Jimenez-Gutierrez et al. run "five and ten distinct data partitions
      generated from fixed random seeds" (their Sec. 4 and 4.3), so calling them
      "random seeds" understates the closest prior work. Rodriguez et al. report that
      the model-selection effect is conditional, not universal.

      FIND (two consecutive sentences, ending just before "What has not been done"):
Rodriguez et al.~\cite{rodriguez2026recseeds} fix the data partition and vary only the training seed in recommender-system evaluation, finding detectable seed effects on metrics and model selection. In federated learning, the nearest work aggregates across runs to damp single-seed artifacts rather than decompose them: Jimenez-Gutierrez et al.~\cite{jimenez2025thorough} report means and standard deviations over five to ten random seeds when assessing non-IID impact, and NIID-Bench~\cite{li2022niidbench} varies an initial seed without separating the partition draw from the training seed.

      REPLACE WITH:
Rodriguez et al.~\cite{rodriguez2026recseeds} fix the data partition and vary only the training seed in recommender-system evaluation, reporting that seed variation is often detectable and that whether it changes model selection depends on how far apart the candidate configurations sit. In federated learning, the nearest work does resample the partition but pools the result into a single spread rather than decomposing it: Jimenez-Gutierrez et al.~\cite{jimenez2025thorough} run five and ten trials built from distinct data partitions with fixed random seeds and report mean accuracy with one standard deviation across trials, without separating the partition draw from the training seed or attributing variance to either; NIID-Bench~\cite{li2022niidbench} likewise varies an initial seed that controls both.

----------------------------------------------------------------------
P1-6  manuscript/sections/05_discussion.tex: replace the body of
      \subsection{Cross-scale reading} with the text below. This absorbs the content of
      the separate "No method recommendation" subsection, which P1-8 deletes. Keep the
      \subsection line itself.

On TinyLlama the partition share is substantial ($0.508$). On LLaMA-3.2-3B at $p{=}10$ the
interaction dominates ($0.992$) and the partition main-effect CI includes zero after
truncation, so we report no partition main effect at 3B. The cross-scale CIs on the
partition share overlap, and the two scales differ in more than parameter count:
TinyLlama-1.1B-Chat-v1.0 is instruction-tuned while LLaMA-3.2-3B is a base model, and the
base weights are float32 against float16. The design was therefore scoped to measure the
partition component within each scale rather than to attribute differences between them,
and the 3B IID floor is reported descriptively at $2$ degrees of freedom per method. The
within-scale conclusions do not depend on a scale comparison. We make no method
recommendation: the separable FFA-LoRA gaps are large and stable, the FedIT--FLoRA gap is
not, and the contribution is the measurement design and the conditioning of ranking
stability on effect size relative to partition-draw noise.

----------------------------------------------------------------------
P1-7  manuscript/sections/05_discussion.tex: replace the ENTIRE
      \subsection{Limitations} block, heading included, with the text below.

\subsection{Scope and limitations}
The design covers two model scales (1.1B and 3B), one dataset (Dolly), two heterogeneity
levels at 1.1B ($\alpha{=}0.1$ and $0.5$), three aggregators, $10$ clients with full
participation, $15$ rounds with one local epoch, and held-out next-token loss as the single
response. Generation benchmarks, additional datasets, partial participation, and larger
scales lie outside it, so the reported shares describe this apparatus rather than federated
LoRA in general. One property of the frozen federation, stated in
Section~\ref{sec:setup}, shapes what the partition draw varies: local updates apply only on
complete gradient-accumulation blocks, so the smallest clients at $\alpha{=}0.1$ contribute
no optimizer step. Communication is reported within method only, and RQ4 is exploratory and
is not used for claims.

Two measurement choices carry quantified bounds. LLaMA production holdouts run in float16;
the float32 spot-check in Section~\ref{sec:setup} bounds the difference at
$4.1{\times}10^{-5}$, about $250$ times below the $0.01$ effect scale used for power, so the
3B numbers are reported in float16. The mixed-model cross-check recovers the residual and
method-level components but not a separate partition component, as reported in
Section~\ref{sec:results}; the method-of-moments estimates are primary, as pre-registered.

The campaign's operational record is complete in the repository's decision log, and the two
items that touch the reported numbers are summarized here because measurement discipline is
the paper's subject. The held-out evaluation was amended mid-campaign to restore float32 for
TinyLlama (\texttt{freeze-v3.1}), and $15$ LLaMA held-out evaluations were recomputed so
that every reported value comes from one code path; the TinyLlama base loss is identical to
$10^{-6}$ across all freeze tags, so the amendment leaves the reported values unchanged.
Separately, $54$ extension cells trained on hosts that installed a torch build other than
the pinned 2.2.0+cu121 and were retrained on the pinned stack, with the originals retained
for comparison. That comparison is itself a measurement: the stack shift averages
$-8.5{\times}10^{-8}$ at 1.1B and $+8.4{\times}10^{-4}$ at 3B
($\mathrm{SD}\,3.0{\times}10^{-4}$, $n{=}15$), so at 3B an undeclared component of the
apparatus moved the metric by more than the FedIT--FLoRA gap of $0.00067$ under test. This
is the paper's argument arriving from the inside: components that go unreported are not
thereby small. All reported results use the pinned stack, and the release covers results and
metadata but not adapter weights.

----------------------------------------------------------------------
P1-8  manuscript/sections/05_discussion.tex: delete the entire
      \subsection{No method recommendation} block and its paragraph. Its content is now
      carried by the last sentence of P1-6. Section V goes from five subsections to four.

----------------------------------------------------------------------
P1-9  manuscript/sections/04_results.tex (around line 4):

      FIND:
We report TinyLlama and LLaMA-3.2-3B separately and do not recommend a method.

      REPLACE WITH:
We report TinyLlama and LLaMA-3.2-3B separately.

----------------------------------------------------------------------
P1-10 manuscript/main.tex, inside \section*{Declarations}, the
      \paragraph{Data and code availability.} block.

      Replace the whole paragraph body with:

Code, configurations, the pre-registered analysis plan, per-run metadata, and analysis
outputs are available at \url{https://github.com/jerryadamsfranklin/fedlora-partition-variance}
and archived at \url{https://doi.org/10.5281/zenodo.22861074}, which resolves to the most
recent archived version. The submitted snapshot is release \texttt{v1.0.0}. Adapter weights
are not included in the archive.

----------------------------------------------------------------------
P1-11 scripts/check_typography.py: add a rule that flags the LaTeX three-hyphen em dash
      (---) in .tex files, in addition to the existing Unicode U+2014 rule. Skip lines
      whose first non-whitespace character is %. Do not flag -- (en dash), which the
      manuscript uses legitimately in page ranges and in FedIT--FLoRA.

      Add a unit test asserting the new rule fires on a fixture line "a---b" and does not
      fire on "a--b", "a-b", or "% a---b". Add a CHANGELOG entry for the script change.

----------------------------------------------------------------------
P1-12 NO RELEASE IN THIS PHASE. Do not create a tag, do not cut a GitHub release, do not
      touch Zenodo. A single release v1.0.0 is cut later, only after Jerry's read-through
      and any follow-up phase, immediately before submission. Stop after P1-11 and report.

## Phase P2: novelty positioning and reviewer-objection pre-emption

Repo: fedlora-partition-variance. Branch: p2-positioning from main at ae7e1c9.
Add to docs/IMPLEMENTATION_PLAN.md as a numbered phase first, then execute from the plan.
Text only. No new runs. No changes under results/. Stop on any failed check.

P2-0  BEFORE any edit, output for review:
      git diff aec19af..ae7e1c9 -- scripts/verify_varpart.py analysis/claims.csv
      This is the outstanding A9 deviation from P1 and it gates the release. Paste it and
      continue with P2-1 onward; do not wait.

P2-1  refs.bib: add the four entries agarwal2021precipice, domini2025profed,
      jimenez2026crossdomain, grosser2026fedpretrain exactly as given in block P2-A.
P2-2  sections/02_related_work.tex: insert block P2-B after the Reimers and Gurevych
      sentence in subsection A, before "These lines of work motivate".
P2-3  sections/02_related_work.tex: replace the closing sentence of subsection B per
      block P2-C.
P2-4  sections/01_introduction.tex: replace the first two sentences of the "Advance over
      the state of the art" paragraph per block P2-D.
P2-5  sections/05_discussion.tex: insert block P2-E in subsection C immediately after
      "so we report no partition main effect at 3B."
P2-6  sections/05_discussion.tex: append block P2-F to the end of the first paragraph of
      "Scope and limitations".
P2-7  sections/03_setup.tex: append block P2-G in the variance-model subsection after
      "and $r{=}2$ training seeds per cell".

ACCEPTANCE CHECKS (stop on any failure)
B1  verify_varpart.py exits 0 on all four grids. P2-G introduces two derived counts (30
    within-cell differences; three to five IID training seeds). If V9 requires them
    registered, ADD them as new claims sourced from analysis/runs.csv and report the new
    total. Do NOT modify or delete any existing claim. Report the before and after counts
    and list any claim added.
B2  check_typography.py exits 0, --- rule active.
B3  Clean build. Zero undefined citations or references.
B4  Reference count in the compiled PDF is 31, numbered 1 to 31 with no gaps. Confirm all
    four new entries render and are cited in text.
B5  No prevalence words introduced. grep the new text for "usually", "rarely", "most
    papers", "typically", "commonly" and confirm none appear in the added blocks. Every
    claim about another paper must name that paper.
B6  Page count. 11 pages is acceptable at IEEE Access (no page limit, no overlength
    charge). Report the count. If the last page is ragged, confirm \balance is called.
B7  overlap_check.py against the OJ-CS tex files read in place, still under 5%.
B8  git diff --stat touches only manuscript/ and the two docs files. Nothing under
    results/. Report anything else BEFORE committing, do not proceed.

AFTER CHECKS PASS
- Commit on p2-positioning, merge to main, push. Log P2 in docs/DECISIONS.md.
- Report: the P2-0 diff, V9 counts before and after with any claim added, page count,
  overlap figure, and the rebuilt PDF.
- Do not tag. v1.0.0 comes after Jerry signs off.

## Phase P2 addendum: flow fixes, then commit and merge

Branch: p2-positioning (already holds the uncommitted P2 edits). Add to the plan first.

P2-H  sections/03_setup.tex, subsection "Variance model": cut the sentence beginning
      "With $p{=}10$ and $m{=}3$ the residual component is pooled over $30$..." from its
      current position and reinsert it verbatim immediately AFTER the sentence ending
      "...with negative estimates truncated at zero and truncation reported."
      No wording change.

P2-I  sections/01_introduction.tex: apply the replacement block P2-I (removes the word
      "commonly" and cross-references Section II). Confirm \ref{sec:related} resolves.

P2-J  Confirm, and state in your report, that the two verifier checks added for
      residual_pool_30 and iid_training_seeds_3_to_5 COMPUTE both values from
      analysis/runs.csv rather than comparing against hardcoded literals: the first by
      counting distinct (data_seed, method) groups at p=10, the second by counting
      distinct run_seed values per model in the IID cells. Demonstrate it: temporarily
      drop one IID row from a scratch copy of runs.csv, show the check FAILS, restore.
      A check that passes on mutated input is not a check. Report the demonstration.

RE-RUN B1 through B8 after P2-H and P2-I.
THEN commit on p2-positioning, merge to main, push. Log P2 in docs/DECISIONS.md. Do NOT tag.

## Phase P3: IID-floor ratio provenance (final pre-release)

Branch: p3-iid-ratio from main at 7b67182. Add to docs/IMPLEMENTATION_PLAN.md first.
Text plus claim registration only. No recomputation of any existing analysis output.

P3-1  sections/04_results.tex, subsection "IID noise floor": replace the first three
      sentences with the block above. The 0.82 value is
      s2_E(p=10) / pooled_iid_var = 2.5101979798593135e-07 / 3.06834472308735e-07
      = 0.8181, from analysis/variance_components_l3_p10.csv and analysis/iid_noise.csv.

P3-2  V9 audit. Report whether the following are already registered claims, and register
      any that are not, each COMPUTED from its source file, never hardcoded:
        - tl_iid_ratio       2.96  <- iid_noise.csv ratio_s2E_a01_over_iid model=tl
        - l3_iid_ratio_p6    0.43  <- iid_noise.csv ratio_s2E_a01_over_iid model=l3
        - l3_iid_ratio_p10   0.82  <- variance_components_l3_p10.csv s2_E
                                      / iid_noise.csv pooled_iid_var, model=l3
        - iid_floor_tl       6.40e-8 and iid_floor_l3 3.07e-7 <- iid_noise.csv
      Do not modify or delete any existing claim. Report the before and after counts and
      list every claim added.

P3-3  Demonstrate bite on the new checks as in P2-J: mutate pooled_iid_var in a scratch
      copy, show the ratio checks FAIL, restore. Report it.

P3-4  Add a one-line note to docs/DECISIONS.md recording that the pre-registered noise
      floor (I2) takes s2_E from I1, that I10 scopes the p=10 recomputation to I1, I3 and
      I4, and that the manuscript now reports both the six-draw and ten-draw ratios so
      the number is reproducible from either fit.

THEN commit, merge to main, push. Do NOT tag until Jerry confirms.

## Phase R: release v1.0.0

Add to docs/IMPLEMENTATION_PLAN.md first, then execute.

R-1  Metadata check BEFORE tagging. Read CITATION.cff and .zenodo.json. If either names a
     version other than 1.0.0, or a date other than today, update ONLY those fields in one
     metadata-only commit. Do not touch manuscript/, analysis/, results/, or scripts/.
     Re-run verify_varpart.py (expect 40/40) and confirm manuscript/main.pdf is
     byte-identical to bb19d0e (sha256 before and after). If there is nothing to change,
     tag bb19d0e directly.
R-2  Annotated tag v1.0.0 on that commit, message "IEEE Access submission snapshot". Push
     the tag.
R-3  Create a GitHub RELEASE from tag v1.0.0. Zenodo's integration fires on a release,
     not on a bare tag. Title "v1.0.0: IEEE Access submission snapshot".
R-4  Wait for Zenodo to ingest it. Confirm all three:
       a) https://doi.org/10.5281/zenodo.22861074 resolves to the v1.0.0 record
       b) the archived zip contains manuscript/main.pdf with the same sha256 as R-1
       c) the record's version field reads v1.0.0
     Record the new VERSION DOI in docs/DECISIONS.md and report it to me. Do NOT add it
     to the manuscript. The manuscript cites the concept DOI by design.
R-5  Report: tag commit hash, release URL, Zenodo version DOI, the sha256 of main.pdf,
     and the three R-4 confirmations.
STOP on any failed check. If Zenodo has not ingested after 30 minutes, report rather
than retry; a second release would mint a second version DOI.

## Phase P4: abstract length compliance (IEEE Access 150 to 250 words)

Branch: p4-abstract from main. Add to docs/IMPLEMENTATION_PLAN.md first.
HOLD Phase R until P4 is merged. (Note: v1.0.0 already tagged before this phase
was discovered; after P4, release strategy must be re-confirmed.)

P4-1  Replace the abstract body with the block above in BOTH places it lives:
      manuscript/main.tex (inlined before \maketitle) and
      manuscript/sections/00_abstract.tex. The two must be identical.
P4-2  Add an abstract word-count rule to scripts/check_typography.py: extract the abstract
      environment from main.tex, strip LaTeX commands and math delimiters, count
      whitespace-delimited tokens, and FAIL if the count is outside 150 to 250. Add a unit
      test with a 251-token fixture (must fail) and a 200-token fixture (must pass). Add a
      CHANGELOG entry.

CHECKS D1-D6; then commit, merge, push, and report.

## Phase P5: float citations, figure/table presentation, and provenance precision

Branch: p5-presentation from current main (post-P4). Add to docs/IMPLEMENTATION_PLAN.md
first. Phase R stays ON HOLD until P5 merges and Jerry/Claude sign off on the new PDF.
No new runs. No change to any analysis/*.csv. Presentation code changes need tests and a
CHANGELOG entry.

TEXT EDITS P5-1..P5-7, BIB P5-8..9, PRESENTATION P5-10..12, LAYOUT P5-13,
REGRESSION P5-14. Acceptance F1-F8. Then commit, merge, push. Do not tag.

## Phase P6: fix P5 regressions and add layout gates

Branch: p6-regressions from main at 8c08fb4. Add to docs/IMPLEMENTATION_PLAN.md first.
Phase R remains ON HOLD. No new runs. No analysis/*.csv changes except claims.csv.

P6-0  Explain why Table 3 lost alpha 0.5 rows (make_tables regenerate from a01-only loop).
P6-1..P6-8  Restore Table 3 (9 rows); fix Fig 1 caption; break IV-A share formula;
      floats between paragraphs; href for GitHub; target 10 pages; precise resumed-cells
      sentence with stop gate; define active vs effective clients.
G1--G3  Layout gates (overfull hbox >1pt; caption text in PDF; table row counts).
Acceptance H1--H5; then commit, merge, push. Do not tag.

## Phase P7: final polish (two edits)

Branch: p7-polish from main. Add to docs/IMPLEMENTATION_PLAN.md first. Phase R stays on
hold until Jerry confirms the P7 PDF.

P7-1  sections/03_setup.tex: "For the 8 resumed cells" -> "For the eight resumed cells".
P7-2  main.tex: remove \balance.

CHECKS K1--K3 (gates unchanged; 11 pages with single-column bio; word-level pdftotext
diff vs 06f69033). Then commit, merge, push. Do not tag.

## Phase P8: last-page layout and pre-release workspace check

Branch: p8-final from main at 4ac7546. Add to docs/IMPLEMENTATION_PLAN.md first.
Phase R stays on hold until Jerry confirms the P8 PDF.

P8-1..P8-3  Investigate untracked holdout dirs; scratch rebuild must stay at 204 rows;
      quarantine outside the repo only if not needed (else STOP).
P8-4  Gitignore LaTeX aux artifacts (*.fdb_latexmk, *.fls, ...).
P8-5  Insert \raggedbottom before bibliography; do not restore \balance.
CHECKS L1--L4; then commit, merge, push. Do not tag.

## Phase P9: repository completeness and page-11 layout

Branch: p9-complete from main at b27ec33. Add to docs/IMPLEMENTATION_PLAN.md first.
Phase R stays on hold.

COMPLETENESS
P9-1  Determine the file pattern used for the 150 already-committed cells (list the tracked
      file names under one committed prod_v1 cell, e.g. results.json, run_meta.json,
      partition_stats.json, instruction_holdout.json, config). Report it.
P9-2  For all 204 cells, determine the minimal file set a CLEAN CLONE needs so that:
      build_runs_table.py reproduces analysis/runs.csv byte-identically, and
      verify_varpart.py passes V1 to V12 on all four grids. Also include the
      quarantine_stackdrift originals needed for analysis/stack_effect.csv to regenerate
      identically. Exclude adapter weights and checkpoints (*.safetensors, *.bin, *.pt,
      *.pth, optimizer state, checkpoint dirs). Do not add stale duplicate holdouts that the
      builder would not select. Report the list of paths to add and the total size.
P9-3  Secret and PII scan of EVERY file in that list before staging: HF tokens (hf_...),
      GitHub tokens (ghp_, github_pat_), IPv4 addresses, host:port strings, ssh strings,
      absolute home paths containing usernames, emails other than
      jerry.adamsf@gmail.com. If anything is found, STOP and report the file and pattern.
      Do not redact silently.
P9-4  Size gate: if the total added size exceeds 50 MB, STOP and report the breakdown.
P9-5  Commit the file set. Record in docs/DECISIONS.md that 54 extension cells' metadata
      had been produced but never committed, and that this phase adds it.

LAYOUT
P9-6  main.tex: immediately before \begin{IEEEbiographynophoto}, insert
      \vspace{0pt plus -1fil}
      to cancel the class's "plus 1fil" stretch, leaving \raggedbottom to absorb the slack.
      If that does not close the gap, add to the preamble instead:
      \usepackage{etoolbox} and a \patchcmd on \IEEEbiographynophoto (or its internal
      macro) changing "plus 1fil" to "plus 0pt". Do NOT edit ieeeaccess.cls.

CHECKS (stop on any failure)
M1  CLEAN-CLONE GATE: git clone the pushed branch into a fresh temporary directory with
    no access to the local working tree. In that clone, install from requirements.txt in a
    fresh venv and run build_runs_table.py into a scratch path: 204 rows, byte-identical to
    analysis/runs.csv. Run verify_varpart.py for all four grids: exit 0, 44/44. Regenerate
    stack_effect.csv into a scratch path: identical to the committed file. Report all three.
M2  Measure page 11 from the rendered geometry, NOT pdftotext blank lines: use
    pdftotext -bbox-layout to get the y-coordinate of the last line of reference [31] and
    the first line of the biography. The vertical distance must be 72 pt or less.
    Report both coordinates.
M3  Word-level diff against the 142f38cb PDF: zero textual operations.
M4  All existing gates pass: check_typography, G1, G2, G3, abstract 150 to 250, 31 refs.
M5  git status --porcelain clean apart from adapter weights and other excluded artifacts,
    which must be covered by .gitignore. Report the .gitignore lines added.
THEN merge, push, send the PDF, its sha256, and the M1 and M2 reports. No tag.

## Phase R-prep (run now; NO tag, NO release, NO Zenodo action)

Add to docs/IMPLEMENTATION_PLAN.md. Base: main at 466bc39.
Expected PDF sha256: 74a4cb26571694dfe5c369542bb944aa5734c2029f8604cbdf7676816ba4cc2a
RP-1  State whether P9 M1 ran in a FRESH venv from requirements.txt. If not, rerun it that
      way (204 rows byte-identical, verify 44/44, stack_effect identical) and report.
RP-2  docs/REPRODUCE.md: add the Python requirement (>= 3.11; 3.12 verified) if missing.
RP-3  CITATION.cff and .zenodo.json: version 1.0.0. Leave the date field to be set at
      release time.
RP-4  Doc/metadata-only commit; manuscript/, analysis/, results/, scripts/ untouched.
      Confirm manuscript/main.pdf sha256 still equals the expected value. Push.
STOP. Report the commit hash. Do not proceed to tagging.

## Phase R-release (ONLY when Jerry says "release")

RR-1  Set the release date in CITATION.cff / .zenodo.json if required; metadata-only commit.
      Re-confirm the PDF sha256.
RR-2  Annotated tag v1.1.0 on that commit; push the tag. Do not move the existing v1.0.0 tag.
RR-3  GitHub release from v1.1.0, titled "v1.1.0: IEEE Access submission snapshot".
RR-4  After Jerry submits: confirm the concept DOI resolves to v1.1.0, the archived zip's
      main.pdf sha256 matches, and the version field reads v1.1.0. Record the version DOI
      in docs/DECISIONS.md only. If Zenodo has not ingested after 30 minutes, report;
      do NOT cut a second release.

## Phase P10: final text corrections (NO tag, NO release, NO Zenodo)

Branch: p10-text from main. Add to docs/IMPLEMENTATION_PLAN.md first.
STANDING RULE: no tag, release, or Zenodo action unless Jerry says "release".
Base PDF for diffing: sha256 74a4cb26571694dfe5c369542bb944aa5734c2029f8604cbdf7676816ba4cc2a

T1--T11  Text corrections (FFA directions, V6/row labels, order-of-magnitude wording,
      wrong→opposite ranking, ProFed/NIID-Bench wording, significance level 0.05,
      full-design mean gap, micro-batch parenthetical, availability v1.1.0).
T12  V9: gap_to_sdpair_tl (8), gap_to_sdpair_l3 (4); availability claim → v1.1.0 with
      negative assertion that v1.0.0 is absent. Bite-test each.

CHECKS X1--X4; then commit, merge, push. No tag, no release.

## Phase P11: final compliance and provenance (NO tag, NO release, NO Zenodo)

Branch: p11-final from main at 97509e6. Add to docs/IMPLEMENTATION_PLAN.md first.

P11-1  sections/04_results.tex, "Pre-registered claim mapping", last sentence. Replace
       "Cross-scale partition-share CIs overlap." with
       "Cross-scale partition-share CIs overlap, so the data cannot distinguish the two
       scales on the partition share."
P11-2  Check whether analysis/ in the CURRENT repo contains the LLaMA p=10 pairwise
       contrasts (fedit-flora +0.00067, CI [-0.00622, +0.00757], Holm 0.83; FFA-LoRA
       contrasts Holm 2.8e-6 and 6.1e-10). If not, generate
       analysis/method_pairwise_l3_p10.csv with the existing I5 code over data seeds
       2001-2010, without modifying method_pairwise.csv. Report the values.
P11-3  docs/DECISIONS.md: log that I5 (observed method differences) is reported at p=10
       for LLaMA, consistent with treating p=10 as primary under I10, although I10's text
       lists only I1, I3 and I4 for recomputation; the p=6 I5 values remain in
       method_pairwise.csv.
P11-4  V9: register, each computed from its CSV and bite-tested: tl fedit-flora Holm 0.57;
       tl FFA-LoRA contrasts Holm < 1e-8; l3 p=10 fedit-flora Holm 0.83 and CI
       [-0.00622, +0.00757]; l3 p=10 FFA-LoRA contrasts Holm < 1e-5; tl alpha 0.5
       fedit-flora -0.00218 and Holm 3.2e-6. Report counts.

CHECKS
Y1  Word diff against the 9e0e9ec0 PDF: exactly the P11-1 change plus reflow.
Y2  All gates pass (verify, typography, G1-G3, abstract, 31 refs, page-11 bbox).
Y3  Report the new PDF sha256. Commit, merge, push. No tag.
