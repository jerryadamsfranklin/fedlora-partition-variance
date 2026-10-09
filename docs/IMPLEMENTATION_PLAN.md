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

## Phase P12: heading hierarchy and method citations (NO tag, NO release, NO Zenodo)

Branch: p12-cites from main at 709d4f0. Add to docs/IMPLEMENTATION_PLAN.md first.
Base PDF for diffing: sha256 34f27884f7824d6da69d35e7232fb152e0851b9143e90ec08d5f698812ab287b

H1--H2  Introduction paragraphs → subsections; Declarations paragraphs → subsection*.
Bib: add Searle, Field, Seabold, Wilson, Lin, Hendrycks, Zheng. Citations C1--C8.
Confirm MixedLM / cluster bootstrap / Wilson / Jensen--Shannon in analysis scripts first.

CHECKS Z1--Z4; commit, merge, push. No tag.

## Phase P13: author photo + reference [5] capitalization (NO tag, NO release)

Branch: p13-photo from main at the P12 merge. Add to docs/IMPLEMENTATION_PLAN.md first.
Base PDF for diffing: sha256 7b4fd5fe91e9daac13382793c3db2cdb16fab602b1fba8d44f5e7f34d4e3a434

PHOTO
P13-1  Jerry provides the source photo (do NOT commit the original). From it, produce
       manuscript/frank.jpg: convert RGBA -> RGB on a white background, crop to exactly
       4:5 if needed (keep head and shoulders centred), resize to 600 x 750 px (1 x 1.25 in
       at 600 dpi), sRGB, JPEG quality 92. Strip ALL metadata (EXIF, XMP, ICC beyond sRGB).
       Verify with exiftool or PIL that no EXIF/XMP/GPS remains; report the output.
       File name follows the IEEE Access template rule (first five letters of surname).
P13-2  main.tex: replace
         \begin{IEEEbiographynophoto}{Jerry Adams Franklin}
       with
         \begin{IEEEbiography}[{\includegraphics[width=1in,height=1.25in,clip,keepaspectratio]{frank.jpg}}]{Jerry Adams Franklin}
       and the matching \end{IEEEbiographynophoto} with \end{IEEEbiography}.
       Keep the existing \vspace{0pt plus -1fil} immediately before it. Biography text
       unchanged.
P13-3  .gitignore: add common raw-photo patterns (*.heic, *_original.*) so no source photo
       is ever committed. Only manuscript/frank.jpg is tracked.

BIB
P13-4  refs.bib zheng2023judging title ->
       {Judging {LLM}-as-a-Judge with {MT-Bench} and {Chatbot Arena}}

CHECKS (stop on any failure)
Q1  Word diff against 7b4fd5fe: only reference [5]'s title, plus layout movement on the
    last page.
Q2  Rendered last page: photo at 1 x 1.25 in, left of the biography text, not clipped,
    not overlapping references; biography starts within 72 pt of the last reference
    (bbox); end mark after it. Report the page count.
Q3  pdfimages -list on the PDF: the photo's effective resolution >= 300 ppi.
Q4  All gates pass (verify 51/51, typography, G1-G3, abstract, 38 refs).
Q5  Report the new PDF sha256. Commit, merge, push. No tag.

## Phase P14: author biography (NO tag, NO release, NO Zenodo)

Branch: p14-bio from main at the P13 merge. Add to docs/IMPLEMENTATION_PLAN.md first,
then execute from the plan.
Base PDF for diffing: sha256 85ac9764f82223d8f85fc3e90fb98d6147c298d392970c9981074d1eb1bcc0f2

P14-1  main.tex, inside \begin{IEEEbiography}[...]{Jerry Adams Franklin} ... \end{IEEEbiography}:
       replace the ENTIRE biography text with exactly:

received the M.S. degree in data science from Northeastern University, Boston, MA, USA. He has worked as a deep learning engineer at Intel and as a senior AI/ML
engineer at Digital Currency Group. His research interests include federated learning
and resource-efficient fine-tuning of large language models.

       Do not change the heading, the photo argument, or the \vspace{0pt plus -1fil}
       before the environment.

CHECKS (stop on any failure)
B1  Word-level diff of pdftotext output against the 85ac9764 PDF: the only textual change
    is the biography text. Anything else, STOP and report.
B2  check_typography passes (no em dashes, no curly quotes, no "---").
B3  Render page 11 at 100 dpi and inspect: photo at 1 x 1.25 in on the left, biography
    beside it, nothing clipped or overlapping, end mark after the biography. Report the
    page count (expect 11).
B4  All gates pass: verify_varpart 51/51, G1 (no overfull hbox > 1pt), G2 (all caption
    text present), G3 (table rows), abstract 150 to 250 words, 38 references.
B5  git diff --stat touches only manuscript/main.tex, manuscript/main.pdf, and
    docs/IMPLEMENTATION_PLAN.md. Anything else, STOP.
THEN commit, merge, push. Report the commit hash and the new PDF sha256. No tag.

## Phase C1: repository cleanup and branch pruning (NO tag, NO release, NO Zenodo)

Add to docs/IMPLEMENTATION_PLAN.md first (it is deleted at the end of this phase; the
DECISIONS.md row below is the permanent record). Work on branch c1-cleanup from main.
HARD RULES: do not touch anything under manuscript/; do not rebuild the PDF;
manuscript/main.pdf must keep sha256
91ace17843fa3b8cb7c8642221c820ea2c424d641e09727732f6186cec5e22b4.
Do not edit src/, tests/, scripts/run_experiment.py, scripts/evaluate_instruction_holdout.py,
results/, analysis/*.csv, config/, figures/. Do not rewrite git history. No force-push.

STEP 0: BACKUP (before anything else)
C1-0  Outside the repo: git clone --mirror <origin> ~/fedlora-backup-mirror-20261009 and
      git -C <repo> bundle create ~/fedlora-backup-20261009.bundle --all
      Verify the bundle (git bundle verify). Report both paths. Never delete these.

STEP 1: BRANCH AND TAG AUDIT (report only; no deletions in this step)
C1-1  List every remote branch and every tag with its commit hash.
C1-2  Explain why p1-refs-tone ... p8-final and phase-c ... phase-o and
      docs-phase-b-decision show 86 to 98 commits ahead of main. For each, report
      git merge-base --is-ancestor <branch> main, and whether its tree content is in main
      (e.g. squash merge). If main's history was rewritten or force-pushed at any point,
      STOP and report what happened and when. Do not continue.
C1-3  Confirm these tags exist on origin: freeze-v1, freeze-v2, freeze-v3, freeze-v3.1,
      v0.9.0-n8-prep, v0.9.1, v0.9.2, v1.0.0. Confirm the commits recorded in every
      results/**/run_meta.json (0812fcf, f3e773d, 7cff2a4) are reachable from a tag.
C1-4  For each branch except main: git log --oneline <branch> --not main --tags. If any
      such commit hash is cited in docs/DECISIONS.md, docs/CHANGELOG.md or
      docs/PROVENANCE.md, create an annotated tag archive/<branch> on that branch tip
      and push it, so the cited commit stays reachable. Report which were tagged.

STEP 2: DELETE BRANCHES (only after Step 1 passes)
C1-5  Delete these remote and local branches, keeping main only:
      p14-bio p13-photo p12-cites p11-final p10-text p9-complete p8-final p7-polish
      p6-regressions p5-presentation p4-abstract p3-iid-ratio p2-positioning
      p1-refs-tone phase-o phase-n phase-j phase-i phase-h phase-d phase-c
      docs-phase-b-decision
      Do NOT delete any tag.

STEP 3: FILE CLEANUP on c1-cleanup
C1-6  git rm:
        STATUS.md
        docs/IMPLEMENTATION_PLAN.md
        docs/merged_configs.txt
        docs/partition_preview.txt
        analysis/logs/              (entire directory)
        scripts/watch_n8_loop.sh    (contains a rented-instance IP:port)
        scripts/ops/watch_prod_v2_health.sh
      First confirm with grep that no file in scripts/, src/, tests/ reads any of these
      paths. If one does, STOP and report.
C1-7  git mv (descriptive names) and update every reference to them:
        scripts/ops/o12_manuscript_precision.py -> scripts/check_manuscript_precision.py
        scripts/ops/o11_linux_verify.sh         -> scripts/verify_linux.sh
        scripts/ops/o11_docker_run.sh           -> scripts/verify_docker.sh
        scripts/ops/n6_reeval_batch.sh          -> scripts/reeval_llama_holdouts.sh
      Change verify_linux.sh to write its logs to logs/verify/ (gitignored) instead of
      analysis/logs/. Remove the now-empty scripts/ops/.
C1-8  README.md:
      - Repository map: delete the literature/ line (the folder does not exist); delete
        "process logs under analysis/logs/"; delete "partition preview and merged-config
        dumps"; describe scripts/ as launcher, holdout evaluation, analysis, verifier and
        reproducibility checks.
      - Add under grids/: "the *_n8_m*.yaml files are the per-machine grids used to
        retrain 54 cells on the pinned stack (manuscript Section V-D)".
      - Replace every em dash with a colon, comma or parentheses. No other content changes.
C1-9  docs/REPRODUCE.md:
      - "git checkout v0.9.2   # or a later archive tag" -> "git checkout v1.1.0   # the
        submission snapshot"
      - Update the verified-environment block: replace "33/33 claims" with the current
        verify_varpart claim count and "84 passed" with the current pytest count, and add
        the date these were re-run in C1-12.
      - Update the precision-check reference to scripts/check_manuscript_precision.py.
C1-10 .gitignore: add logs/ (if absent) and logs/verify/.
C1-11 docs/DECISIONS.md: APPEND one row (do not edit past rows):
      "9 Oct 2026 | Repository cleanup before submission: removed internal planning and
      status files, process logs, regenerable dumps, and campaign monitoring scripts
      (one contained a rented-instance address); renamed reproducibility scripts; pruned
      all branches except main. Provenance is carried by tags (freeze-v1, freeze-v2,
      freeze-v3, freeze-v3.1, release tags, and archive/* originals from C1a).
      | Public archive clarity | phase C1; backup bundle held offline"
      docs/CHANGELOG.md: add a matching entry.

STEP 4: CHECKS (stop on any failure)
K1  git diff --stat main...c1-cleanup shows nothing under manuscript/, src/, tests/,
    results/, analysis/*.csv, config/, figures/. sha256 of manuscript/main.pdf equals
    91ace178... .
K2  grep across tracked files (excluding docs/DECISIONS.md and docs/CHANGELOG.md) finds
    none of: IMPLEMENTATION_PLAN, STATUS.md, analysis/logs, partition_preview,
    merged_configs, watch_n8_loop, watch_prod_v2_health, o11_, o12_, n6_reeval,
    scripts/ops, literature/.
K3  No IPv4 address with a port in any tracked file at HEAD. "@gmail" appears only in
    manuscript/main.tex.
K4  pytest -q passes; report the count.
K5  CLEAN-CLONE GATE: push c1-cleanup, clone it into a fresh temp dir, create a fresh
    python3.12 venv from requirements.txt, then: build_runs_table over the four
    production grids = 204 rows byte-identical to analysis/runs.csv; verify_varpart
    exit 0 with all claims passing (report the count); regenerate stack_effect.csv into
    a scratch path, byte-identical to the committed file; check_typography passes.
C1-12 Put the K4/K5 counts and date into docs/REPRODUCE.md (C1-9), commit.
THEN merge c1-cleanup into main with git merge --ff-only, push, and delete the
c1-cleanup branch.
K6  git ls-remote --heads origin shows only main. git ls-remote --tags origin shows every
    tag from C1-3 plus any archive/* tags from C1-4.
REPORT: backup paths; the C1-2 explanation; archive tags created; files deleted and
renamed; K1 to K6 results; the final main commit hash; the PDF sha256 (must be 91ace178...).

## Phase C1a: Accept the 9 Oct 2026 history rewrite and preserve original commits (amends C1)

AUTHORIZATION (Jerry): I accept that main and the tags were rewritten on 9 Oct 2026
with git filter-branch. I authorize creating and pushing ONLY the annotated archive/*
tags defined in C1a-4. No other tag, release, or Zenodo action. Do not create GitHub
releases for archive tags.

HARD RULES
- No further history rewriting. No force-push of any ref. Never use --force or --tags.
- Do not move or delete any existing tag (freeze-*, v0.9.*, v1.0.0, v0.9.0-n8-prep).
- Do not touch manuscript/, src/, tests/, results/. manuscript/main.pdf sha256 must stay
  91ace17843fa3b8cb7c8642221c820ea2c424d641e09727732f6186cec5e22b4.
- Never delete backup/pre-author-rewrite-de20c25, the mirror, or the bundle.
- Stop on any failed check and report. Do not improvise fixes.

C1a-0 Log first. Append this phase with its checks to docs/IMPLEMENTATION_PLAN.md
  under C1. Commit "plan: C1a rewrite acceptance and archive tags". Normal push.

C1a-1 Inventory original commits.
  a. Collect distinct git commit SHAs from every results/**/run_meta.json, including
     results/quarantine_stackdrift. Print sha | run count.
  b. Add de20c25 (pre-rewrite main tip) and e9ed8ec (v1.0.0 original base).
  c. For v0.9.0-n8-prep, v0.9.1, v0.9.2, v1.0.0: print
     tag | current peel | original commit | rewritten (Y/N).
     Get originals from the Zenodo record file names (they contain the short SHA)
     or the backup bundle. If an original cannot be determined, print UNKNOWN.
  CHECK C1a-1: every SHA from (a) and (b) passes `git cat-file -e <sha>^{commit}`.
  Any missing -> STOP.

C1a-2 Prove the rewrite changed metadata only.
  Pairs: 0812fcf/aaab722, f3e773d/d9fc854, 7cff2a4/051eea4, de20c25/daec4f6,
  plus any release-tag pairs flagged rewritten in C1a-1c.
  CHECK C1a-2 (all must hold, print each):
   - git rev-parse <orig>^{tree} == git rev-parse <new>^{tree}
   - git diff --stat de20c25 daec4f6 is empty
   - git rev-list --count de20c25 == git rev-list --count daec4f6
  Any mismatch -> STOP.

C1a-3 Secret scan across ALL refs (old branches included).
  Run gitleaks detect over full history, or git log -p --all with patterns:
  hf_[A-Za-z0-9]{30,}, ghp_, github_pat_, AKIA[0-9A-Z]{16}, -----BEGIN,
  \b\d{1,3}(\.\d{1,3}){3}:\d{2,5}\b
  CHECK C1a-3: zero tokens or private keys. List host:port hits with file and commit
  (expected: scripts/watch_n8_loop.sh 60.250.87.179:59442). Report them; do not rewrite.
  Any token or key -> STOP, push nothing.

C1a-4 Create annotated tags locally. Message for each:
  "Original pre-rewrite commit. Rewritten twin: <new sha>. Trees identical
   (verified C1a-2). See docs/PROVENANCE.md."
   archive/freeze-v1-original    -> 0812fcf
   archive/freeze-v3-original    -> f3e773d
   archive/freeze-v3.1-original  -> 7cff2a4
   archive/pre-rewrite-main      -> de20c25
   archive/v1.0.0-original       -> e9ed8ec   (only if v1.0.0 now peels elsewhere)
   archive/<tag>-original        for each v0.9.x tag flagged rewritten in C1a-1c
   archive/run-commit-<short>    for any C1a-1a SHA not contained in the tags above
  CHECK C1a-4: for every SHA from C1a-1a, `git tag --contains <sha> | grep '^archive/'`
  is non-empty.

C1a-5 Push archive tags one by one: git push origin refs/tags/archive/<name>
  Record `gh release list` before and after.
  CHECK C1a-5: `git ls-remote --tags origin 'refs/tags/archive/*'` shows every tag
  with the peeled SHA from C1a-4. Release list unchanged (same count, same names).

C1a-6 Documentation (one commit on main, normal push).
  a. docs/PROVENANCE.md: new section "History rewrite of 9 Oct 2026". Table:
     role | original SHA | archive tag | rewritten SHA | current tag | tree equal.
     One row per C1a-1 SHA. Text:
     "On 9 Oct 2026 the repository history was rewritten with git filter-branch to set
     a single author and committer identity and to remove tool co-author trailers from
     commit messages. File trees are unchanged. The run_meta.json files record the
     original commit SHAs and are not edited. Each original commit is preserved under
     an archive/* tag. Releases archived on Zenodo before this date were built from
     the original commits."
  b. docs/DECISIONS.md: append one row in the existing format (append-only):
     "2026-10-09 | History rewrite accepted | main and tags were rewritten on 9 Oct 2026
     (git filter-branch; author identity and co-author trailers only; trees identical,
     verified C1a-2). Originals preserved under archive/* tags; mapping in
     docs/PROVENANCE.md. No further rewrites."
     Do not claim in any committed file that history was left unrewritten.
  c. REPRODUCE.md: one line stating that run_meta commit SHAs refer to original
     commits, with a pointer to the PROVENANCE mapping.
  d. CHANGELOG.md entry.
  CHECK C1a-6:
   - no committed file claims history was left unrewritten (search for that claim)
   - PROVENANCE table has one row per C1a-1 SHA
   - python scripts/verify_varpart.py exits 0, 51/51; print the V12 line verbatim
   - check_typography.py passes on changed docs (no em dashes)
   - PDF sha256 unchanged
  If V12 fails -> STOP and paste the output. Do not edit V12.

THEN RESUME C1 FROM C1-2 with these amendments:
- C1-2's "stop if history rewritten" check is replaced by C1a-2 passing.
- Before deleting any remote branch: git fetch --tags origin, re-run CHECK C1a-4
  against the fetched tags, and confirm `gh pr list --state open` is empty
  (if not, list the PRs and STOP).
- Delete remote branches with `git push origin --delete <branch>`, one per command.
  Keep only main.
- New K7: in a fresh clone, every C1a-1a SHA passes git cat-file -e, and the
  clean-clone gate passes (runs.csv 204 rows byte-identical, stack_effect.csv identical).
- New K8: origin tag list = pre-C1 tags + archive/* only; release list unchanged.
- Final report lists every tag, branch, and release action taken, with SHAs.
  STOP after C1a-6 and report C1a-1c + V12 before any branch deletion.

## Phase C1 resume (after C1a, verified 9 Oct 2026)

AUTHORIZATION (Jerry): Resume C1 from C1-3. Branch deletion is authorized subject to
C1-R1. No tag, release, or Zenodo action. No history rewrite. No force-push.
All C1 and C1a hard rules still apply (manuscript/, src/, tests/, results/ untouched;
PDF sha256 91ace17843fa3b8cb7c8642221c820ea2c424d641e09727732f6186cec5e22b4).

C1-R0 Log: append "C1 resume" with checks C1-R1..R3, K7, K8 to
  docs/IMPLEMENTATION_PLAN.md. Commit and push normally.

C1-R1 Branch containment (before any deletion).
  git fetch --all --tags --prune
  For each remote branch except main:
    contained = tip is an ancestor of main OR of any archive/* tag
    (git merge-base --is-ancestor <tip> <ref>)
  Print: branch | tip | contained (Y/N) | containing ref
  Delete ONLY contained branches: git push origin --delete <branch>, one per command.
  Non-contained branches: do NOT delete. Print commits unique to them
  (git log --oneline <tip> --not main $(git tag -l 'archive/*')) and leave them.
  CHECK C1-R1: gh pr list --state open is empty (else STOP before deleting anything);
  every deleted branch was contained.

C1-R2 Reports only (non-blocking):
  a. run_meta count by directory (results/<grid>/, results/quarantine_stackdrift/,
     any other) and by SHA; show how 270 relates to runs.csv 204 + quarantine 54.
  b. For each release tag original from C1a-1c: number of commits in the object store
     with that tree. Expected exactly 1 each.

C1-R3 Run the original C1 file-cleanup, README, and REPRODUCE steps, with this addition:
  no host:port or bare instance IP may remain in the CURRENT tree. scripts/watch_n8_loop.sh
  (60.250.87.179|59442) and the scan/report files containing host:ports are removed
  or redacted at tip only. Do not touch history.
  CHECK C1-R3: git grep -nE '\b([0-9]{1,3}\.){3}[0-9]{1,3}\b' HEAD returns no instance IPs
  (list any hits; version strings like 2.2.0 are fine).

Then run K1..K6 plus:
  K7 Fresh clone: every SHA 7cff2a4, 0812fcf, f3e773d passes git cat-file -e;
     clean-clone gate passes (runs.csv 204 rows byte-identical, stack_effect.csv identical);
     verify_varpart.py 51/51.
  K8 Origin tags = pre-C1 tags + 8 archive/* tags; gh release list = same 4 releases.

Final report: every branch deleted (with tip SHA), every branch kept and why,
every file removed or renamed, all tag/release actions (expected: none), K1..K8 results,
PDF sha256.
