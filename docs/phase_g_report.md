# Phase G report (production launch)

**For review.** Pre-registered production grids from `docs/IMPLEMENTATION_PLAN.md` Phase G.  
**Status:** **COMPLETE** — acceptance criterion met on the Mac after final sync.  
**Freeze:** `freeze-v1` (`0812fcf`).  
**Date closed:** 18 Sep 2026 (UTC).

---

## 1. Executive summary

Phase G ran the full production grids on Vast.ai **NVIDIA GeForce RTX 4090** (24 GB) instances with `--production --workers 1`.

| Grid | Cells | Acceptance (`grid_status.py`) | Result |
|------|------:|-------------------------------|--------|
| **tl** (TinyLlama-1.1B) | 75 | `complete=75` / 75 | **PASS** |
| **l3** (LLaMA-3.2-3B) | 45 | `complete=45` / 45 | **PASS** |

Every production cell has training artifacts (`results.json`, `run_meta.json`, `partition_stats.json`) and a Dolly held-out eval (`instruction_holdout.json`). Tag on all runs: `prod_v1`.

**Next (plan):** Phase H `scripts/verify_varpart.py` (V1–V9), then Phase I analysis. No further GPU instances required unless verification forces re-runs.

---

## 2. Acceptance check (plan wording)

Plan: *“Phase G acceptance: `grid_status.py` shows 75 of 75 (and 45 of 45, if LLaMA was kept) complete.”*

```text
$ python scripts/grid_status.py --grid grids/tl.yaml
Grid: tl  expected=75  enumerated=75
complete=75  needs_holdout=0  resumable=0  orphan=0  fresh=0  other=0

$ python scripts/grid_status.py --grid grids/l3.yaml
Grid: l3  expected=45  enumerated=45
complete=45  needs_holdout=0  resumable=0  orphan=0  fresh=0  other=0
```

Also satisfied: *“Do not destroy an instance until its shard's jsonl shows every cell complete and the sync has landed on the Mac.”* Final M3 sync landed before this report; M1/M2 were already synced and idle.

---

## 3. Grid design (as frozen)

### TinyLlama (`grids/tl.yaml`) — 75 cells

- Methods: `fedit`, `ffa_lora`, `flora`
- Heterogeneity: `a01` (Dirichlet α=0.1) with data seeds `2001–2010` × run seeds `7001–7002`; `iid` with data seed `2001` × run seeds `7001–7005`
- Sharding: 3 shards (27 / 24 / 24 cells)

### LLaMA-3.2-3B (`grids/l3.yaml`) — 45 cells

- Same methods
- `a01`: data seeds `2001–2006` × run seeds `7001–7002`; `iid`: data seed `2001` × run seeds `7001–7003`
- Sharding: 3 shards (15 / 15 / 15 cells)

Launch pattern (each shard):

```bash
python scripts/run_grid.py --grid grids/{tl|l3}.yaml --shard {0|1|2} --num-shards 3 \
  --device cuda --production --workers 1 --max-retries 5
```

---

## 4. Compute footprint

| Role | Host (SSH) | Workload |
|------|------------|----------|
| M1 | `116.127.115.27:43029` | tl shard 0 → l3 shard 0 |
| M2 | `115.75.223.236:57132` | tl shard 1 → l3 shard 1 |
| M3 | `1.193.139.139:39647` | tl shard 2 → l3 shard 2 (last box still up at close) |

- All production `run_meta.json` records: **`hardware.gpu_name == "NVIDIA GeForce RTX 4090"`** (75/75 tl, 45/45 l3).
- Library triple identical across all 120 production runs: **torch `2.2.0+cu121`**, transformers `4.45.2`, peft `0.10.0`.
- Wall-clock (train process `wall_clock_s` from `run_meta`):

| Grid | min | median | mean | max |
|------|----:|-------:|-----:|----:|
| tl | 1229 s (~20.5 min) | 1628 s (~27.1 min) | 1799 s (~30.0 min) | 3377 s (~56.3 min) |
| l3 | 2349 s (~39.1 min) | 3067 s (~51.1 min) | 3060 s (~51.0 min) | 4499 s (~75.0 min) |

Phase F timing gates (F1 ~29 min tl, F2 ~65 min l3) remain consistent with observed production medians (holdout is separate and short relative to train).

---

## 5. Provenance snapshot (pre–Phase H)

Sampled all `prod_v1` `run_meta.json` files on the Mac after sync:

| Check | tl (75) | l3 (45) |
|-------|---------|---------|
| `git_describe == freeze-v1` | 75/75 | 45/45 |
| `git_dirty_tracked == false` | 75/75 | 45/45 |
| `device == cuda` | 75/75 | 45/45 |
| Single `gpu_name` within grid | RTX 4090 | RTX 4090 |
| Identical library versions within grid | yes | yes |

**Note:** Formal Phase H assertions V1–V9 are **not** claimed here; this section is a launch-quality snapshot to support review. `scripts/verify_varpart.py` is the next deliverable.

---

## 6. Held-out evaluation snapshot

All production holdouts under `results/downstream_instruction/**/prod_v1/**/instruction_holdout.json`:

| Field | tl (75) | l3 (45) |
|-------|---------|---------|
| Dataset | `databricks/databricks-dolly-15k` | same |
| `formatter_version` | `v2-dolly-context` | same |
| Start index / examples | 3000 / 500 | same |
| `eval_dtype` | `torch.float32` | `torch.float16` |
| `base_loss` (shared within model) | **2.120666** (unique) | **2.168946** (unique) |
| `tuned_loss` range | 1.691 – 1.723 | 1.790 – 1.839 |

### Why L3 holdout is float16

Early L3 cells failed holdout with **CUDA OOM**: the eval script loaded **two float32 3B copies** (tuned + base) on a 24 GB card. Training itself fit (~9 GB peak in F2).  

**Mitigation (eval-only):** sequential load + `torch_dtype=float16` on CUDA in `evaluate_instruction_holdout.py`, deployed on the GPU boxes without dirtying freeze-v1 training provenance (`git_dirty_tracked` remained false on all production `run_meta`). TinyLlama holdouts stayed float32.  

This should be recorded in `docs/DECISIONS.md` if reviewers treat eval dtype as analysis-facing (Phase H V7 mentions finite loss / Dolly / formatter, not dtype equality across models).

---

## 7. Incidents and operational notes

| Issue | Impact | Resolution |
|-------|--------|------------|
| L3 holdout OOM (dual float32 3B) | Cells trained then failed holdout; 0 L3 completes until fix | float16 + free between loads; re-ran / continued grids |
| M3 host thrash hangs (GPU ~0%, CPU >>100%) | Delayed tl shard 2 and some l3 flora cells; SIGTERM `exit=-15` in logs | Kill hung `run_experiment`; `run_grid` resume from checkpoint |
| Overnight autoheal false positives | Brief kill storms on M3 using **global** stale checkpoint mtime | Safer healer (per-run ckpt age, longer grace); grids finished |
| Wrong SSH IP (`166.88.186.149`) | Operator confusion | Live M3 remained `1.193.139.139:39647` |
| M3 venv `python` symlink resolve | Early l3 shard 2 failed `No module named torch` | Launch with unresolved `.venv/bin/python` path |

None of the above left incomplete cells in the final Mac tree (`grid_status` all complete).

---

## 8. Partition stats (descriptive)

- IID production cells often record `label_source: "none"` with still-populated per-client category histograms (IID does not use Dirichlet labels the same way).
- α=0.1 cells record `label_source: "column"` with `label_column: "category"`.
- `total_samples: 3000` and 8-category histograms are present in sampled stats; Phase H V4 should assert the exact schema keys (`global_label_hist`, etc.).

Carry-forward findings from earlier STATUS (still relevant for the paper): α=0.1 active clients often 9–10; some zero-step clients on small shards; discarded trailing samples vary by model.

---

## 9. Artifacts for reviewers

| Path | Role |
|------|------|
| `grids/tl.yaml`, `grids/l3.yaml` | Frozen cell lists |
| `results/raw/vp_tl_*/**/prod_v1/**` | TinyLlama runs |
| `results/raw/vp_l3_*/**/prod_v1/**` | LLaMA runs |
| `results/downstream_instruction/**/prod_v1/**/instruction_holdout.json` | Held-out metrics |
| `results/launch/*_shard*.jsonl` | Per-shard launch logs |
| `analysis/holdout_*.csv` | Convenience holdout tables |
| `docs/phase_f_report.md` | Timing gate that authorized this launch |
| `docs/IMPLEMENTATION_PLAN.md` | Pre-registered protocol |

Git ignores `*.pt` (adapters/checkpoints stay local backups only).

---

## 10. Go / no-go for Phase H

| Criterion | Verdict |
|-----------|---------|
| 75/75 tl complete on Mac | **GO** |
| 45/45 l3 complete on Mac | **GO** |
| Single GPU model name within each grid | **GO** (RTX 4090) |
| freeze-v1 + clean tracked dirty flag on run_meta | **GO** (spot-complete census) |
| Dolly holdout + v2 formatter on all cells | **GO** |
| Phase H verifier script exists | **NO** — write `scripts/verify_varpart.py` next |

**Recommendation:** Approve Phase G closure; destroy remaining Vast instance after any final personal backup sync; proceed to Phase H verification on the Mac.

---

## 11. Suggested reviewer checklist

- [ ] Re-run `python scripts/grid_status.py --grid grids/tl.yaml` and `... l3.yaml` on a clean checkout with synced `results/`
- [ ] Spot-check 2–3 `run_meta.json` files per grid for `git_describe`, `gpu_name`, library versions
- [ ] Spot-check 2–3 holdout JSONs for Dolly dataset and `formatter_version`
- [ ] Confirm no `timing/` tagged runs are mixed into analysis inputs
- [ ] After Phase H lands, require `verify_varpart.py` exit 0 before trusting Phase I tables
