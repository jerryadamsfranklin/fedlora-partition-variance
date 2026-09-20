# fedlora-partition-variance

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22861074.svg)](https://doi.org/10.5281/zenodo.22861074)

Measurement study: how much of the variance in federated LoRA fine-tuning results
comes from the Dirichlet partition draw versus the training seed, and how often
method rankings change as a result.

Scope (frozen, see docs/SCOPE.md): FedIT, FFA-LoRA, FLoRA; TinyLlama-1.1B and
LLaMA-3.2-3B; Dolly-15k (3k subset) partitioned by its `category` column;
Dirichlet alpha 0.1 and IID; metric is held-out loss on Dolly train[3000:3500].

Code provenance: `src/`, `tests/`, `scripts/run_experiment.py`,
`scripts/evaluate_instruction_holdout.py`, and `config/base_config*.yaml` were
imported unmodified from an earlier federated LoRA codebase (commit recorded in
docs/PROVENANCE.md). All later changes are listed in docs/CHANGELOG.md.

Secrets: set HF_TOKEN in the environment. Never commit it.

Archive: concept DOI [10.5281/zenodo.22861074](https://doi.org/10.5281/zenodo.22861074);
release `v0.9.1` DOI [10.5281/zenodo.22861075](https://doi.org/10.5281/zenodo.22861075).
Adapter weights are not included.

## License

MIT — see `LICENSE`.

