# Phase N report (prod_v2 addendum)

**For review.** Pre-registered 84-run addendum from `docs/IMPLEMENTATION_PLAN.md` Phase N (N5) / `docs/PHASE_N_RUNBOOK.md`.  
**Status:** **COMPLETE** — Mac sync verified 19 Sep 2026 (EDT).  
**Freeze:** `freeze-v3.1` (`7cff2a4`) on 83/84 cells; one early cell tagged `freeze-v3` (`f3e773d`) before the TinyLlama float32 holdout hotfix.  
**Tag:** `prod_v2`.

---

## 1. Executive summary

| Grid | Cells | `grid_status.py` | Result |
|------|------:|------------------|--------|
| **tl_a05** (TinyLlama, α=0.5) | 60 | `complete=60` / 60 | **PASS** |
| **l3_ext** (LLaMA-3.2-3B, α=0.1 seeds 2007–2010) | 24 | `complete=24` / 24 | **PASS** |
| Adapters (`final_adapter_state.pt` under `prod_v2`) | 84 | local Mac count | **PASS** |
| Holdouts (`instruction_holdout.json` under `prod_v2`) | 84 | local Mac count | **PASS** |

Hardware: 3× exact **NVIDIA GeForce RTX 4090** (Vast.ai). Shards: M1 shard0 (21+9), M2 shard1 (21+9), M3 shard2 (18+6). All three instances synced to Mac before destroy.

---

## 2. Acceptance check

```text
$ python scripts/grid_status.py --grid grids/tl_a05.yaml
complete=60

$ python scripts/grid_status.py --grid grids/l3_ext.yaml
complete=24

$ find results -path '*prod_v2*' -name 'final_adapter_state.pt' | wc -l
84
```

`python scripts/verify_varpart.py --grids grids/tl.yaml grids/l3.yaml`:
- **V12 PASS** (training path unchanged freeze-v1..freeze-v3; holdout path notes freeze-v3.1 TinyLlama float32 hotfix).
- **V7** TinyLlama PASS (float32 pooling).
- **V7** LLaMA: one cross-tag base_loss mismatch on
  `vp_l3_flora_a01/.../seed_2010_run7001/prod_v2/.../instruction_holdout.json`
  (`2.168848` vs prod_v1 reference `2.168946`). Cell itself is complete; flag for Phase O / analysis follow-up, not a missing run.

---

## 3. Grid design (as frozen)

### TinyLlama α=0.5 (`grids/tl_a05.yaml`) — 60 cells

- Methods: `fedit`, `ffa_lora`, `flora` (20 each)
- Data seeds `2001–2010` × run seeds `7001–7002`
- Config pattern: `config/vp/vp_tl_{method}_a05.yaml`

### LLaMA extension (`grids/l3_ext.yaml`) — 24 cells

- Methods: `fedit`, `ffa_lora`, `flora` (8 each)
- Data seeds `2007–2010` × run seeds `7001–7002` (α=0.1)
- Config pattern: `config/vp/vp_l3_{method}_a01.yaml`

Launch (each shard, production):

```bash
bash scripts/vast_launch_shard.sh grids/{tl_a05|l3_ext}.yaml {0|1|2} 3
```

---

## 4. Artifacts (Mac)

| Path | Role |
|------|------|
| `results/launch/tl_a05_shard{0,1,2}.jsonl` | per-cell launch ledger |
| `results/launch/l3_ext_shard{0,1,2}.jsonl` | per-cell launch ledger |
| `results/raw/**/prod_v2/*/` | `results.json`, `run_meta.json`, `config_merged.yaml`, `partition_stats.json` (+ local `final_adapter_state.pt`, gitignored) |
| `results/downstream_instruction/**/prod_v2/*/instruction_holdout.json` | Dolly holdout |
| `analysis/holdout_tl_a05_shard{0,1,2}.csv` | shard holdout tables |
| `analysis/holdout_l3_ext_shard{0,1,2}.csv` | shard holdout tables |
| `logs/{tl_a05,l3_ext}_shard{0,1,2}.log` | grid driver logs |

---

## 5. Known footnotes

1. **freeze-v3 vs freeze-v3.1:** `tl_fedit_a05_d2001_r7001` recorded `git_describe=freeze-v3` (first cell before hotfix deploy). Remaining 83 cells are `freeze-v3.1`.
2. **On-box hang watchdog:** early L3 flora attempts saw `train exit=-15` (SIGTERM) from the hang watchdog; watchdog was disabled; affected cells retried to completion.
3. **V7 L3 base_loss:** single prod_v2 holdout off reference by ~1e-4 (see §2).

---

## 6. Next

- Destroy remaining Vast instance(s); revoke campaign GitHub + HF tokens.
- Phase O: fold 84-run addendum into analysis / IEEE Access rework; resolve or document the L3 V7 footnote.
