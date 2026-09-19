# Phase N report (prod_v2 addendum)

**For review.** Pre-registered 84-run addendum from `docs/IMPLEMENTATION_PLAN.md` Phase N / `docs/PHASE_N_RUNBOOK.md`.  
**Status:** **COMPLETE** (grids + N6 diagnosis/repair + I8–I10).  
**Freeze:** `freeze-v3.1` (`7cff2a4`) on **83/84** cells; **1/84** (`tl_fedit_a05_d2001_r7001`) under `freeze-v3` (`f3e773d`) before the TinyLlama float32 holdout hotfix.  
**Tag:** `prod_v2`.

---

## 1. Executive summary

| Grid | Cells | `grid_status.py` | Result |
|------|------:|------------------|--------|
| **tl_a05** (TinyLlama, α=0.5) | 60 | `complete=60` / 60 | **PASS** |
| **l3_ext** (LLaMA-3.2-3B, α=0.1 seeds 2007–2010) | 24 | `complete=24` / 24 | **PASS** |
| Adapters (`final_adapter_state.pt` under `prod_v2`) | 84 | local Mac count | **PASS** |
| Holdouts (`instruction_holdout.json` under `prod_v2`) | 84 | local Mac count | **PASS** |
| Verifier V7 / V12 | — | after N6 holdout repair | **PASS** |
| `analysis/runs.csv` | 204 | prod_v1 (120) + prod_v2 (84) | **PASS** |

Hardware: 3× exact **NVIDIA GeForce RTX 4090** (Vast.ai). Shards: M1 shard0 (21+9), M2 shard1 (21+9), M3 shard2 (18+6).

---

## 2. N6-1 Diagnosis (LLaMA `base_loss` anomaly)

Compared failing
`vp_l3_flora_a01/flora/seed_2010_run7001/prod_v2/20260919_183440/instruction_holdout.json`
to a passing peer (`seed_2009_run7001` on the same method).

| Field | Failing | Passing |
|-------|---------|---------|
| `eval_dtype` | `torch.float16` | `torch.float16` |
| `max_seq_length` | 256 | 256 |
| `heldout_start` / `heldout_examples` | 3000 / 500 | 3000 / 500 |
| `base_model` | `meta-llama/Llama-3.2-3B` | same |
| `device` | `cuda` | `cuda` |
| `formatter_version` | `v2-dolly-context` | same |
| `base_loss` | **2.1688484129405574** | **2.168945952316856** |
| `git_describe` (run_meta) | `freeze-v3.1` | `freeze-v3.1` |
| `hardware.torch` (run_meta) | **2.14.0+cu130** | **2.2.0+cu121** |

**Census:** 15/24 LLaMA prod_v2 cells had 2.1688484 (torch 2.11.0+cu128 or 2.14.0+cu130); 9/24 matched the prod_v1 reference on torch 2.2.0+cu121. This is **not** the single `freeze-v3` TinyLlama cell, and **not** a dtype swap (fp16 spot-check was ~2.16897).

---

## 3. N6-2 Dual re-eval (surviving 4090, torch 2.2.0+cu121, freeze-v3.1)

Scratch tags `n6_scratch_r1/rerun1` and `n6_scratch_r2/rerun2` on the flora d2010/r7001 adapter:

| Run | `base_loss` | `tuned_loss` | vs ref 2.168945952316856 |
|-----|------------:|-------------:|--------------------------|
| r1 | 2.168945952316856 | 1.8043874669992972 | abs diff 0 (<1e-6) |
| r2 | 2.168945952316856 | 1.8043874669992972 | abs diff 0; **identical to r1** |

Conclusion: deterministic on the 2.2.0 stack; anomaly was host torch/CUDA drift. Replaced all **15** anomalous prod_v2 LLaMA holdouts via the same eval path. Verifier: **V7 PASS**, **V12 PASS**.

---

## 4. Retry census (N6-5)

| Grid | Failed train attempts | All recovered? | Cause (from jsonl / logs) |
|------|----------------------:|:--------------:|---------------------------|
| `tl_a05` | **38** | yes | Mostly `train failed exit=1` during early TinyLlama float16 holdout / gate period before freeze-v3.1; plus `exit=-15` (2) and `exit=-9` (1) |
| `l3_ext` | **19** | yes | All `train failed exit=-15` (SIGTERM) from the on-box hang watchdog false-killing L3 flora mid-train; watchdog disabled; cells retried to completion |

---

## 5. I8–I10 results (N6-3)

`analysis/runs.csv`: **204** rows.

### I8 — TinyLlama α=0.5 variance components

| | share_P | share_PM | share_E |
|--|--------:|---------:|--------:|
| point | 0.2766 | (see CSV) | (see CSV) |
| 95% CI share_P | [0.0000, 0.5972] | | |

Artifact: `analysis/variance_components_a05.csv` (also `variance_components_by_het.csv`).

### I9 — Heterogeneity gradient (α=0.5 − α=0.1, TinyLlama)

| Δ share | point | 95% CI | excludes 0? |
|---------|------:|--------|:-----------:|
| Δ share_P | −0.2312 | [−0.5678, 0.1940] | no |
| Δ share_PM | +0.2130 | [−0.2143, 0.5422] | no |
| Δ share_E | +0.0181 | [−0.0159, 0.0704] | no |

**Pre-registered row selected:** *Gradient absent* — all three difference CIs include zero; α=0.1 findings generalize over this range.

### I10 — LLaMA at p=10 (pooled prod_v1+prod_v2 a01)

| | share_P | 95% CI | includes 0? |
|--|--------:|--------|:-----------:|
| p=10 | 0.0000 | [0.0000, 0.3527] | **yes** |
| p=6 sensitivity | (see CSV) | | |

**Pre-registered row selected:** *At p=10, LLaMA partition-share CI still includes zero* — keep interaction-dominated 3B story; p=6 remains sensitivity.

Artifacts: `analysis/het_gradient.csv`, `variance_components_l3_p10.csv`, `rank_flip_l3_p10.csv`, `power_l3_p10.csv`, `i8_i10_selected_claims.txt`.

---

## 6. Artifacts (Mac)

| Path | Role |
|------|------|
| `results/launch/tl_a05_shard{0,1,2}.jsonl` | launch ledger |
| `results/launch/l3_ext_shard{0,1,2}.jsonl` | launch ledger |
| `results/raw/**/prod_v2/*/` | run JSON/YAML (+ local `.pt`) |
| `results/downstream_instruction/**/prod_v2/*/instruction_holdout.json` | holdouts (15 LLaMA repaired under N6) |
| `analysis/runs.csv` | 204-row I0 table |
| `analysis/variance_components_a05.csv`, `het_gradient.csv`, `variance_components_l3_p10.csv` | I8–I10 |

---

## 7. Next

- Destroy the surviving Vast 4090; revoke campaign GitHub + HF tokens.
- Phase O: Results / Discussion / Abstract / Conclusion for I8–I10; disclose freeze-v3.1 mid-grid eval change and torch-stack holdout repair in limitations.
