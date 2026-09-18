# Frozen scope

The freeze-v1 block below is historical and unchanged. The freeze-v3 addendum follows; cross-reference `docs/DECISIONS.md` for the venue change and the 84-run addendum.

## freeze-v1 design (unchanged)

Copy this section verbatim into `docs/SCOPE.md` in Phase B. Nothing in it changes after the `freeze-v1` tag.

**Research questions**

- RQ1. At Dirichlet alpha 0.1, what share of the variance in held-out loss comes from the partition draw, from the partition-by-method interaction, and from the training seed?
- RQ2. How often does an evaluation using k partition draws rank FedIT, FFA-LoRA, and FLoRA differently from the full-design ranking?
- RQ3. How many partition draws are needed to detect held-out loss differences of 0.005, 0.01, 0.02, and 0.05 with 80% power, for paired and unpaired designs?
- RQ4 (exploratory). Do partition statistics (active clients, heterogeneity) track held-out loss and measured communication?

**Frozen design**

| Element | Value |
|---|---|
| Methods | `fedit`, `ffa_lora`, `flora` (no other aggregators) |
| Models | TinyLlama/TinyLlama-1.1B-Chat-v1.0 (primary); meta-llama/Llama-3.2-3B (replication, subject to Phase F gate) |
| LoRA | r=16, alpha=32, dropout 0.1, target modules q_proj and v_proj only |
| Federation | 10 clients, full participation, 15 rounds, 1 local epoch |
| Data | databricks/databricks-dolly-15k, train[0:3000] for training |
| Non-IID | Dirichlet label skew over the real `category` column, alpha=0.1 |
| IID | IID split, fixed data seed |
| Primary metric | Held-out loss on Dolly train[3000:3500], max length 256, same prompt format as training |
| Secondary | Total measured communication (MB) per run |
| Not used | Zero-shot benchmarks, per-round validation, any new aggregator |

**Seeds**

| Model | Setting | Data seeds | Run seeds | Runs |
|---|---|---|---|---|
| TinyLlama | alpha 0.1 | 2001 to 2010 | 7001, 7002 | 60 |
| TinyLlama | IID | 2001 | 7001 to 7005 | 15 |
| LLaMA-3.2-3B | alpha 0.1 | 2001 to 2006 | 7001, 7002 | 36 |
| LLaMA-3.2-3B | IID | 2001 | 7001 to 7003 | 9 |
| **Total** | | | | **120** |

**Rules for Cursor**

1. No new research directions, methods, models, datasets, or metrics.
2. No edits to aggregator logic (`src/federation/aggregators/*`) or the training loop in `src/federation/client.py` and `server.py`.
3. Every code change gets a test and a line in `docs/CHANGELOG.md`.
4. Production runs only from the `freeze-v1` commit with a clean tracked tree.
5. The analysis follows `docs/ANALYSIS_PLAN.md` exactly. Any deviation is logged in `docs/DECISIONS.md` with the reason, and reported in the paper.
6. No em dashes and no curly quotes in any text file written for the manuscript.

## freeze-v3 addendum (Phase N)

Added after the freeze-v1 design completed, under tag `freeze-v3` / run tag `prod_v2`. The training path (`src/`, `scripts/run_experiment.py`) is unchanged from freeze-v1; holdout eval remains pinned at freeze-v2. See `DECISIONS.md` for venue change (IEEE Access) and adapter retention.

| Element | Value |
|---|---|
| TinyLlama heterogeneity | Second Dirichlet level: alpha = 0.5 (`het: a05`), data seeds 2001 to 2010, run seeds 7001/7002 (60 runs) |
| LLaMA partition extension | Same alpha 0.1 configs; additional data seeds 2007 to 2010, run seeds 7001/7002 (24 runs), pooling with prod_v1 for p = 10 |
| **Addendum total** | **84** |

Analysis extensions I8 to I10 and their outcome-to-claim rows are pre-registered in `docs/ANALYSIS_PLAN.md` before any prod_v2 analysis.
