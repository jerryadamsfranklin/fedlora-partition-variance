# N8-6 side-by-side: drifted-stack (19 Sep) vs retrain (20 Sep)

Source drifted: `analysis/n8_drifted_stack_19sep/` (+ ranking means from `phase_n_review_20260919/analysis/runs.csv`).
Source clean: `analysis/runs.csv` (204 rows) after 54-cell torch 2.2.0+cu121 retrain; I8–I10 recomputed.

## Pre-registered outcome rows selected

| Row | Drifted (19 Sep) | Clean (20 Sep) |
|---|---|---|
| (auto) | I8/I9: Gradient absent — all three difference CIs include zero; alpha 0.1 findings generalize over this range. | I8/I9: Gradient absent — all three difference CIs include zero; alpha 0.1 findings generalize over this range. |
| (auto) | I10: At p=10, LLaMA partition-share CI still includes zero; keep interaction-dominated 3B story; p=6 remains sensitivity. | I10: At p=10, LLaMA partition-share CI still includes zero; keep interaction-dominated 3B story; p=6 remains sensitivity. |
| (auto) | I10 note: s2_P truncated at zero at p=10 (MS_P < MS_PM); report trunc_P=True alongside the share CI. | I10 note: s2_P truncated at zero at p=10 (MS_P < MS_PM); report trunc_P=True alongside the share CI. |

Selected rows **unchanged**.

## Ranking reversal (l3 top-two FedIT vs FLoRA)

| Set | p=6 order (best→worst) | flora−fedit | p=10 order | flora−fedit | Reversal? |
|---|---|---:|---|---:|---|
| Drifted | fedit > flora > ffa_lora | +0.00201 | flora > fedit > ffa_lora | -0.00070 | YES |
| Clean | fedit > flora > ffa_lora | +0.00201 | flora > fedit > ffa_lora | -0.00067 | YES |

**Verdict: the l3 p=6 versus p=10 top-two reversal SURVIVES the retrain.**

## I8 — TinyLlama variance components / shares

| Quantity | Drifted a01 | Clean a01 | Drifted a05 | Clean a05 |
|---|---:|---:|---:|---:|
| s2_P | 4.094e-06 | 4.094e-06 | 2.219e-07 | 2.219e-07 |
| s2_PM | 3.779e-06 | 3.779e-06 | 5.468e-07 | 5.468e-07 |
| s2_E | 1.893e-07 | 1.893e-07 | 3.336e-08 | 3.337e-08 |
| share_P | 0.5078 | 0.5078 | 0.2766 | 0.2766 |
| share_PM | 0.4687 | 0.4687 | 0.6818 | 0.6817 |
| share_E | 0.0235 | 0.0235 | 0.0416 | 0.0416 |
| share_P CI | [0.2024,0.6626] | [0.2024,0.6626] | [0.0000,0.5972] | [0.0000,0.5973] |
| share_PM CI | [0.3161,0.7647] | [0.3161,0.7647] | [0.3524,0.9583] | [0.3524,0.9583] |
| share_E CI | [0.0068,0.0563] | [0.0068,0.0563] | [0.0270,0.0939] | [0.0270,0.0940] |

## I9 — Share differences (a05 − a01) with CIs

| Diff | Drifted | Clean | excludes 0? drifted→clean |
|---|---|---|---|
| delta_share_P | -0.2312 [-0.5678,0.1940] | -0.2311 [-0.5678,0.1940] | False→False |
| delta_share_PM | 0.2130 [-0.2143,0.5422] | 0.2130 [-0.2142,0.5421] | False→False |
| delta_share_E | 0.0181 [-0.0159,0.0704] | 0.0181 [-0.0159,0.0705] | False→False |

## I10 — LLaMA p=10 (and p=6 sensitivity)

| Quantity | Drifted p=10 | Clean p=10 | Drifted p=6 | Clean p=6 |
|---|---:|---:|---:|---:|
| s2_P | 0.0 | 0.0 | 3.2806790573462094e-06 | 3.280679057346212e-06 |
| s2_PM | 2.944650648745825e-05 | 2.9442384428438935e-05 | 1.1053934835216425e-05 | 1.1053934835216425e-05 |
| s2_E | 2.0344034039398516e-07 | 2.5101979798593135e-07 | 1.3086842005753545e-07 | 1.3086842005753545e-07 |
| share_P | 0.0 | 0.0 | 0.22679361713947385 | 0.226793617139474 |
| share_PM | 0.9931385934155241 | 0.9915462775479768 | 0.7641594380556951 | 0.764159438055695 |
| share_E | 0.006861406584475884 | 0.008453722452023298 | 0.009046944804831116 | 0.009046944804831114 |
| trunc_P | True | True | False | False |
| share_P CI | [0.0000,0.3527] | [0.0000,0.3288] | [0.0000,0.5512] | [0.0000,0.5512] |

## I10 — Pair-level flips (k=1 paired; ref_order)

| pair | Drifted gap | Clean gap | Drifted P(flip) | Clean P(flip) | Drifted sign flips | Clean |
|---|---:|---:|---:|---:|---:|---:|
| fedit-ffa_lora | -0.03063 | -0.03051 | 0.0000 | 0.0000 | 0/20 | 0/20 |
| fedit-flora | 6.998e-04 | 6.742e-04 | 0.7001 | 0.7001 | 14/20 | 14/20 |
| ffa_lora-flora | 0.03133 | 0.03118 | 0.0000 | 0.0000 | 0/20 | 0/20 |
| ref_order | flora>fedit>ffa_lora | flora>fedit>ffa_lora | | | | |

## I10 — Observed-gap power (and preregistered deltas)

| kind | pair/delta | Drifted n_paired | Clean n_paired | Drifted n_unpaired | Clean n_unpaired |
|---|---|---:|---:|---:|---:|
| preregistered_delta | 0.005 | 21 | 21 | 20 | 20 |
| preregistered_delta | 0.01 | 7 | 7 | 6 | 6 |
| preregistered_delta | 0.02 | 4 | 4 | 3 | 3 |
| preregistered_delta | 0.05 | 3 | 3 | 2 | 2 |
| observed_gap | fedit-ffa_lora | 3 | 3 | 3 | 3 |
| observed_gap | fedit-flora | 953 | more than 1000 | 952 | more than 1000 |
| observed_gap | ffa_lora-flora | 3 | 3 | 2 | 2 |

## Notes

- a01 TinyLlama shares unchanged (prod_v1 only).
- a05 shares move only in the 4th–5th digit after retrain (39/60 cells).
- l3 p=10: interaction share 0.993→0.992; share_P CI upper 0.353→0.329; still trunc_P=True; still includes 0.
- Near-tie fedit–flora paired draws needed: 953 → more than 1000 (gap 0.00070→0.00067).
- Interaction “nearly tripled” at p=10 vs p=6: drifted s2_PM 2.94e-5 / 1.11e-5 ≈ 2.66×; clean 2.94e-5 / 1.11e-5 ≈ 2.66× (still elevated vs p=6; p=6 unchanged).
