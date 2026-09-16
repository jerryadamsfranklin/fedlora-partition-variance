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
