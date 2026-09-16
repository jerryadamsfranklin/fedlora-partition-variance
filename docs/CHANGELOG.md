# Changelog

All changes relative to the imported code, newest last.

Baseline test count at v0-import: 28 passed

- B1: write `partition_stats.json` after partitioning; fail loudly when
  `data.require_label_column` is true and the label column is missing
  (`resolve_label_source`); length-proxy fallback unchanged when not required.
