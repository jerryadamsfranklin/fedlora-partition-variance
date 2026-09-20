# Partition Draws, Not Aggregators

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22861074.svg)](https://doi.org/10.5281/zenodo.22861074)

This repository archives the measurement study behind *Partition Draws, Not
Aggregators*: how much of the variance in federated LoRA held-out loss comes from
the Dirichlet partition draw versus the training seed, and how often method
rankings reverse when the evaluation draws a different partition.

## Headline results

- TinyLlama at Dirichlet alpha 0.1: partition / interaction / residual shares
  0.508 / 0.469 / 0.023.
- LLaMA-3.2-3B at p=10: interaction share 0.992; the partition-share confidence
  interval includes zero.
- Extending LLaMA from six to ten partition draws reverses the top-two method
  order and multiplies the interaction component by about 2.66x.
- Resolving a near-tie needs 206 paired partition draws at 1.1B and more than
  1000 at 3B.

## Scope

Methods: FedIT, FFA-LoRA, FLoRA. Models: TinyLlama-1.1B-Chat and LLaMA-3.2-3B.
Data: Dolly-15k 3k training subset, partitioned by the real `category` column
(Dirichlet alpha 0.1, alpha 0.5, and IID). Primary metric: held-out loss on Dolly
train[3000:3500]. Design size: 204 production cells.

## Repository map

- `src/` — federated LoRA training and aggregation (imported training path)
- `scripts/` — grid launcher, holdout eval, analysis, verifier; `scripts/ops/`
  holds campaign tooling
- `config/` — base and per-cell experiment configs
- `grids/` — production and smoke grid YAMLs (grids pin freeze tags)
- `results/` — run metadata and holdout JSON (no adapter weights)
- `analysis/` — paper CSVs and `claims.csv`; process logs under `analysis/logs/`
- `figures/` — manuscript figures
- `manuscript/` — IEEE Access LaTeX source and PDF
- `docs/` — scope, analysis plan, decisions, provenance, reproduce guide
- `tests/` — unit and integration tests for the training path
- `literature/` — local citation notes

## Reproducing

Full copy-paste commands, production-guard rules, and freeze-tag requirements are
in [`docs/REPRODUCE.md`](docs/REPRODUCE.md). Expected runtimes on one RTX 4090:

| Stage | Typical cost |
|---|---|
| Environment setup | minutes |
| Smoke grid | minutes |
| One TinyLlama cell | about 27 min |
| One LLaMA-3.2-3B cell | about 51 min |
| Full 204-cell design | about 150 GPU-hours |
| Analysis + `verify_varpart` | minutes on CPU |

## What is and is not archived

Archived: code, configs, grids, run metadata (`run_meta.json`, `results.json`,
`partition_stats.json`, merged configs), holdout JSON, analysis CSVs, figures,
and the manuscript. Not archived: LoRA adapter weights (`.pt`). Adapters are
large, regenerable from the pinned configs and seeds, and not required to
reproduce the published tables once holdout JSON and `analysis/runs.csv` are
present.

## Provenance

- `freeze-v1` — 120-cell TinyLlama + LLaMA core design (`prod_v1`)
- `freeze-v2` — holdout-eval pin used by production cells
- `freeze-v3.1` — 84-cell addendum (TinyLlama alpha 0.5 and LLaMA seeds
  2007–2010) after stack-pin hardening (`prod_v2`)

The training path under `src/` and `scripts/run_experiment.py` is byte-identical
across these freezes (verifier check V12).

## Inherited code

`src/federation/aggregators/` contains `reverse_adaptive.py`, `two_phase.py`, and
`flexlora.py` from the upstream codebase. They are not used in this study. They
are retained so the training path stays byte-identical to the imported commit,
and they remain covered by inherited tests.

## Citation

Article (placeholder until the Access DOI is assigned):

> J. A. Franklin, "Partition Draws, Not Aggregators," submitted to *IEEE Access*, 2026.

Software concept DOI (resolves to the latest archive version):
[10.5281/zenodo.22861074](https://doi.org/10.5281/zenodo.22861074).

## License

MIT — see [`LICENSE`](LICENSE).
