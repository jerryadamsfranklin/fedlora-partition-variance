# Changelog

All changes relative to the imported code, newest last.

Baseline test count at v0-import: 28 passed

- B1: write `partition_stats.json` after partitioning; fail loudly when
  `data.require_label_column` is true and the label column is missing
  (`resolve_label_source`); length-proxy fallback unchanged when not required.
- B2: `run_meta.json` records `git_dirty_tracked`, `git_describe`, `hardware`,
  and `wall_clock_s` after training; legacy `git_dirty` unchanged.
- B3: held-out Dolly formatter includes `### Context:` when present (matches
  training); JSON records `formatter_version=v2-dolly-context` and `eval_dtype`.
  Formatter test uses hard-coded strings from `client.py` (no FederatedClient
  construction).
- B4: add `scripts/make_vp_configs.py` (12 `config/vp/*.yaml`),
  `scripts/print_merged_config.py`, and `docs/merged_configs.txt` (dump later removed in C1); list merge
  replaces base `target_modules` with q_proj/v_proj.
- B5: grids `grids/tl.yaml` and `grids/l3.yaml`, launcher `scripts/run_grid.py`,
  status tool `scripts/grid_status.py` (enumerate, shard, production guard).
- B6: add `scripts/vast_setup.sh` for Vast.ai instance bootstrap (clone freeze-v1,
  deps, HF login, prefetch, pytest).
- C: `scripts/inspect_partitions.py` and `docs/partition_preview.txt` (dump later removed in C1) for Dolly
  train[0:3000] label_skew alpha=0.1, seeds 2001 to 2010.
- C addendum: effective clients and discarded trailing samples (optimizer steps
  only on complete accumulation blocks); pre-registered in I6 and limitations.
- D: Mac smoke tests (smoke report not retained); classify orphan run folders in
  run_grid/grid_status; TinyLlama per-client upload 9,011,200 bytes (FedIT/FLoRA;
  FFA upload same, download B-only 3,244,032).
- D fix: shard by (het, data_seed, run_seed) group so all methods share a GPU;
  tl counts 27/24/24 and l3 15/15/15 for three shards.
- G/H: LLaMA holdout eval uses float16 on CUDA and frees the tuned model before
  loading the base (sequential load); TinyLlama holdouts remain float32.
- H: `scripts/verify_varpart.py` (V1-V11); V4 scoped by het; V7 records eval_dtype;
  V10 resume/retry census; V11 eval-script provenance vs freeze-v2.
- H close: float32 spot-check evidence committed; Phase K audit dropped in DECISIONS.
- I: `scripts/analysis/build_runs_table.py` and `analyze_variance.py` (I0 to I6);
  outputs under `analysis/*.csv`.
- I addendum: pair-level flip table (`rank_flip_pairs.csv`) and observed-gap power rows.
- J: `make_figures.py` (Figs 1 to 3, pair panel on Fig 2) and `make_tables.py` (Tabs 1 to 3).
- J fix: figures at 505 pt full width with >=8 pt fonts; Tab1 LoRA alpha notation;
  Tab2 design p/m/r and no-truncation note; I7 claim wording for l3 near-tie.
- L: draft Setup section (`manuscript/sections/03_setup.tex`).
- N1-N4: TinyLlama alpha 0.5 configs (15 total); grids `tl_a05` and `l3_ext`;
  ANALYSIS_PLAN I8 to I10; V12 training-path freeze check; tag `freeze-v3`.
  Holdout eval restored to the freeze-v2 blob so V12 can pin prod_v2 eval.
- N5 runbook: `docs/PHASE_N_RUNBOOK.md` (RTX 4090 name gate, stagger, tl then l3).
- N5a-d: grid `freeze_tag` + production_guard; partition preview append;
  V7 cross-tag base_loss pooling; DECISIONS/PROVENANCE for ed80372 spot-check.
- O10: pin `statsmodels==0.14.1` and drop unused `torchvision`/`torchaudio`/
  `wandb`/`seaborn`/`scikit-learn` from `requirements.txt`; V9 exports
  `analysis/claims.csv`; delete `docs/IJACSA_FORMAT_AND_SUBMISSION.md` and
  `manuscript/template/` (SAI zip + IJACSA copyright PDF); public STATUS;
  move process logs to `analysis/logs/` and campaign scripts to `scripts/ops/` (both later removed from the public tree in C1);
  rewrite README and add `docs/REPRODUCE.md`.
- O11: Linux Docker verify of the pinned stack (`python:3.12-slim-bookworm`
  linux/amd64, 2026-09-20): 84 tests, full analysis over 204 cells,
  `verify_varpart` 33/33. Byte-level CSV regen differs at ULP across OpenBLAS;
  archive left unchanged. Exposed two regeneration bugs fixed in O12.
- O12: `analyze_variance.py` — LLaMA primary I1 restricted to p=6 (seeds
  2001–2006) per ANALYSIS_PLAN when `l3_ext` is present; `comm.csv` keeps
  per-het rows (`het` column) and constant-active origin slopes. Fresh
  regeneration now reproduces the committed archive at manuscript precision.
  Document verified environment and numerical reproducibility in REPRODUCE.
- O13: availability statement points at submitted snapshot `v0.9.2`
  (10.5281/zenodo.22862931); V9 claim updated. Earlier tags
  `ieee-access-submitted` / `ieee-access-submitted-v1` and Zenodo `v0.9.1`
  predate this pointer fix (and the O12 analysis fixes); tip tagged
  `ieee-access-submitted-final`. No new Zenodo release (code unchanged).
- Docs cleanup: remove campaign scaffolding from the public tree
  (internal planning log `IMPLEMENTATION_PLAN.md` (not public),
  `PHASE_N_RUNBOOK.md`, phase/smoke reports, `STATUS.md`). Keep
  pre-registration and archive docs (`ANALYSIS_PLAN`, `SCOPE`, `DECISIONS`,
  `PROVENANCE`, `REPRODUCE`, `CHANGELOG`).
- P1: `scripts/check_typography.py` also flags LaTeX `---` em dashes in `.tex`
  files (comment lines skipped; `--` still allowed). Unit test added.
  Manuscript: Holm 1979 citation; bib/related-work accuracy; limitations
  reframed; availability uses concept DOI + `v1.0.0` tag (no release cut).
- P4: abstract shortened to IEEE Access 150--250 words; `check_typography.py`
  fails outside that range on `main.tex` (unit tests for 251-fail / 200-pass).
- P5: cite every float in order; Fig.~1 caption carries cluster order (no
  in-axes labels); Fig.~2 legends use FedIT/FFA-LoRA/FLoRA; tables use
  ${\times}10^{k}$ (no e-notation) and round-half-up comm ranges; bib titles
  FederatedGPT and non-IID; resumed-cell sibling diffs registered in V9;
  `check_typography` requires every `fig:`/`tab:` label to be referenced.
- P6: restore Table~3 $\alpha{=}0.5$ rows; shorten Fig.~1 caption (ieeeaccess
  `tabular{l}` does not wrap); break IV-A share formula; floats between
  paragraphs; GitHub `\href`; precise resumed-cell max/median/max wording;
  define active vs effective clients; `check_layout.py` gates G1--G3.
- P7: spell out ``eight'' resumed cells; drop `\balance` so the biography
  stays in one column on the final page.
- P8: `\raggedbottom` before the bibliography; gitignore `*.fdb_latexmk` /
  `*.fls`. Untracked l3_ext holdout dirs left in place (required for 204-row
  rebuild); page-11 spacing is the class biography `\vskip 4\baselineskip plus 1fil`.
- P9: commit metadata for 54 extension cells (raw + holdout mirrors; weights
  excluded) so a clean clone rebuilds `runs.csv` and passes V1–V12; cancel
  biography `plus 1fil` with `\vspace{0pt plus -1fil}` in `main.tex`; measure
  page-11 gap by `pdftotext -bbox-layout`.
- R-prep: document Python ≥ 3.11 (3.12 verified) for byte-identical
  `stack_effect.csv` regen; keep `CITATION.cff` / `.zenodo.json` at version
  1.0.0 with release date deferred to R-release. No tag.
- P10: correct FFA download wording; replace repo-internal V6/row labels; bound
  separable gaps as 4×–8× paired SD; ``opposite'' ranking; significance level
  0.05; full-design mean gap; micro-batch parenthetical; availability `v1.1.0`;
  V9 `gap_to_sdpair_{tl,l3}`. No tag.
- P11: restore I7 ``cannot distinguish the two scales'' clause; add
  `method_pairwise_l3_p10.csv` and `method_pairwise_tl_a05.csv`; register Holm
  contrasts in V9. No tag.
- P12: promote intro/Declarations headings; cite MMLU, MT-Bench, Dirichlet,
  FedAvg, Searle, Field, MixedLM, Wilson, Lin, TinyLlama, Llama~3; seven new
  refs (31→38). No tag.
- C1a: accept the 9 Oct 2026 filter-branch rewrite (author identity and co-author
  trailers only; trees identical). Push annotated `archive/*` tags for original
  freeze, release, and pre-rewrite-main commits; document the mapping in
  `docs/PROVENANCE.md`. No release.
- C1: remove internal planning/status files, process logs, regenerable dumps, and
  campaign watchers (including a rented-instance address at tip); rename
  reproducibility scripts (`check_manuscript_precision.py`, `verify_linux.sh`,
  `verify_docker.sh`, `reeval_llama_holdouts.sh`); prune all remote branches except
  `main`; fix README map and REPRODUCE checkout/claim counts. No tag.
- C2: add gitignored `.internal/` for local planning logs; fix dangling
  references after C1 (DECISIONS append for removed planning paths). Manuscript
  and PDF text contain no removed-path hits. No tag.
- C3: V12 requires empty training-path diff freeze-v1..freeze-v3.1 (manuscript
  Section III); unit tests for the check; PROVENANCE preprint ref [32]; README
  provenance wording and spacing; REPRODUCE/CHANGELOG nits. No tag.
