# fedlora-partition-variance

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

## License

MIT — see `LICENSE`.

