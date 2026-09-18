# Phase N runbook (prod_v2 / freeze-v3)

Follow this document for the 84-run addendum. Do not improvise instance choice, grid order, or destroy timing. Plan reference: Phase N step N5 in `docs/IMPLEMENTATION_PLAN.md`.

## 1. Instances

Rent **3** on-demand [Vast.ai](https://vast.ai) instances with:

| Spec | Requirement |
|---|---|
| GPU | NVIDIA GeForce RTX 4090, 24 GB |
| Host reliability | at least 99% |
| Disk | at least 60 GB |
| Image | CUDA 12.x |

**GPU name gate (hard reject).** On each machine, before any training:

```bash
nvidia-smi --query-gpu=name --format=csv,noheader
```

The printed name must be exactly `NVIDIA GeForce RTX 4090`. The RTX 4090 D variant reports a different string and would break V2 (`hardware.gpu_name` identical across the grid). Destroy and replace any non-matching instance.

**Stagger starts by 10 minutes.** Bring up machine 0, wait 10 minutes, then machine 1, then machine 2. All three download TinyLlama and LLaMA-3.2-3B from Hugging Face on the same token; simultaneous 3B pulls occasionally hit rate limits, and a failed download at cell 1 wastes an hour of confusion.

## 2. Tokens

Create a **new** read-only GitHub token and a **new** Hugging Face token for this campaign. The previous pair lived on destroyed machines; do not reuse them.

After all instances are destroyed (Section 7), revoke both tokens.

## 3. Per-instance setup

On each machine `i` in `{0, 1, 2}`:

```bash
export HF_TOKEN=...          # new HF token
export REPO_URL=...          # private clone URL using the new read-only GitHub token
export FREEZE_TAG=freeze-v3

bash scripts/vast_setup.sh   # checks out FREEZE_TAG (default freeze-v1 if unset)
```

Then:

```bash
cd /workspace/fedlora-partition-variance
# Strip the token from the remote URL so it is not left in .git/config
git remote set-url origin git@github.com:jerryadamsfranklin/fedlora-partition-variance.git
# or: git remote set-url origin https://github.com/jerryadamsfranklin/fedlora-partition-variance.git

git describe --tags --exact-match   # must print: freeze-v3
nvidia-smi --query-gpu=name --format=csv,noheader   # must be exact RTX 4090 name
source .venv/bin/activate
python -m pytest -q
```

Do not start the grid until `git describe --tags --exact-match` prints `freeze-v3` and pytest passes.

## 4. Launch sequencing (same three instances)

Run both grids on the **same** three machines. **TinyLlama first, then LLaMA.** Do **not** start `l3_ext` on a machine until that machine's `tl_a05` shard is fully complete. Running both at once on one 4090 halves throughput for both (Phase F concurrency was 1.06x, not 1.6x); sequential is faster overall.

Use `tmux`. `--workers 1`. `--max-retries 2`.

### 4a. TinyLlama grid (`tl_a05`, 60 cells)

On machine `i` (`i = 0, 1, 2`), inside tmux:

```bash
cd /workspace/fedlora-partition-variance
source .venv/bin/activate
python scripts/run_grid.py --grid grids/tl_a05.yaml --shard i --num-shards 3 \
  --device cuda --production --workers 1 --max-retries 2
```

Shard sizes: 21 / 21 / 18 cells. Expect about **10 hours** per machine for this grid, plus setup and held-out evals.

### 4b. LLaMA extension (`l3_ext`, 24 cells)

Only after that machine's `tl_a05` shard reports complete:

```bash
python scripts/run_grid.py --grid grids/l3_ext.yaml --shard i --num-shards 3 \
  --device cuda --production --workers 1 --max-retries 2
```

Shard sizes: 9 / 9 / 6 cells. Expect about **9 hours** per machine for this grid.

**Wall-clock per machine:** roughly **24 to 30 hours** including setup and held-out evals.

## 5. Mac-side sync (every 2 to 3 hours)

Cursor runs these from the Mac. The Mac is the only git writer for results. Include adapters:

```bash
# For each HOST (replace HOST and SSH port as rented):
rsync -avz --prune-empty-dirs \
  --include='*/' \
  --include='results.json' --include='run_meta.json' --include='config_merged.yaml' \
  --include='partition_stats.json' --include='instruction_holdout.json' \
  --include='final_adapter_state.pt' --include='*.jsonl' --include='holdout_*.csv' \
  --exclude='*' \
  -e 'ssh -p PORT' \
  root@HOST:/workspace/fedlora-partition-variance/{results,analysis,logs} ./

python scripts/grid_status.py --grid grids/tl_a05.yaml
python scripts/grid_status.py --grid grids/l3_ext.yaml

# Adapter count under prod_v2 (expect 84 when both grids finish):
find results -path '*prod_v2*' -name 'final_adapter_state.pt' | wc -l
```

Commit synced artifacts on the Mac when a meaningful batch lands. `*.pt` files stay local (gitignored) as backups.

## 6. Completion gate (before any destroy)

All of the following must hold:

1. `grid_status.py --grid grids/tl_a05.yaml` shows **60/60** complete
2. `grid_status.py --grid grids/l3_ext.yaml` shows **24/24** complete
3. **84** adapters present on the Mac under the `prod_v2` tag
4. `python scripts/verify_varpart.py --grids grids/tl.yaml grids/l3.yaml` still exits 0 with **V12** pass (training path unchanged; eval pinned)
5. Synced results committed and pushed to `origin`

Hard stop from the plan: if both grids are not complete by end of Mon 22 Sep, drop the incomplete grid entirely rather than reporting partial cells, and move to Phase O.

## 7. Destroy and revoke

Only after Section 6:

1. Destroy all three Vast.ai instances.
2. Revoke the GitHub token and the Hugging Face token used for this campaign.

## 8. Checklist

- [ ] Three exact RTX 4090 instances (name gate passed)
- [ ] New GitHub and HF tokens; staggered starts (+0 / +10 / +20 min)
- [ ] Partition preview appended for alpha 0.5 (2001-2010) and alpha 0.1 (2007-2010); stop conditions pass
- [ ] Each machine: `freeze-v3` exact-match, pytest green, remote URL stripped
- [ ] Grid `freeze_tag` matches HEAD (`freeze-v3` for prod_v2); production_guard green
- [ ] Each machine: `tl_a05` shard complete before `l3_ext` starts
- [ ] Mac sync includes `final_adapter_state.pt`; status 60/60 and 24/24
- [ ] 84 adapters on Mac; V7 base_loss pooling and V12 exit 0; results pushed
- [ ] Instances destroyed; both tokens revoked