# Provenance

- Source repository: fedlora-protocols (private reference). IEEE Access uses single-anonymized review; the arXiv preprint is cited in the manuscript as reference [26].
- Source tag: ijacsa-fork-point
- Source commit: 96c40f7040313b8cd5d3ef3ea8362e5ccbcab981
- Export method: git archive (byte-identical, verified with SHA-256 in CURSOR_TASK_01 step 3)
- Files imported: src/, tests/, requirements.txt, LICENSE, .gitignore, .gitattributes,
  scripts/run_experiment.py, scripts/evaluate_instruction_holdout.py,
  config/base_config.yaml, config/base_config_4layers.yaml, config/base_config_llama3_3b.yaml
- No results, analysis files, figures, or manuscript files were imported.

## Holdout float32 spot-check (limitations citation)

- Commit `ed80372` (`H: add verify_varpart and spotcheck float32 eval CLI`) added
  `--torch-dtype` / `--output-root` CLI flags to `scripts/evaluate_instruction_holdout.py`.
- That code produced `analysis/holdout_l3_fp32_spotcheck.csv` (max |fp16-fp32| tuned_loss
  about 4.1e-5), cited in the manuscript limitations.
- For freeze-v3 / prod_v2, the script was restored to the freeze-v2 blob so new cells pin
  the same eval path as prod_v1. The spot-check CLI is therefore not in HEAD; reproduce
  from `git show ed80372:scripts/evaluate_instruction_holdout.py` if needed.
