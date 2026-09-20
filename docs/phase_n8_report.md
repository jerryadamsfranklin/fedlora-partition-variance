# Phase N8 report — stack-drift retrain complete

**For review.** Retrain of 54 `prod_v2` cells that had drifted off the pinned torch stack.  
**Date:** 20 Sep 2026  
**Plan refs:** `docs/IMPLEMENTATION_PLAN.md` §N7–N8; `docs/PHASE_N_RUNBOOK.md`  
**Code pin:** `freeze-v3.1` · tag `prod_v2`  
**Review package:** `phase_n8_review_20260920/` (+ zip)

---

## 1. Executive summary

| Item | Result |
|------|--------|
| Cells quarantined (stack drift) | **54** |
| Cells retrained + synced to Mac | **54/54** |
| TinyLlama α=0.5 (`tl_a05_n8_m*`) | **39/39** complete |
| LLaMA-3.2-3B α=0.1 (`l3_ext_n8_m*`) | **15/15** complete |
| `run_meta.hardware.torch` | **2.2.0+cu121** on all 54 |
| `gpu_name` | **NVIDIA GeForce RTX 4090** on all 54 |
| `git_describe` | **freeze-v3.1** on all 54 |
| Full Phase N grids after merge | **tl_a05 60/60**, **l3_ext 24/24** (39+15 retrain + prior good cells) |

**Verdict:** N8 retrain **COMPLETE**. Safe to destroy all Vast instances used for N8.  
**Still open (plan N8-6+):** re-run I8/I9/I10 on the cleaned stack; write DECISIONS row; do **not** put drifted-stack numbers in the manuscript.

---

## 2. Why N8 existed

Census (N7) found **54** `prod_v2` cells whose training hosts had installed **torch ≠ 2.2.0+cu121** despite the requirements pin (observed **2.11 / 2.14** on some boxes). That confounded **training stack** with **partition draw**.

Response:
1. Quarantine drifted run dirs + holdouts under `results/quarantine_stackdrift/` (not delete).
2. Pin setup with assert at `freeze-v3.1` → exact `2.2.0+cu121` + exact RTX 4090 name.
3. Retrain only the 54 cells on three gated 4090s.
4. Re-run I8–I10 after sync (next step for analysis, not blocking destroy).

---

## 3. Machine assignment (final)

Default `--num-shards 3` was **unusable** (≈100% hour imbalance). Cells were **rebalanced by (het, data_seed, run_seed) groups** into filtered grids (spread **11.2%**).

| Role | Region (Vast) | Instance (final) | Filtered grids | Cells |
|------|---------------|------------------|----------------|------:|
| **M0** | Taiwan | `51661379` | `tl_a05_n8_m0` (12) + `l3_ext_n8_m0` (6) | 18 |
| **M1** | Czech / EU | destroyed after sync | `tl_a05_n8_m1` (9) + `l3_ext_n8_m1` (6) | 15 |
| **M2** | France | destroyed after sync | `tl_a05_n8_m2` (18) + `l3_ext_n8_m2` (3) | 21 |

Japan candidate destroyed early (≈1 MB/s setup). France replaced it for M2.

Projected hours at planning rates: M0 ≈13.8 h · M1 ≈12.3 h · M2 ≈13.1 h.

---

## 4. Gates and integrity

| Gate | Status |
|------|--------|
| N8-0 torch + GPU name per machine | **PASS** (all three) |
| Group integrity (no method split across machines) | **PASS** — see `analysis/logs/n8_group_integrity.txt` |
| Filtered union == 54 quarantined | **PASS** |
| First-cell / stack assert in setup | **PASS** (`GATE_PASS 2.2.0+cu121`) |
| Post-retrain manifest (`n8_cell_manifest.csv`) | **54/54** torch/gpu/git match |

---

## 5. Ops timeline (short)

| When (EDT) | Event |
|------------|-------|
| 19 Sep | Quarantine + filtered grids; M0/M1 launch; France M2 setup |
| 19–20 Sep | TL then L3 on each box; 10-min Mac health watcher + auto-heal |
| ~01:00 20 Sep | M1 TL done → L3 |
| ~08:50 20 Sep | M2 N8 fully done (TL 18 + L3 3) |
| ~07:10 20 Sep | M1 L3 done (watcher DONE) |
| ~10:37 20 Sep | M0 L3 done (**6/6**); all N8 complete |
| 20 Sep AM | M1+M2 results synced; later M0 synced; instances stopped |

### Ops incidents (resolved)

1. **Hang detector** missed long GPU-idle stretches when checkpoints were still fresh → tightened to idle+low power+etime>25m.
2. **Heal restart** activated `/venv/main` (no `datasets`) → instant fail loop → fixed to **`.venv` only**.
3. Health script fell through to full `tl_a05` after N8 grids finished → false UNHEALTHY on M2 → N8-only candidate list.
4. Mac watcher briefly **SIGKILL**’d (`Killed: 9`) → log spam without progress lines; remotes kept training.
5. Destroy confusion (Vast UI GPU % vs SSH) — final keep was Taiwan `51661379` until M0 finished.

---

## 6. Deliverables on Mac

| Path | What |
|------|------|
| `results/raw/**/prod_v2/**/results.json` | Training metrics (54 N8 cells + prior) |
| `results/raw/**/prod_v2/**/run_meta.json` | torch / gpu / git |
| `results/downstream_instruction/**/instruction_holdout.json` | Held-out eval |
| `results/quarantine_stackdrift/` | Original drifted cells (preserved) |
| `grids/*_n8_m*.yaml` | Filtered launch grids |
| `analysis/logs/n8_*.txt` / `n8_public_repo_scan*` | Pre-launch checks |
| `analysis/logs/holdout_*_n8_*.csv` | Holdout summary CSVs from remotes |
| `logs/prod_v2_health.log` | 10-min health history |

---

## 7. What this review package contains

```
phase_n8_review_20260920/
  README.md                          # this pointer
  docs/phase_n8_report.md            # this report
  docs/IMPLEMENTATION_PLAN_N8_excerpt.md
  analysis/logs/n8_cell_manifest.csv      # 54 rows: paths, torch, gpu, git
  analysis/logs/n8_group_integrity.txt
  analysis/logs/n8_machine_gates.txt
  analysis/logs/n8_balance_check.txt
  analysis/logs/n8_public_repo_scan_findings.md
  analysis/logs/holdout_*.csv             # available n8 holdout summaries
  grids/*.yaml                       # six filtered grids
  status/GIT_HEAD.txt
  status/completion_summary.txt
```

Full raw `results/` trees are large; reviewers who need adapters should pull from the Mac `results/` tree or a separate archive. The **manifest CSV** is enough to audit completeness and stack pins.

---

## 8. Recommended next steps (not done in N8 ops)

1. **N8-6:** Re-run I8 / I9 / I10; compare to drifted-stack table; keep N7 effect size beside it.  
2. **N8-7:** Append DECISIONS.md row (template in IMPLEMENTATION_PLAN).  
3. **N8-5 remaining:** Confirm V2-cross-tag / V7 / V12 on the merged 84 `prod_v2` set.  
4. Manuscript: still **no** results prose until N8-6 numbers are locked.  
5. Destroy Taiwan if not already destroyed.

---

## 9. One-line status for STATUS.md

> Phase N8 **COMPLETE** 20 Sep 2026: 54/54 stack-drift cells retrained on torch `2.2.0+cu121` + RTX 4090 at `freeze-v3.1`; synced to Mac; awaiting I8–I10 re-run (N8-6).
