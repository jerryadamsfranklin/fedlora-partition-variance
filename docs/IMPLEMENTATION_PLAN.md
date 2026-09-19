# IMPLEMENTATION PLAN: Partition-Variance Study (IJACSA, submit by 24 Sep 2026)

Repo: `fedlora-partition-variance` (created by `CURSOR_TASK_01_REPO_SETUP.md`).
Author: Jerry Adams Franklin, Independent Researcher.

This file is the single source of truth for execution. Cursor executes phases in order. Each phase ends with an acceptance check. If a check fails, stop and report; do not work around it.

---

## 0. Frozen scope

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

---

## 1. Timeline

| Date | Phase | Output |
|---|---|---|
| Tue 15 Sep | A, B, C, D | New repo, code changes, configs, Mac smoke tests |
| Wed 16 Sep | E, F, G | Pre-registration and freeze, GPU timing gate, production launch |
| Thu 17 Sep | G (running), K, L | Runs finish overnight; literature audit; draft Intro, Related Work, Setup |
| Fri 18 Sep | H, I, J | Sync, verification, analysis, figures |
| Sat 19 to Sun 20 Sep | L | Results and Discussion |
| Mon 21 Sep | Go/no-go | Section 14 criteria |
| Tue 22 Sep | L | SAI template, anonymization, declarations |
| Wed 23 Sep | M | Full verification pass, overlap check, read-through |
| Thu 24 Sep | M | Submit |
| Fri 25 Sep | Buffer | Official deadline |

---

## Phase A. Repository creation

Execute `CURSOR_TASK_01_REPO_SETUP.md`. Acceptance is defined there.

---

## Phase B. Code changes (Mac)

Work on branch `main`, one commit per item. Run `python -m pytest -q` after each item.

### B0. Scope and decision documents

Create:

- `docs/SCOPE.md`: Section 0 of this file, verbatim.
- `docs/DECISIONS.md`: a header plus a table with columns `date | decision | reason | evidence`.

Commit: `docs: scope and decision log`.

### B1. Partition statistics and required label column

**Why.** The imported runner silently falls back to instruction-length buckets when the configured label column is missing. For this study that fallback would invalidate the non-IID setting, so it must fail loudly. Every run must also record exactly how data was split.

**New module `src/data/partition_stats.py`** (pure functions, no torch):

```python
from __future__ import annotations
from collections import Counter
from typing import Any, Dict, List, Optional


def _hist(values) -> Dict[str, int]:
    c = Counter(str(v) for v in values)
    return {k: int(c[k]) for k in sorted(c)}


def compute_partition_stats(
    client_datasets,
    *,
    label_column: Optional[str],
    label_source: str,          # "column" | "length_proxy" | "none"
    partition_method: str,
    partition_alpha: Optional[float],
    data_seed: int,
    num_clients_configured: int,
) -> Dict[str, Any]:
    sizes = [int(len(ds)) for ds in client_datasets]
    per_client: List[Dict[str, int]] = []
    global_hist: Counter = Counter()
    for ds in client_datasets:
        if label_column and len(ds) > 0 and label_column in ds.column_names:
            h = _hist(ds[label_column])
        else:
            h = {}
        per_client.append(h)
        global_hist.update(h)
    return {
        "schema_version": 1,
        "data_seed": int(data_seed),
        "partition_method": partition_method,
        "partition_alpha": partition_alpha,
        "label_column": label_column,
        "label_source": label_source,
        "num_clients_configured": int(num_clients_configured),
        "active_clients": int(sum(1 for s in sizes if s > 0)),
        "client_sizes": sizes,
        "total_samples": int(sum(sizes)),
        "per_client_label_hist": per_client,
        "global_label_hist": {k: int(global_hist[k]) for k in sorted(global_hist)},
    }
```

**Edits in `scripts/run_experiment.py`** (partition block, currently around lines 520 to 580):

1. Before the proxy-label branch, compute:
   ```python
   require_label = bool(data_cfg.get("require_label_column", False))
   if partition_method == "label_skew":
       if label_column in dataset.column_names:
           label_source = "column"
       else:
           if require_label:
               raise SystemExit(
                   f"ERROR: data.label_column={label_column!r} not in dataset columns "
                   f"{dataset.column_names} and data.require_label_column is true."
               )
           label_source = "length_proxy"
   else:
       label_source = "none"
   ```
   Leave the existing proxy branch unchanged; it now only runs when `label_source == "length_proxy"`.
2. Immediately after `client_datasets` is created, write the stats:
   ```python
   from src.data.partition_stats import compute_partition_stats
   os.makedirs(output_dir, exist_ok=True)
   _pstats = compute_partition_stats(
       client_datasets,
       label_column=label_column if label_column in dataset.column_names else None,
       label_source=label_source,
       partition_method=partition_method,
       partition_alpha=partition_alpha if partition_method == "label_skew" else None,
       data_seed=data_seed,
       num_clients_configured=num_clients,
   )
   with open(os.path.join(output_dir, "partition_stats.json"), "w") as f:
       json.dump(_pstats, f, indent=2)
   ```
   Use the variable names that actually exist in the file (`partition_alpha` may be read from `data_cfg`; check).
3. Do not change how partitions are drawn.

**Tests `tests/test_partition_stats.py`:**

- Synthetic `datasets.Dataset` with 200 rows and a `category` column of 8 values. Using `DataPartitioner(ds, 10, seed=2001).label_skew_partition("category", 0.1)`, assert sizes sum to 200 and `global_label_hist` sums to 200.
- Determinism: two partitioners with seed 2001 give identical `client_sizes` and identical per-client histograms. Seed 2002 gives a different result.
- `active_clients` equals the count of non-empty clients.
- A config with `require_label_column: true` on a dataset lacking the column raises `SystemExit`. Test through a small helper or by factoring the check into a function in `partition_stats.py` (`resolve_label_source(columns, partition_method, label_column, require)`), and use that helper in `run_experiment.py`.

Commit: `B1: partition_stats.json and require_label_column`.

### B2. Hardware and provenance in run_meta

**Why.** The imported runner records `git_dirty` with `git status --porcelain`, which counts untracked files. Once the first run writes into `results/`, every later run on that machine would be marked dirty. It also records no GPU model.

**Edits in `scripts/run_experiment.py`** (the `run_meta` block, currently around line 660):

1. Keep the existing `git_dirty` field unchanged for compatibility. Add:
   ```python
   "git_dirty_tracked": bool(_git(["git", "status", "--porcelain", "--untracked-files=no"])),
   "git_describe": _git(["git", "describe", "--tags", "--always"]),
   ```
2. Add `"hardware": _hardware_info()` using this helper:
   ```python
   def _hardware_info() -> dict:
       import hashlib, socket, subprocess
       import transformers, peft, datasets as hf_datasets
       info = {
           "torch": torch.__version__,
           "transformers": transformers.__version__,
           "peft": peft.__version__,
           "datasets": hf_datasets.__version__,
           "hostname_hash": hashlib.sha256(socket.gethostname().encode()).hexdigest()[:12],
       }
       if torch.cuda.is_available():
           p = torch.cuda.get_device_properties(0)
           info.update(
               cuda_version=torch.version.cuda,
               gpu_name=torch.cuda.get_device_name(0),
               gpu_count=torch.cuda.device_count(),
               gpu_mem_total_bytes=int(p.total_memory),
               peak_mem_allocated_bytes=int(torch.cuda.max_memory_allocated(0)),
           )
           try:
               info["nvidia_smi"] = subprocess.check_output(
                   ["nvidia-smi", "--query-gpu=name,driver_version,memory.total",
                    "--format=csv,noheader"], text=True).strip()
           except Exception:
               info["nvidia_smi"] = None
       elif torch.backends.mps.is_available():
           info["mps"] = True
       return info
   ```
3. Add `"wall_clock_s"`: wall time from script start to the `run_meta` write.

Confirm `run_meta.json` is written after training finishes, so the peak memory figure is meaningful. If it is written earlier, move only the hardware capture to the end and rewrite the file.

**Test:** extend `tests/test_runner_overrides.py` or add `tests/test_run_meta.py` to call `_hardware_info()` and assert the version keys exist.

Commit: `B2: hardware provenance and tracked-only dirty flag`.

### B3. Held-out formatter parity for Dolly

**Why.** Training formats Dolly rows with a `### Context:` block when context is present (`src/federation/client.py`, `tokenize`). The imported held-out evaluator drops the context for `instruction` plus `response` rows, so held-out loss would be measured on a different prompt format than training.

**Edit `scripts/evaluate_instruction_holdout.py`, function `format_instruction_texts`.** Insert this branch before the existing `{"instruction", "response"}` branch:

```python
if {"instruction", "context", "response"}.issubset(cols):
    out = []
    for inst, ctx, resp in zip(examples["instruction"], examples["context"], examples["response"]):
        if ctx:
            out.append(
                f"### Instruction:\n{inst}\n\n"
                f"### Context:\n{ctx}\n\n"
                f"### Response:\n{resp}"
            )
        else:
            out.append(f"### Instruction:\n{inst}\n\n### Response:\n{resp}")
    return out
```

Add these keys to the output row and JSON:

- `"formatter_version": "v2-dolly-context"`
- `"eval_dtype"`: the dtype of the loaded model parameters, read from `next(model.model.parameters()).dtype`

**Test `tests/test_holdout_formatter.py`.** Build a fake model object whose tokenizer records the `texts` argument, then construct `FederatedClient` on a two-row Dolly-style dataset: one row with context, one without. Assert that the recorded training texts equal `format_instruction_texts(...)` on the same rows. If constructing `FederatedClient` with a fake model proves too invasive, assert against hard-coded strings copied character for character from `client.py`, and note that in the CHANGELOG.

Commit: `B3: held-out formatter matches training format for Dolly context`.

### B4. Config generator and experiment configs

Create `scripts/make_vp_configs.py`, which writes 12 files into `config/vp/`:

`vp_{model}_{method}_{het}.yaml` for model in `tl`, `l3`; method in `fedit`, `ffa_lora`, `flora`; het in `a01`, `iid`.

Template for TinyLlama (`tl`):

```yaml
_inherit: ../base_config_4layers.yaml

experiment:
  name: "vp_tl_{method}_{het}"
  description: "Partition-variance study | {method} | TinyLlama-1.1B | Dolly-3k | {het}"

lora:
  r: 16
  lora_alpha: 32
  lora_dropout: 0.1
  target_modules: ["q_proj", "v_proj"]

federated:
  aggregation_method: "{method}"
  num_rounds: 15
  num_clients: 10
  clients_per_round: 10

data:
  dataset_name: "databricks/databricks-dolly-15k"
  dataset_split: "train"
  max_samples: 3000
  partition_method: "{label_skew|iid}"
  partition_alpha: 0.1          # omit for iid
  label_column: "category"
  require_label_column: true
  eval_split: null
  eval_samples: 300

checkpointing:
  save_every: 5
  keep_last_n: 1
```

For LLaMA (`l3`), use `_inherit: ../base_config_llama3_3b.yaml` and the same blocks. Do not restate training hyperparameters, so they come from the base file (float16 base, LoRA params float32, batch 2, grad accumulation 8, lr 1e-4, seq 256, 1 local epoch).

Then write `scripts/print_merged_config.py`, which loads a config through `run_experiment.load_config` and prints it. Run it on all 12 files and confirm:

- `target_modules == ["q_proj", "v_proj"]`. This matters because list merge must replace the base list, and the LLaMA base file lists four modules.
- The model name is correct.
- Rounds, clients, and dataset are as specified.
- `partition_method` and `partition_alpha` are correct.

Save that printout to `docs/merged_configs.txt`.

**Test `tests/test_vp_configs.py`:** for each of the 12 files, assert the merged values above.

Commit: `B4: study configs and generator`.

### B5. Grid definitions and launcher

**Grid files.**

`grids/tl.yaml`:

```yaml
name: tl
tag: prod_v1
methods: [fedit, ffa_lora, flora]
config_pattern: "config/vp/vp_tl_{method}_{het}.yaml"
cells:
  - het: a01
    data_seeds: [2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010]
    run_seeds: [7001, 7002]
  - het: iid
    data_seeds: [2001]
    run_seeds: [7001, 7002, 7003, 7004, 7005]
expected_runs: 75
```

`grids/l3.yaml`: the same structure, with `name: l3`, data seeds 2001 to 2006 for `a01`, run seeds 7001 to 7003 for `iid`, and `expected_runs: 45`.

**Launcher `scripts/run_grid.py`.**

Arguments:

| Argument | Meaning |
|---|---|
| `--grid PATH` | Grid file to run |
| `--shard I --num-shards N` | Which slice of the grid this instance runs |
| `--workers W` | Parallel jobs on one GPU (default 1) |
| `--device cuda` | Compute device |
| `--dry-run` | Print the plan only |
| `--production` | Enforce freeze conditions (below) |
| `--holdout-only` | Run held-out evals only |
| `--max-retries 1` | Retries per failed attempt |

Behavior:

1. **Enumerate cells.** Each cell is (het, data_seed, run_seed, method). Order them so partial completion stays balanced: sort by `(het_order, data_seed, run_seed)` with IID first, then method (fedit, ffa_lora, flora). Assign whole (het, data_seed, run_seed) groups to shards so all methods of a group run on the same GPU: order groups as above, then `shard = group_index mod num_shards`.
2. **Production guard.** When `--production` is set, refuse to start unless `git tag --points-at HEAD` includes `freeze-v1`, the grid YAML has no `overrides`, `git status --porcelain --untracked-files=no` is empty, and `HF_TOKEN` is set.
3. **Output directory.** A cell's directory is `results/raw/vp_{model}_{method}_{het}/{method}/seed_{d}_run{r}/{tag}/<timestamp>/`.
4. **Per-cell state.**
   - **complete:** some timestamp directory has a `results.json` with 15 entries, a `run_meta.json`, a `partition_stats.json`, and an `instruction_holdout.json` file somewhere under `results/downstream_instruction/` for that checkpoint.
   - **needs_holdout:** training is complete but the held-out JSON is missing.
   - **resumable:** a directory has `checkpoints/latest.pt` and no complete `results.json`. Resume with `--resume <dir>`.
   - **fresh:** none of the above.
5. **Training command.**
   ```bash
   python scripts/run_experiment.py --config {cfg} --data-seed {d} --run-seed {r} \
     --tag {tag} --device cuda --save-every 5
   ```
6. **Held-out command** (runs immediately after training, on the same GPU):
   ```bash
   python scripts/evaluate_instruction_holdout.py \
     --checkpoint {run_dir}/final_adapter_state.pt --device cuda \
     --start-index 3000 --num-examples 500 --max-seq-length 256 \
     --summary-csv analysis/holdout_{grid}_shard{I}.csv --skip-existing
   ```
   When `--workers > 1`, use per-cell CSV paths `analysis/holdout_{grid}_shard{I}_{cell_id}.csv` to avoid concurrent writes.
   The dataset is read from the run's `config_merged.yaml`. Assert that the written JSON reports `databricks/databricks-dolly-15k`.
7. **Logging.** Stream stdout and stderr to `logs/{grid}_shard{I}/{cell_id}.log`. Append one JSON line per attempt to `results/launch/{grid}_shard{I}.jsonl` with: `cell_id`, `attempt`, `status`, `start`, `end`, `duration_s`, `train_exit`, `holdout_exit`, `run_dir`, `gpu_name`.
8. **Failure handling.** On failure, retry up to `--max-retries`, resuming if a checkpoint exists. After final failure, log `status: failed` and continue to the next cell.
9. **Summary.** At the end, print counts by status.

**Status tool `scripts/grid_status.py`.** Given `--grid`, scan `results/` and print a table of complete, needs_holdout, resumable, and missing cells. It must work on the Mac after syncing.

**Tests `tests/test_run_grid.py`:**

- Dry-run enumeration gives 75 cells for `tl` and 45 for `l3`.
- The union of shards covers every cell exactly once, for N = 1, 3, and 6.
- The first 3 cells of the `a01` block are the three methods for (2001, 7001).
- The production guard fails on an untagged commit (mock the git calls).

Commit: `B5: grid launcher and status tool`.

### B6. Vast.ai setup script

`scripts/vast_setup.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
: "${HF_TOKEN:?set HF_TOKEN}"
: "${REPO_URL:?set REPO_URL}"          # private repo URL with a read-only deploy key or gh auth
cd /workspace
git clone "$REPO_URL" fedlora-partition-variance
cd fedlora-partition-variance
git checkout freeze-v1
python3 -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt pytest statsmodels
python - <<'EOF'
import torch; print("torch", torch.__version__, "cuda", torch.version.cuda, torch.cuda.get_device_name(0))
EOF
nvidia-smi
huggingface-cli login --token "$HF_TOKEN"
python - <<'EOF'
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM
load_dataset("databricks/databricks-dolly-15k", split="train")
for m in ["TinyLlama/TinyLlama-1.1B-Chat-v1.0", "meta-llama/Llama-3.2-3B"]:
    AutoTokenizer.from_pretrained(m); AutoModelForCausalLM.from_pretrained(m)
print("prefetch ok")
EOF
python -m pytest -q
mkdir -p logs
```

Commit: `B6: vast setup script`.

**Phase B acceptance:** all tests pass; `docs/CHANGELOG.md` lists B1 to B6; `git status` is clean; pushed.

---

## Phase C. Data sanity check (Mac, no training)

Write `scripts/inspect_partitions.py`. It loads Dolly train[0:3000], runs the same partition logic as the runner for data seeds 2001 to 2010 at alpha 0.1, and prints per seed: active clients, client sizes, and category counts. Save the output to `docs/partition_preview.txt`.

Acceptance:

- The global category histogram has 8 categories and sums to 3000.
- Held-out rows 3000 to 3499 have no overlap with rows 0 to 2999 (index check).
- Report the minimum active-client count across the 10 seeds. If any seed gives fewer than 3 active clients, stop and report. That would be a design issue to record in `DECISIONS.md` before freezing, not something to patch silently.

Commit: `C: partition preview`.

---

## Phase D. Mac smoke tests

Run each of these with `--device mps --tag smoke`:

```bash
for m in fedit ffa_lora flora; do
  python scripts/run_experiment.py --config config/vp/vp_tl_${m}_a01.yaml \
    --data-seed 2001 --run-seed 7001 --tag smoke --device mps \
    --override federated.num_rounds=1 --override data.max_samples=300
done
python scripts/evaluate_instruction_holdout.py --checkpoint <one smoke run>/final_adapter_state.pt \
  --device mps --start-index 3000 --num-examples 20 --summary-csv analysis/smoke_holdout.csv
```

**Acceptance table** (record results in `docs/smoke_report.md`):

| Check | Pass condition |
|---|---|
| Label source | `partition_stats.json` has `label_source == "column"` and `label_column == "category"` |
| No proxy | Console log does not contain "instruction-length buckets" |
| Empty clients | All three methods finish even when `active_clients < 10` |
| Bytes | Per-round `upload_mb` equals `active_clients` times a constant per method; record the constant |
| Held-out | JSON has `dataset == databricks/databricks-dolly-15k`, `formatter_version == v2-dolly-context`, finite losses |
| Provenance | `run_meta.json` has `git_dirty_tracked`, `hardware`, and `wall_clock_s` |

Record the TinyLlama per-client upload payload constants. For FedIT and FLoRA the expected value is 9,011,200 bytes (8.59375 MB): q and v, r=16, 22 layers, float32. For FFA-LoRA, record whatever is measured.

Delete smoke outputs from `results/raw` before freezing, or keep them under the `smoke` tag and exclude them in analysis. Prefer deletion, to keep the tree clean.

---

## Phase E. Pre-registration and freeze

1. Write `docs/ANALYSIS_PLAN.md` by copying Phase I and Phase J from this file verbatim, plus the outcome-to-claim table in Section I7.
2. Commit it: `E: pre-registered analysis plan`.
3. Tag the commit and push:
   ```bash
   git tag -a freeze-v1 -m "Code, configs, grids, analysis plan frozen for production runs"
   git push origin main freeze-v1
   ```

After this tag, the only permitted commits are results, analysis outputs, figures, manuscript, and documentation. Any code fix after freeze requires a `DECISIONS.md` entry, a `freeze-v2` tag, and re-running every affected cell.

---

## Phase F. GPU timing gate (Vast.ai)

**Instances.** Rent 2 on-demand instances (not interruptible) with RTX 4090 24 GB, host reliability of at least 99%, at least 60 GB disk, and a CUDA 12.x image. Run `scripts/vast_setup.sh` on each.

**F1. TinyLlama timing.** On instance 1, run one full production-config run outside the grid, with the tag `timing`:

```bash
python scripts/run_experiment.py --config config/vp/vp_tl_flora_a01.yaml \
  --data-seed 2001 --run-seed 7001 --tag timing --device cuda --save-every 5
```

**F2. LLaMA-3.2-3B timing.** On instance 2, run the same command with `config/vp/vp_l3_flora_a01.yaml`.

**F3. Concurrency test.** On instance 1, start two TinyLlama timing runs at once, using data seed 2002 with run seeds 7001 and 7002. Compare total throughput against F1.

**Gate** (record in `DECISIONS.md`):

| Condition | Decision |
|---|---|
| F1 at most 45 min | Proceed with TinyLlama grid |
| F2 finishes, peak memory under 22 GB, at most 75 min | Proceed with LLaMA grid on 4090s |
| F2 out of memory on 4090 | Retry F2 on an A100 40 GB or L40S 48 GB. If at most 75 min, use those for the LLaMA grid |
| F2 over 75 min on every tried GPU | Drop LLaMA. Paper becomes single-scale; record the limitation |
| F3 throughput at least 1.6 times F1 | Use `--workers 2` for TinyLlama |
| Per-client upload bytes differ from Phase D constants (TinyLlama) or from 9,175,040 bytes (LLaMA, FedIT/FLoRA) | Stop. Investigate before any production run |

Timing runs are not production data. Move them to `results/timing/` and exclude them from analysis.

---

## Phase G. Production launch

**Sizing.** Use the F1 and F2 times: GPU-hours equal runs times minutes per run divided by 60. With 33 and 60 minutes per run, TinyLlama needs about 41 GPU-hours and LLaMA about 45. Plan 3 instances per grid, about 14 to 15 hours wall-clock each. Check live Vast prices before renting.

**Launch on each instance** inside `tmux`:

```bash
source .venv/bin/activate
export HF_TOKEN=...   # never written to disk in the repo
python scripts/run_grid.py --grid grids/tl.yaml --shard 0 --num-shards 3 \
  --device cuda --production --workers 1
```

Use shards 0, 1, 2 on the three TinyLlama instances, and the same pattern with `grids/l3.yaml` on the LLaMA instances.

**Sync.** The Mac is the only git writer for results. Every 2 to 3 hours, pull from each instance:

```bash
rsync -avz --prune-empty-dirs \
  --include='*/' \
  --include='results.json' --include='run_meta.json' --include='config_merged.yaml' \
  --include='partition_stats.json' --include='instruction_holdout.json' \
  --include='final_adapter_state.pt' --include='*.jsonl' --include='holdout_*.csv' \
  --exclude='*' \
  root@HOST:/workspace/fedlora-partition-variance/{results,analysis} ./
python scripts/grid_status.py --grid grids/tl.yaml
python scripts/grid_status.py --grid grids/l3.yaml
```

Commit synced artifacts on the Mac. `*.pt` files are ignored by git, so they stay local as backups.

**Monitoring rules**

- A cell that fails twice is investigated from its log before any rerun. The cause goes in `DECISIONS.md`.
- Do not destroy an instance until its shard's jsonl shows every cell complete and the sync has landed on the Mac.
- If an instance dies, start a new one from `freeze-v1`, copy that shard's partial results back to it, and rerun the same shard. The launcher skips or resumes completed cells.

**Phase G acceptance:** `grid_status.py` shows 75 of 75 (and 45 of 45, if LLaMA was kept) complete.

---

## Phase H. Verification

Write `scripts/verify_varpart.py` in the style of the old `verify_numbers.py`: curated assertions, each with a clear failure message naming the run or claim.

| ID | Assertion |
|---|---|
| V1 | Each grid cell has exactly one complete production run tagged `prod_v1`; no duplicates, no extras |
| V2 | Every run has `git_describe == freeze-v1`, `git_dirty_tracked == false`, device `cuda`, and `hardware.gpu_name` present. Library versions are identical across runs of the same grid. `hardware.gpu_name` is identical across all runs of the same grid |
| V3 | Merged config values match Section 0: model, target modules, r, alpha, rounds, clients, dataset, max_samples, partition method, alpha, label column |
| V4 | `partition_stats.label_source == "column"`; the global histogram has 8 keys and sums to 3000 |
| V5 | Same data seed gives identical `client_sizes` and per-client histograms across all methods and run seeds (determinism) |
| V6 | Each round's upload increment equals `active_clients` times the method's per-client payload (constants from Phases D and F) |
| V7 | Each run has a held-out JSON with the Dolly dataset, start 3000, 500 examples, length 256, `formatter_version == v2-dolly-context`, finite loss; `base_loss` is identical (within 1e-6) across all runs of the same model |
| V8 | No NaN or inf in any `results.json` |
| V9 | Manuscript claims: a `CLAIMS` list mapping every number in the paper to its computation from `analysis/*.csv`, filled during Phase L |

Run with `python scripts/verify_varpart.py --grids grids/tl.yaml grids/l3.yaml`. The run must exit 0 before Phase I results are trusted, and again before submission.

jsonl lines with attempt 0 are skip records and are ignored by verification and status counts.

---

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

---

## Phase K. Literature audit (Jerry codes, Cursor assists)

This is a motivation section, not the paper's core. Jerry does the coding by hand; Cursor may help locate PDFs and set up the sheet.

**Selection rule** (write it in the paper): federated LoRA or PEFT fine-tuning of LLMs, 2023 to 2026, reporting at least one non-IID setting built from Dirichlet or category splits. Take the first 25 qualifying papers in reverse chronological order from Jerry's existing search logs, topped up by an arXiv search for "federated LoRA non-IID Dirichlet".

**Sheet `literature/audit.csv` columns:**

`paper_id, title, venue, year, methods_compared, datasets, noniid_scheme, alpha_values, num_clients, num_seeds_reported, partition_seed_separate (yes/no/unclear), variance_reported (none/sd/ci/other), comm_metric (params/bytes/rounds/none), smallest_reported_margin, notes, coded_by, checked`

Jerry re-checks a random 20% of rows and marks `checked`.

**Outputs:** 3 to 4 summary counts for the Introduction, for example the fraction of papers reporting a single seed and the fraction separating partition seeds from training seeds. Every count is generated by `scripts/analysis/audit_summary.py` and covered by V9.

---

## Phase L. Manuscript

**Format.** SAI LaTeX template from thesai.org. Target 6 to 7 pages including figures, about 4,000 words, 25 to 30 references.

**Working title:** *Partition Draws, Not Aggregators: Decomposing Result Variance in Federated LoRA Fine-Tuning Under Non-IID Splits.* Finalize after the results are in.

| Section | Words | Content |
|---|---|---|
| Abstract | 180 to 200 | Question, design (120 runs, 2 scales), three headline numbers, one recommendation |
| 1 Introduction | 600 | Small reported margins in federated LoRA; audit counts; RQ1 to RQ3; contributions list |
| 2 Related work | 500 | Variance in ML benchmarks; non-IID simulation practice; federated LoRA methods and evaluation |
| 3 Study design | 800 | Methods, models, data and category split, seeds, metric, formatter, hardware, variance model |
| 4 Results | 1,200 | I1 to I6, Figs 1 to 3, Tabs 2 to 3 |
| 5 Discussion | 500 | Recommendations for reporting; what pairing does and does not fix; limitations |
| 6 Conclusion | 150 | |
| Declarations | 100 | AI use, data and code availability, funding, conflicts |

**Required limitations paragraph:** two model scales only (1.1B, 3B); one dataset; 15 rounds and 10 clients; 6 partitions at 3B; held-out loss as the only quality metric; exploratory RQ4 with n = 10; local updates use only complete gradient-accumulation blocks; clients with fewer samples than one block contribute no update.

**Writing rules:**

- No em dashes and no curly quotes.
- No sentences starting with First, Furthermore, Moreover, or Additionally.
- Every number comes from `analysis/` and is registered in V9.
- Write the setup section fresh. Do not adapt text from the OJ-CS manuscript.

**Double-blind review copy:**

- No author name, affiliation, or acknowledgments.
- Code availability reads: "Code and run artifacts will be released upon acceptance."
- Cite arXiv:2609.13512 in the third person, only where the byte-accounting approach is used.
- Strip PDF metadata (`\hypersetup{pdfauthor={}}`; check with `pdfinfo`).
- Check figures for embedded file paths or usernames.

**Camera-ready details** (title page and submission form only): Jerry Adams Franklin, Independent Researcher, ORCID, email.

**Declaration on Generative AI.** Jerry must choose the version that matches what actually happened:

- (a) If Claude only edited grammar and language: "The author used Claude (Anthropic) for grammar and language editing only. All technical content, analysis, and interpretations are the author's own."
- (b) If AI tools also helped draft text or write code: "The author used Claude (Anthropic) for language editing and drafting support, and AI coding assistants for implementing experiment and analysis scripts. The author designed the study, verified all code and results, and is responsible for all technical content, analysis, and interpretations."

IJACSA treats undeclared or inaccurately declared AI use as misconduct, so accuracy is required.

**References to verify against primary sources before use** (confirm title, authors, venue, and year for each; add nothing unverified):

- LoRA (Hu et al., ICLR 2022)
- FedAvg (McMahan et al., AISTATS 2017)
- Dirichlet non-IID simulation (Hsu, Qi, Brown, arXiv 2019)
- NIID-Bench (Li et al., ICDE 2022)
- Accounting for variance in ML benchmarks (Bouthillier et al., MLSys 2021)
- Reporting score distributions (Reimers and Gurevych, EMNLP 2017)
- Significance testing in NLP (Dror et al., ACL 2018)
- FedIT (Zhang et al., ICASSP 2024)
- FFA-LoRA (Sun et al., ICLR 2024)
- FLoRA (Wang et al., NeurIPS 2024)
- FederatedScope-LLM (Kuang et al.)
- OpenFedLLM and FedLLM-Bench (Ye et al.)
- TinyLlama (Zhang et al., 2024)
- Llama 3 (Meta, 2024)
- Dolly-15k (Conover et al., 2023)
- Advances and open problems in FL (Kairouz et al., 2021)
- arXiv:2609.13512 (third person)

---

## Phase M. Pre-submission checklist

- [ ] `verify_varpart.py` exits 0, including every V9 claim
- [ ] `python -m pytest -q` passes
- [ ] `scripts/overlap_check.py --manuscript manuscript/main.tex --reference $OLD/docs/ojcs-submission/body.tex --reference $OLD/docs/ojcs-submission/supplemental.tex` reports shared 8-gram overlap under 5%, excluding references. The script reads the old files in place and never copies them.
- [ ] Main body is within the 10-page limit (target 6 to 7 pages)
- [ ] Review copy is anonymized, and PDF metadata is empty
- [ ] Generative AI declaration matches actual use
- [ ] Every reference verified
- [ ] No em dashes or curly quotes: `python scripts/check_typography.py manuscript/` reports clean. The script flags U+2014, U+2013, U+201C, U+201D, U+2018, and U+2019 in every `.tex` and `.bib` file, and flags sentences starting with First, Furthermore, Moreover, or Additionally.
- [ ] Cover letter names the related preprint and states that the present study uses new experiments, different methods, and a different research question
- [ ] Signed IJACSA copyright form completed and attached with the manuscript (download from thesai.org/Home/Downloads; blank copy in `manuscript/template/IJACSA_Copyright.pdf`)
- [ ] Non-Gmail author email ready for the submission form (prefer an address on jerryadamsfranklin.com); ORCID iD ready; affiliation remains Independent Researcher
- [ ] Final commit tagged `ijacsa-submitted-v1`

---

## Phase N. Eighty-four-run addendum (freeze-v3, prod_v2)

Venue target is now IEEE Access (see Phase O and `DECISIONS.md`). This phase adds a pre-registered 84-run addendum under `freeze-v3` / tag `prod_v2` without changing the training path, so new cells pool with `prod_v1`.

Standing rule: every subsequent change request is added here as a numbered phase with acceptance checks before execution. No ad-hoc execution outside the plan. If a request conflicts with this plan, stop and report.

### N1. TinyLlama alpha 0.5 configs

Create three configs identical to the corresponding `a01` files except `partition_alpha: 0.5` and `experiment.name`:

- `config/vp/vp_tl_fedit_a05.yaml`
- `config/vp/vp_tl_ffa_lora_a05.yaml`
- `config/vp/vp_tl_flora_a05.yaml`

Extend `scripts/make_vp_configs.py` with het `a05` (alpha 0.5) so regeneration stays consistent. Extend `tests/test_vp_configs.py` to cover all 15 configs (tl/l3 × three methods × a01/a05/iid for tl; tl a05 only for the new het; l3 keeps a01/iid only, so 12 + 3 = 15 files).

Acceptance: all 15 config files exist; pytest config tests pass; merged `partition_alpha` is 0.5 for `a05` and 0.1 for `a01`.

### N2. New grids (do not edit `grids/tl.yaml` or `grids/l3.yaml`)

`grids/tl_a05.yaml`:

```yaml
name: tl_a05
tag: prod_v2
methods: [fedit, ffa_lora, flora]
config_pattern: "config/vp/vp_tl_{method}_{het}.yaml"
cells:
  - het: a05
    data_seeds: [2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010]
    run_seeds: [7001, 7002]
expected_runs: 60
```

`grids/l3_ext.yaml`:

```yaml
name: l3_ext
tag: prod_v2
methods: [fedit, ffa_lora, flora]
config_pattern: "config/vp/vp_l3_{method}_{het}.yaml"
cells:
  - het: a01
    data_seeds: [2007, 2008, 2009, 2010]
    run_seeds: [7001, 7002]
expected_runs: 24
```

Uses existing `vp_l3_*_a01.yaml` configs. Add `a05` to `HET_ORDER` in `scripts/run_grid.py` so enumeration stays stable.

Tests in `tests/test_run_grid.py`:

- Enumeration counts: `tl_a05` = 60, `l3_ext` = 24
- Same-shard groups (all methods for a (het, data_seed, run_seed) share a shard) for both grids at N in {1, 3, 6}
- Per-shard counts at 3 shards: `tl_a05` → 21/21/18; `l3_ext` → 9/9/6

Acceptance: those tests pass; `grids/tl.yaml` and `grids/l3.yaml` unchanged.

### N3. Pre-registered analysis extension

Append to `docs/ANALYSIS_PLAN.md` (and keep this file's Phase I section in sync where needed):

**I8. Variance components at alpha 0.5** (`analysis/variance_components_a05.csv` or equivalent keyed by het)

TinyLlama only: p = 10, r = 2, m = 3. Same method-of-moments estimators and cluster bootstrap as I1 (B = 2000, seed 12345).

**I9. Heterogeneity gradient** (`analysis/het_gradient.csv`)

Compare `share_P`, `share_PM`, `share_E` between alpha 0.1 and alpha 0.5 on TinyLlama. Bootstrap CIs on the differences (B = 2000, seed 12345).

**I10. LLaMA at p = 10**

Pool `prod_v1` and `prod_v2` LLaMA alpha 0.1 cells (data seeds 2001 to 2010). Recompute I1, I3, and I4 at p = 10. Report the original p = 6 analysis as a sensitivity analysis. State whether the partition main-effect interval still includes zero.

**I8 to I10 outcome-to-claim rows** (pre-registered):

| Result | Claim the paper makes |
|---|---|
| Gradient present: at least one of the differences in `share_P`, `share_PM`, or `share_E` (alpha 0.5 minus alpha 0.1) has a bootstrap CI that excludes zero | Heterogeneity level changes the variance decomposition; report both alphas and the gradient |
| Gradient absent: all three difference CIs include zero | Across alpha 0.1 to 0.5, variance shares do not detectably change at this design; the alpha 0.1 findings generalize over this range |
| At p = 10, the LLaMA partition-share CI excludes zero | Partition main effect is identifiable at 3B with ten draws; update claims accordingly and keep p = 6 as sensitivity |
| At p = 10, the LLaMA partition-share CI still includes zero | Keep the 3B story as interaction-dominated; p = 6 remains a sensitivity analysis |

Acceptance: I8 to I10 and the four rows appear in `ANALYSIS_PLAN.md` before any `prod_v2` analysis runs.

### N4. V12 training-path freeze check

Add V12 to `scripts/verify_varpart.py`. Purpose: prove `prod_v2` pools with `prod_v1`.

- `git diff --name-only freeze-v1..freeze-v3 -- src scripts/run_experiment.py` must be empty (training path unchanged since freeze-v1).
- `scripts/evaluate_instruction_holdout.py` was amended at freeze-v2 (LLaMA float16 holdout). V12 therefore requires `git diff --name-only freeze-v2..freeze-v3 -- scripts/evaluate_instruction_holdout.py` to be empty (eval path pinned at freeze-v2).

Hard stop if either diff is non-empty: do not launch `prod_v2`.

Tag `freeze-v3` on the commit that contains N1 to N4 (configs, grids, analysis-plan extension, V12) with a clean tracked tree for those paths. Report grid enumeration tests and V12 before any instance launch.

Acceptance: V12 passes; freeze-v3 tagged and pushed; pytest for N1/N2 green.

### N5. Launch (three instances, same GPU model)

After N4 report and Jerry approval to launch, follow the runbook in `docs/PHASE_N_RUNBOOK.md` (source of truth for instance specs, setup, sequencing, sync, and destroy). Summary:

- Three on-demand Vast.ai RTX 4090 (24 GB) instances; reject any GPU whose `nvidia-smi` name is not exactly `NVIDIA GeForce RTX 4090`.
- New read-only GitHub and HF tokens; setup on `freeze-v3`; stagger machine starts by 10 minutes.
- Same three machines: finish each machine's `tl_a05` shard before starting its `l3_ext` shard (`--workers 1`, `--max-retries 2`).
- Mac sync every 2 to 3 hours including `final_adapter_state.pt`; destroy only after 60/60, 24/24, 84 adapters, V12 exit 0, and results pushed.

#### N5a. Grid `freeze_tag` and production_guard

`production_guard` reads a required `freeze_tag:` key from the grid YAML and passes only if that exact tag is in `git tag --points-at HEAD`.

- `grids/tl.yaml` and `grids/l3.yaml`: `freeze_tag: freeze-v1`
- `grids/tl_a05.yaml` and `grids/l3_ext.yaml`: `freeze_tag: freeze-v3`

Tests: passes with matching tag; fails with a different tag; fails when the key is absent. V12 must still show an empty diff over `src` and the two run scripts (`run_experiment.py`, `evaluate_instruction_holdout.py` vs freeze-v2).

Update `scripts/vast_setup.sh` to honor `FREEZE_TAG` (default `freeze-v1`).

#### N5b. Partition preview before launch (Mac)

Before any GPU spend, run `inspect_partitions.py` for:

- alpha 0.5, data seeds 2001 to 2010 (TinyLlama a05 cells)
- alpha 0.1, data seeds 2007 to 2010 (LLaMA extension cells)

Append to `docs/partition_preview.txt` with per-seed active clients, effective clients (both model configs), client sizes, and category histograms. Stop if any seed has fewer than 3 active clients or a histogram that is not 8 categories summing to 3000.

#### N5c. V7 pooling check (Phase N acceptance)

Extend V7: `base_loss` must be identical within 1e-6 across **all** runs of a model regardless of tag. Reference values from prod_v1: TinyLlama `2.120666`, LLaMA `2.168946`. Failure means the eval path drifted and the addendum cannot be pooled; do not launch or do not accept prod_v2 cells.

#### N5d. Spot-check CLI provenance

Add to `DECISIONS.md` and `docs/PROVENANCE.md`: the holdout spot-check CLI was reverted to the freeze-v2 blob so prod_v2 pins the prod_v1 eval path; the code that produced the float32 spot-check (max |fp16-fp32| tuned_loss 4.1e-5) remains at commit `ed80372`. The manuscript limitations paragraph should cite that commit.

#### N5e. TinyLlama holdout dtype hotfix (18 Sep, during prod_v2 launch)

freeze-v2 CUDA default force-float16 applied to TinyLlama as well, so the first prod_v2 TL cell recorded `base_loss≈2.120368` (fp16) instead of `2.120666` (fp32). That breaks V7 pooling with prod_v1.

Fix: `evaluate_instruction_holdout.py` uses float16 on CUDA only for Llama-3.2 / 3B-class models; TinyLlama stays float32. Tag `freeze-v3.1`; `tl_a05` / `l3_ext` `freeze_tag` point at it. Re-holdout any completed TL adapters before continuing the grid.

Acceptance: re-holdout of the first TL adapter yields `base_loss` within 1e-6 of 2.120666 and `eval_dtype=torch.float32`.

#### N5 acceptance (pre-launch)

- N5a to N5d complete; production_guard and freeze_tag tests green; V12 empty diffs; partition preview appended and stop conditions pass; V7 extended; DECISIONS/PROVENANCE updated; runbook current.

#### N5 acceptance (post-run)

`grid_status` shows 60/60 and 24/24 complete; 84 local adapters present; tokens revoked after destroy.

### N6. Post-run base_loss diagnosis, holdout repair, and I8–I10 (19 Sep)

Blocking before destroy / analysis:

**N6-1.** Diff failing LLaMA holdout JSON vs a passing prod_v2 peer (eval fields) and run_meta hardware.

**N6-2.** On the surviving 4090 (torch 2.2.0+cu121), re-run the named cell's holdout twice under `freeze-v3.1` to scratch tags. If both match 2.1689459 within 1e-6, repair; if the two re-runs differ, STOP (nondeterminism). Extend repair to every prod_v2 LLaMA cell with the anomalous base_loss on non-2.2.0 stacks. Re-run verifier; V7 must PASS.

**N6-3.** Rebuild `analysis/runs.csv` over prod_v1+prod_v2 (204 rows). Run I8, I9, I10; write `variance_components_a05.csv`, `het_gradient.csv`, `variance_components_l3_p10.csv`, and `i8_i10_selected_claims.txt`.

**N6-4.** DECISIONS rows for freeze-v3.1 mid-grid counts and the LLaMA base_loss resolution.

**N6-5.** Phase N report: retry census (tl_a05 38 failed attempts; l3_ext 19; all recovered) with causes from logs.

Acceptance: V7 PASS; 204-row runs.csv; I8–I10 artifacts present; DECISIONS + phase_n_report updated.

### N6-decisions (earlier). DECISIONS.md entries

Append three rows (do not edit past rows):

1. Venue change to IEEE Access (IJACSA remains fallback; never dual-submit).
2. The 84-run addendum under freeze-v3 / prod_v2 (alpha 0.5 on TinyLlama; LLaMA partition extension to data seeds 2007 to 2010).
3. Adapters retained for every prod_v2 cell (prod_v1 adapters may already be incomplete).

### N7. MixedLM re-specification and refs expansion

Re-specify the MixedLM cross-check so the partition component identifies (cross-check only; moment estimates stay primary). Expand `manuscript/refs.bib` toward about 25 verified entries; every new entry verified against its primary source.

### Phase N acceptance

- All tests pass
- `freeze-v3` tagged
- V12 passes
- V7 pooling: base_loss matches prod_v1 references across tags (2.120666 tl, 2.168946 l3)
- `grid_status` shows 60/60 (`tl_a05`) and 24/24 (`l3_ext`) complete
- 84 adapters present locally

### Phase N hard stop

If both grids are not complete by end of Mon 22 Sep, drop the incomplete grid entirely rather than reporting partial cells, and move to Phase O.

---

## Phase O. IEEE Access rework

Target venue: IEEE Access (single-anonymized review). Do not submit to IJACSA and Access at the same time.

### O1. The Partition-Draw Reporting Protocol

Name the contribution **the Partition-Draw Reporting Protocol**, spelled out, with no acronym (PDR, PDP, PVR, and PDA collide with common engineering terms). After first mention, use "the protocol".

State it as three numbered steps in both the abstract and a dedicated discussion subsection:

1. Report the number of partition draws, and the partition seeds, separately from training seeds.
2. Pair method comparisons on the same partition draws.
3. Report the minimum difference the design can detect, at the design's number of draws.

### O2. Advance over the state of the art

Add an explicit advance-over-the-state-of-the-art paragraph to the introduction (Access Stage 3 desk screening).

### O2b. Novelty positioning (literature check, 18 Sep) — DONE 18 Sep 2026

Independent of prod_v2 GPU runs. Do not touch grids or `analysis/` while prod_v2 is in flight.

**O2b-1.** DONE. Rewrote Gap in `02_related_work.tex`: cites adjacent variance decompositions (arXiv:2510.26714, 2605.18229, 2609.02499); FL nearest work aggregates across seeds (Jimenez-Gutierrez et al. 2025; NIID-Bench); concludes federated partition draw not treated as variance component for LoRA instruction tuning.

**O2b-2.** DONE. Setup sentence on FlowerTune (arXiv:2506.02961): leaderboards report single-configuration results, so design needs author-controlled seeds.

**O2b-3.** DONE. Five new refs verified against primary sources; `refs.bib` count 14 (target ~25).

**O2b-4.** DONE. DECISIONS row 18 Sep 2026 narrowing Gap claim.

### O2c. Reference expansion (home sentences, 18 Sep) — DONE 18 Sep 2026

Independent of prod_v2 GPU runs. Do not touch grids or `analysis/`. Every new cite must have a home sentence; drop any entry that cannot be verified against a primary source.

**O2c-1.** DONE. Setup cites: LoRA, FedAvg, Dolly-15k, TinyLlama, Llama 3 herd.

**O2c-2.** DONE. Related-work cites: Yang survey; FederatedScope-LLM; OpenFedLLM + FedLLM-Bench with FlowerTune; Cho hetLoRA clause on FLoRA.

**O2c-3.** DONE. Reimers (EMNLP 2017); Dror (ACL 2018) at Holm; Kairouz (FnT ML 2021) at client heterogeneity.

**O2c-4.** DONE. `refs.bib` count 27; STATUS.md updated; verification reported; commit on phase-n.

**O2c-5 (correction, 18 Sep).** Cho venue matched to FLoRA's bibliography (workshop NeurIPS 2023), not arXiv-only; LoRA ICLR venue confirmed in-session via Semantic Scholar (`venue` + DBLP `conf/iclr/HuSWALWWC22`), not assumed from a blocked OpenReview fetch.

Verification log (field → source):

| Entry | Field | Confirmed by |
|---|---|---|
| `cho2024hetlora` | title, authors (incl. Matt Barnes), booktitle, year 2023 | FLoRA PDF arXiv:2409.05976 References [3] (same NeurIPS-published paper cited adjacent in our Related Work) |
| `cho2024hetlora` | arXiv twin 2401.06432 | arXiv API (identity check only; bib venue follows FLoRA, not arXiv) |
| `hu2022lora` | title, authors | arXiv API 2106.09685 |
| `hu2022lora` | venue ICLR | Semantic Scholar API `ARXIV:2106.09685` → `venue`/`publicationVenue` = International Conference on Learning Representations; `externalIds.DBLP` = `conf/iclr/HuSWALWWC22` |
| `hu2022lora` | year 2022 | DBLP key suffix `22` from that same S2 payload (S2 `year` field was 2021 = arXiv year) |

### O3. IEEE Access template and de-anonymization

Convert the manuscript to the IEEE Access template. Single-anonymized review: restore author name, affiliation "Independent Researcher", real email, and ORCID.

### O4. Public artifacts

Replace the code-availability statement with a public repository link plus a Zenodo DOI.

### O5. Results update for I8 to I10

Update results, discussion, abstract, and conclusion for I8 to I10 per the pre-registered outcome-to-claim rows. Lead with the protocol as the contribution.

### O6. Pre-submission checks

- Page and format compliance with the Access template
- `check_typography.py` clean
- `verify_varpart.py` exits 0 with V9 refreshed for every new number
- Overlap check re-run against the OJ-CS body and supplement
- Every reference verified against its primary source

### Phase O acceptance

Verifier exit 0; all checks clean; final PDF reviewed in the Claude Project before submission.

---

## 14. Go/no-go (Mon 21 Sep)

Submit on 24 Sep only if all of these hold:

1. Phase G complete for TinyLlama (75 of 75). LLaMA is either complete (45 of 45) or formally dropped in `DECISIONS.md`.
2. `verify_varpart.py` V1 to V8 pass.
3. I1 to I5 computed, and Figs 1 to 3 rendered.
4. Full draft of Sections 1 to 5 exists.

If any item fails, target the November IJACSA cycle (confirm the date with info@thesai.org), and record the decision.

## 15. Stop conditions (halt and report immediately)

- Any smoke or timing check in Phases D or F fails.
- Per-client upload bytes deviate from the recorded constants.
- `label_source` is anything other than `column` in any production run.
- Partitions for the same data seed differ across runs (V5).
- Any need to edit aggregator or training-loop code.
