# Reproduce

Copy-paste commands for the public archive. Grids pin `freeze_tag`, and the
production guard refuses to start a production run from an untagged or dirty
tree, so a casual checkout cannot silently diverge from the archived cells.

## 1. Environment

```bash
git clone https://github.com/jerryadamsfranklin/fedlora-partition-variance.git
cd fedlora-partition-variance
git checkout v0.9.2   # or a later archive tag
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

CUDA production hosts must install the cu121 build of `torch==2.2.0` from the
PyTorch index (see `scripts/vast_setup.sh`) and assert
`torch.__version__ == "2.2.0+cu121"` before launching grids.

Set `HF_TOKEN` in the environment for gated model downloads. Never commit it.

### Verified environment

The pinned stack was installed and executed on **2026-09-20** inside Docker
`python:3.12-slim-bookworm` (`linux/amd64`):

- OS: Linux x86_64 `6.12.54-linuxkit`
- Python: 3.12.14
- `pip freeze` (key packages): `numpy==1.26.0`, `scipy==1.12.0`,
  `statsmodels==0.14.1`, `pandas==2.2.0`, `torch==2.2.0`,
  `transformers==4.45.2`, `peft==0.10.0`, `datasets==2.18.0`,
  `evaluate==0.4.1`, `matplotlib==3.8.0`, `pytest==8.3.5`
- `pytest -q`: **84 passed**
- `verify_varpart.py` over the four production grids: **33/33 claims** (exit 0)

**macOS was not used for the analysis path.** Local macOS installs may fail or
segfault on the pinned NumPy/OpenBLAS wheels; use Linux (Docker is fine) to
reproduce analysis and tests.

### Numerical reproducibility

Under the pinned Linux stack, regenerating `analysis/` from the 204-cell
`runs.csv` reproduces every manuscript-cited value to the number of digits
printed in the paper (`scripts/ops/o12_manuscript_precision.py` and V9).
Last-digit (ULP) differences in raw CSV floats across OpenBLAS builds are
expected and are **not** treated as archive updates. The verifier checks claim
values rather than byte identity of CSV files. Keep the committed
`analysis/*.csv` tables; do not replace them with regenerated ULP variants.

## 2. Tests

```bash
pytest -q
```

## 3. Smoke grid (CPU or GPU)

```bash
python scripts/run_grid.py --grid grids/smoke.yaml --shard 0 --num-shards 1
```

## 4. Single production cell

Check out the freeze tag named in the grid (`freeze-v1` for `grids/tl.yaml` /
`grids/l3.yaml`, `freeze-v3.1` for `grids/tl_a05.yaml` / `grids/l3_ext.yaml`),
ensure a clean tracked tree, then:

```bash
python scripts/run_grid.py \
  --grid grids/tl.yaml \
  --production \
  --shard 0 --num-shards 75 \
  --workers 1
```

`--production` enables the guard: matching `freeze_tag`, clean git state, and
hardware gates. Omitting it is for local debugging only.

## 5. Full grids (204 cells)

```bash
# 120-cell core on freeze-v1
python scripts/run_grid.py --grid grids/tl.yaml --production --shard I --num-shards 3
python scripts/run_grid.py --grid grids/l3.yaml --production --shard I --num-shards 3

# 84-cell addendum on freeze-v3.1
python scripts/run_grid.py --grid grids/tl_a05.yaml --production --shard I --num-shards 3
python scripts/run_grid.py --grid grids/l3_ext.yaml --production --shard I --num-shards 3
```

Replace `I` with the shard index for each host. Expected wall time is about
27 minutes per TinyLlama cell and about 51 minutes per LLaMA cell on one RTX
4090; the full design is about 150 GPU-hours.

## 6. Analysis

Rebuild the run table over **all four** production grids (204 cells), then I1–I6
and I8–I10:

```bash
python scripts/analysis/build_runs_table.py \
  --grids grids/tl.yaml grids/l3.yaml grids/tl_a05.yaml grids/l3_ext.yaml
python scripts/analysis/analyze_variance.py --runs analysis/runs.csv --out-dir analysis
python scripts/analysis/analyze_i8_i10.py --runs analysis/runs.csv --out-dir analysis
```

`analyze_variance.py` keeps LLaMA primary I1 at p=6 (seeds 2001–2006) even when
`l3_ext` adds seeds 2007–2010; I10 owns the p=10 pool.

## 7. Verifier and claim map

```bash
python scripts/verify_varpart.py \
  --grids grids/tl.yaml grids/l3.yaml grids/tl_a05.yaml grids/l3_ext.yaml
```

Exit 0 is required before trusting tables. The V9 step regenerates
`analysis/claims.csv` from the in-repo claim registry so manuscript numbers
cannot drift from their sources.
