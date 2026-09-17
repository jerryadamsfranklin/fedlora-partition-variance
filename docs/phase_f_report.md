# Phase F report (GPU timing gate)

Pre-registered gates from `docs/IMPLEMENTATION_PLAN.md` Phase F.  
Freeze tag: `freeze-v1` (`0812fcf`).  
Hardware: on-demand **NVIDIA GeForce RTX 4090** (24 GB), CUDA 12.x, Vast.ai.  
Timing tag: `timing` (not production data).

## Summary

| Check | Result | Gate | Decision |
|---|---|---|---|
| **F1** TinyLlama full prod config | **1759 s (29.3 min)** | ≤ 45 min | **PASS** — proceed with TinyLlama grid |
| **F2** LLaMA-3.2-3B full prod config | **3910 s (65.2 min)**; peak alloc **~9.0 GB** | ≤ 75 min; peak &lt; 22 GB | **PASS** — keep LLaMA grid on 4090s |
| **F3** two TinyLlama runs concurrent | wall **3309 s (55.2 min)** for 2 runs | throughput ≥ 1.6× F1 | **FAIL threshold** (ratio **1.06×**) — use **`--workers 1`** |
| TinyLlama per-client upload | **9,011,200 B** | match Phase D | **PASS** |
| LLaMA per-client upload (FLoRA) | **9,175,040 B** | 9,175,040 expected | **PASS** |

## Runs

### F1 — TinyLlama (machine 1)

```text
config: config/vp/vp_tl_flora_a01.yaml
data_seed=2001 run_seed=7001 tag=timing
output: results/raw/vp_tl_flora_a01/flora/seed_2001_run7001/timing/20260917_070508
wall_clock_s: 1759.43
gpu_name: NVIDIA GeForce RTX 4090
git_describe: freeze-v1
rounds: 15
communication_mb (cumulative): 2578.125
broadcast_bytes_per_client: 9011200
```

### F2 — LLaMA-3.2-3B (machine 2)

```text
config: config/vp/vp_l3_flora_a01.yaml
data_seed=2001 run_seed=7001 tag=timing
output: results/raw/vp_l3_flora_a01/flora/seed_2001_run7001/timing/20260917_074036
wall_clock_s: 3910.30
peak_mem_allocated_bytes: 9458633216 (~9017 MiB)
gpu_mem_total: 24564 MiB
gpu_name: NVIDIA GeForce RTX 4090
git_describe: freeze-v1
rounds: 15
communication_mb (cumulative): 2625.0
broadcast_bytes_per_client: 9175040
```

### F3 — concurrency (machine 1)

Two parallel TinyLlama FLoRA runs (`data_seed=2002`, `run_seed=7001` and `7002`).

| Job | wall_clock_s (run_meta) | output |
|---|---|---|
| F3a | 3275.88 | `.../seed_2002_run7001/timing/20260917_073444` |
| F3b | 3281.56 | `.../seed_2002_run7002/timing/20260917_073449` |

Concurrent wall clock (first start → both complete): **3309 s**.

Throughput vs F1:

\[
\frac{2 / 3309}{1 / 1759} = \frac{2 \times 1759}{3309} \approx 1.06
\]

Gate requires ≥ **1.6**. Therefore production TinyLlama uses **`--workers 1`**.

## Phase G sizing (from measured times)

Training-only estimates (production cells also run held-out eval; add ~2–3 GPU-min/cell):

| Grid | Cells | min/run (train) | GPU-hours (train) | + holdout (~2.5 min) |
|---|---|---|---|---|
| `tl` | 75 | ~29.3 | ~36.6 | ~**40** |
| `l3` | 45 | ~65.2 | ~48.9 | ~**51** |

With **2× 4090** on `tl` shards 0+1 (27+24 cells): expect on the order of **~1–1.5 days** wall-clock for those shards before shard 2 is rented. Add credits before long overnight burns (~$0.4–0.5/hr per box).

## Phase G launch (started after F)

| Instance | Command | Cells |
|---|---|---|
| Machine 1 (`116.127.115.27:43029`) | `run_grid.py --grid grids/tl.yaml --shard 0 --num-shards 3 --production --workers 1` | 27 |
| Machine 2 (`115.75.223.236:57132`) | `run_grid.py --grid grids/tl.yaml --shard 1 --num-shards 3 --production --workers 1` | 24 |

Still needed later: **shard 2** (24 cells) on a third 4090; then `grids/l3.yaml` on matching 4090s (same `gpu_name`).

## Artifacts synced to this repo

- `results/raw/vp_tl_flora_a01/.../timing/**/{run_meta,results,partition_stats,config_merged}.json/yaml`
- `results/raw/vp_l3_flora_a01/.../timing/**/...`
- `results/timing/f1_timing.log`, `f2_timing.log`, `f3a_timing.log`, `f3b_timing.log`

`*.pt` adapters kept on Vast / local disk; not required in git.

## Stop conditions checked

- No OOM on LLaMA 4090  
- Bytes match recorded constants  
- Both scales proceed  

Ready for review; production `tl` shards 0–1 already running under `prod_v1`.
