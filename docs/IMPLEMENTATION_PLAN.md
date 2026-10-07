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
