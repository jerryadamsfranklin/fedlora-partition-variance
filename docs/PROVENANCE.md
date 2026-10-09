# Provenance

- Source repository: fedlora-protocols (private reference). IEEE Access uses single-anonymized review; the arXiv preprint is cited in the manuscript as reference [32].
- Source tag: ijacsa-fork-point
- Source commit: 96c40f7040313b8cd5d3ef3ea8362e5ccbcab981
- Export method: git archive (byte-identical, verified with SHA-256 at import)
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

## History rewrite of 9 Oct 2026

On 9 Oct 2026 the repository history was rewritten with git filter-branch to set
a single author and committer identity and to remove tool co-author trailers from
commit messages. File trees are unchanged. The run_meta.json files record the
original commit SHAs and are not edited. Each original commit is preserved under
an archive/* tag. Releases archived on Zenodo before this date were built from
the original commits.

| role | original SHA | archive tag | rewritten SHA | current tag | tree equal |
|---|---|---|---|---|---|
| freeze-v1 / run_meta (128 runs) | 0812fcf3bb1a31a7ad8ba126d0818d9f84ea3303 | archive/freeze-v1-original | aaab722c85136c0a7d306bd88621ec4c540be526 | freeze-v1 | yes |
| freeze-v3 / run_meta (1 run) | f3e773d763836d39415e0e6a9b0de4a49a67c506 | archive/freeze-v3-original | d9fc854e4ca85c2646e886bc6e10bd18dba0e2fb | freeze-v3 | yes |
| freeze-v3.1 / run_meta (141 runs) | 7cff2a4de03bb7e0ab4fecfb3601e278aabe7301 | archive/freeze-v3.1-original | 051eea430c3a1c99475e57d5b5e8f4db07cdb890 | freeze-v3.1 | yes |
| pre-rewrite main tip (P12) | de20c25b52cd1508b5f267e5e2a109aa0c165a29 | archive/pre-rewrite-main | daec4f6c1b2e508091597010f98bd1d7b3b88878 | (on main) | yes |
| v1.0.0 original base | e9ed8ec0a5ac9b9c784ad787626b30192eb2010c | archive/v1.0.0-original | 1b0f24783eb593b64ba9c3cd5e11e9fc0908d5d0 | v1.0.0 | yes |

Related release-tag originals (same rewrite; trees identical):

| role | original SHA | archive tag | rewritten SHA | current tag | tree equal |
|---|---|---|---|---|---|
| v0.9.0-n8-prep | 5f461eb9bf1227fdbc0f9b05d267bc56bc7082d7 | archive/v0.9.0-n8-prep-original | 54f559863c3e960f995e1cabcca16194bca1d7b7 | v0.9.0-n8-prep | yes |
| v0.9.1 | 7aaf54c3ba3eb2332d8fbc690fa06d965f0e56a3 | archive/v0.9.1-original | b93886953e181860a471c05c082104314667935d | v0.9.1 | yes |
| v0.9.2 | 353c78059579c06d746aa1470a73d2fed8d886f0 | archive/v0.9.2-original | 88877a228f8c62d60e1a64b7717548559b7e566f | v0.9.2 | yes |
