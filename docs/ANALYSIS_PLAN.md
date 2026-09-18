Pre-registered before any production run. Frozen at freeze-v1.

## Phase I. Analysis (pre-registered)

**I0. Run table.** `scripts/analysis/build_runs_table.py` writes `analysis/runs.csv`, one row per run, with columns: `model, het, method, data_seed, run_seed, heldout_loss, base_loss, delta_loss, final_train_loss, comm_mb_total, upload_mb_total, active_clients, run_dir, gpu_name, wall_clock_s`. Build the table from `instruction_holdout.json` files only; holdout summary CSVs are convenience logs and may be sharded per cell when `--workers > 1`.

All analyses use `heldout_loss` as Y. `scripts/analysis/analyze_variance.py` produces I1 to I6 for each model separately.

**I1. Variance components at alpha 0.1** (`analysis/variance_components.csv`)

The design is balanced: m = 3 methods (fixed), p partitions (random; 10 for TinyLlama, 6 for LLaMA), r = 2 seeds per cell.

Two-way ANOVA with replication:

- `MS_P = SS_P / (p - 1)`
- `MS_PM = SS_PM / ((m - 1)(p - 1))`
- `MS_E = SS_E / (m p (r - 1))`

Method-of-moments estimates:

- `s2_E = MS_E`
- `s2_PM = max(0, (MS_PM - MS_E) / r)`
- `s2_P = max(0, (MS_P - MS_PM) / (m r))`

Report each component, its share of `s2_P + s2_PM + s2_E`, and a flag wherever truncation at 0 occurred.

Confidence intervals come from a cluster bootstrap over partitions: resample partitions with replacement, B = 2000, seed 12345, percentile 95% CI.

As a cross-check, fit a `statsmodels` MixedLM: `Y ~ C(method)` with variance components for partition and partition:method. Report both. The ANOVA estimates are primary.

Per-method one-way estimates: `s2_P_j = max(0, (MSB_j - MSW_j) / r)` and `s2_E_j = MSW_j`.

**I2. IID noise floor** (`analysis/iid_noise.csv`)

For each method, compute the variance across its IID run seeds, then pool across methods. Report the pooled value next to `s2_E` from I1, together with the ratio `s2_E(alpha 0.1) / s2_E(IID)`. This is descriptive; there is no test.

**I3. Ranking stability** (`analysis/rank_flip.csv`)

The reference ranking orders the methods by mean held-out loss over all alpha 0.1 cells.

For k in {1, 2, 3, 5} (TinyLlama) or {1, 2, 3} (LLaMA), draw B = 10000 samples with seed 12345:

- **Paired protocol:** sample k partitions without replacement; for each, pick one run seed uniformly; use the same (partition, seed) pairs for all methods; rank the methods by mean.
- **Unpaired protocol:** sample independently for each method.

Report P(best method differs from reference) and P(full order differs from reference), with Wilson 95% CIs.

**I4. Draws needed** (`analysis/power.csv`)

- Paired per-draw SD for a method pair: `sd_pair = sqrt(2 * s2_PM + 2 * s2_E)`.
- Unpaired per-draw SD: `sd_unpair = sqrt(s2_P + s2_PM + s2_E)`.

For Delta in {0.005, 0.01, 0.02, 0.05}:

- Paired: smallest n with power at least 0.8 at alpha 0.05, two-sided, using `statsmodels.stats.power.TTestPower` with effect size `Delta / sd_pair`.
- Unpaired: `TTestIndPower` with `Delta / sd_unpair`, reporting n per method.

Report n as an integer, or "more than 1000".

Also compute an empirical `sd_pair` directly from the observed paired differences across partitions for each method pair, and report it next to the model-based value.

**I5. Observed method differences** (`analysis/method_means.csv`)

For each method: mean and SD of held-out loss for alpha 0.1 and for IID.

For each method pair at alpha 0.1: paired t-test on partition-level means (averaged over seeds) with Holm correction across the 3 pairs; report mean difference, 95% CI, raw p, and Holm p. This is reported as context. The paper does not claim a winning method.

**I6. Partition statistics and communication** (`analysis/partition_effects.csv`, `analysis/comm.csv`)

Per partition, compute:

- active clients
- effective clients (active clients with at least one optimizer step), per model
- discarded trailing samples (samples never entering a completed gradient-accumulation block), per model
- Gini coefficient of client sizes
- mean Jensen-Shannon divergence between each active client's category distribution and the global distribution (natural log)

Report the Spearman correlation of each statistic with the partition-mean held-out loss (averaged over methods and seeds), with n noted. Label this exploratory.

For communication: `comm_mb_total` versus `active_clients` for each method. Report the fitted line and confirm it matches the V6 formula exactly. Report the range of total communication across alpha 0.1 partitions for each method.

**I7. Outcome-to-claim table** (pre-registered; copy into `ANALYSIS_PLAN.md`)

| Result | Claim the paper makes |
|---|---|
| Partition share at least 30%, or 3-draw paired flip probability at least 20% | Few-partition evaluations of federated LoRA methods are unreliable at this scale; report partition draws explicitly and pair comparisons on partitions |
| Partition share under 10% and flip probability under 5% | At this scale, partition draws contribute little; three draws suffice for differences larger than the I4 detectable Delta |
| In between | Report the numbers and the n from I4 without a categorical claim |
| Interaction `s2_PM` large relative to `s2_P` | Pairing on partitions does not remove the partition effect on rankings; stress the interaction |
| TinyLlama and LLaMA shares differ in direction (non-overlapping CIs) | Report the scale difference with the 6-partition caveat |
| Overlapping CIs across scales | State that the data cannot distinguish the two scales |

**I8. Variance components at alpha 0.5** (TinyLlama; `analysis/variance_components.csv` keyed by het, or `analysis/variance_components_a05.csv`)

Design: m = 3 methods (fixed), p = 10 partitions (random), r = 2 seeds per cell. Same method-of-moments estimators and cluster bootstrap as I1 (B = 2000, seed 12345).

**I9. Heterogeneity gradient** (`analysis/het_gradient.csv`)

On TinyLlama, compare `share_P`, `share_PM`, and `share_E` between alpha 0.1 and alpha 0.5. Report each difference (alpha 0.5 minus alpha 0.1) with a cluster-bootstrap 95% CI (B = 2000, seed 12345).

**I10. LLaMA at p = 10**

Pool `prod_v1` and `prod_v2` LLaMA alpha 0.1 cells (data seeds 2001 to 2010). Recompute I1, I3, and I4 at p = 10. Report the original p = 6 analysis as a sensitivity analysis. State whether the partition main-effect interval still includes zero.

**I8 to I10 outcome-to-claim table** (pre-registered)

| Result | Claim the paper makes |
|---|---|
| Gradient present: at least one of the differences in `share_P`, `share_PM`, or `share_E` (alpha 0.5 minus alpha 0.1) has a bootstrap CI that excludes zero | Heterogeneity level changes the variance decomposition; report both alphas and the gradient |
| Gradient absent: all three difference CIs include zero | Across alpha 0.1 to 0.5, variance shares do not detectably change at this design; the alpha 0.1 findings generalize over this range |
| At p = 10, the LLaMA partition-share CI excludes zero | Partition main effect is identifiable at 3B with ten draws; update claims accordingly and keep p = 6 as sensitivity |
| At p = 10, the LLaMA partition-share CI still includes zero | Keep the 3B story as interaction-dominated; p = 6 remains a sensitivity analysis |

---

## Phase J. Figures and tables

`scripts/analysis/make_figures.py` writes vector PDFs to `figures/`. Use a colorblind-safe palette and fonts of at least 8 pt at single-column width.

| ID | Content |
|---|---|
| Fig 1 | Held-out loss per run: x = method, y = loss, points colored by partition, IID and alpha 0.1 side by side, one panel per model |
| Fig 2 | Ranking flip probability versus k, paired and unpaired, one line per model, with Wilson CIs |
| Fig 3 | Required partition draws versus Delta (log y-axis), paired and unpaired, one line per model |
| Tab 1 | Setup summary (from Section 0) |
| Tab 2 | Variance components with shares and bootstrap CIs, per model |
| Tab 3 | Method means and SDs (IID and alpha 0.1), total communication range, active-client range |

`scripts/analysis/make_tables.py` writes LaTeX tables to `manuscript/tables/`, generated only from `analysis/*.csv`. No hand-typed numbers.
