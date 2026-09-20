#!/usr/bin/env bash
# O11 Linux verification — run inside a clean Linux container.
# Expects the repo mounted at /work (including .git for V11/V12).
set -euo pipefail
cd /work
python3 --version
uname -a

# git is required by verify_varpart V11/V12 (subprocess to freeze tags).
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq git >/tmp/o11_apt_git.log

rm -rf /tmp/o11_venv
python3 -m venv /tmp/o11_venv
source /tmp/o11_venv/bin/activate
pip install -U pip

echo "===== pip install -r requirements.txt ====="
pip install -r requirements.txt
echo "PIP_INSTALL_EXIT=$?"

echo "===== pip freeze (key packages) ====="
pip freeze | grep -E '^(numpy|scipy|statsmodels|pandas|torch|transformers|peft|datasets|evaluate|matplotlib|pytest|huggingface-hub)==' | tee /tmp/o11_pip_freeze_key.txt

echo "===== pytest -q ====="
set +e
python -m pytest -q 2>&1 | tee /tmp/o11_pytest.txt
PYTEST_EXIT=${PIPESTATUS[0]}
set -e
echo "PYTEST_EXIT=$PYTEST_EXIT"
tail -5 /tmp/o11_pytest.txt

# Snapshot committed analysis outputs before regeneration
mkdir -p /tmp/o11_committed_analysis
cp -a analysis/*.csv /tmp/o11_committed_analysis/ 2>/dev/null || true
cp -a analysis/i7_selected_claims.txt analysis/i8_i10_selected_claims.txt analysis/l3_p10_truncation_flag.txt /tmp/o11_committed_analysis/ 2>/dev/null || true

GRIDS=(grids/tl.yaml grids/l3.yaml grids/tl_a05.yaml grids/l3_ext.yaml)

echo "===== build_runs_table.py (204-cell grids) ====="
set +e
python scripts/analysis/build_runs_table.py --grids "${GRIDS[@]}" 2>&1 | tee /tmp/o11_build_runs.txt
BUILD_EXIT=${PIPESTATUS[0]}
set -e
echo "BUILD_EXIT=$BUILD_EXIT"

echo "===== analyze_variance.py ====="
set +e
python scripts/analysis/analyze_variance.py --runs analysis/runs.csv --out-dir analysis 2>&1 | tee /tmp/o11_analyze_var.txt
VAR_EXIT=${PIPESTATUS[0]}
set -e
echo "VAR_EXIT=$VAR_EXIT"

echo "===== analyze_i8_i10.py ====="
set +e
python scripts/analysis/analyze_i8_i10.py --runs analysis/runs.csv --out-dir analysis 2>&1 | tee /tmp/o11_analyze_i8.txt
I8_EXIT=${PIPESTATUS[0]}
set -e
echo "I8_EXIT=$I8_EXIT"

echo "===== verify_varpart.py ====="
set +e
python scripts/verify_varpart.py --grids "${GRIDS[@]}" 2>&1 | tee /tmp/o11_verify.txt
VERIFY_EXIT=${PIPESTATUS[0]}
set -e
echo "VERIFY_EXIT=$VERIFY_EXIT"
tail -8 /tmp/o11_verify.txt

echo "===== diff analysis CSVs vs committed snapshot (byte; informational) ====="
CITE_GLOBS=(
  runs.csv
  variance_components.csv
  variance_components_a05.csv
  variance_components_by_het.csv
  variance_components_l3_p10.csv
  het_gradient.csv
  rank_flip.csv
  rank_flip_pairs.csv
  rank_flip_l3_p10.csv
  rank_flip_pairs_l3_p10.csv
  power.csv
  power_l3_p10.csv
  method_means.csv
  method_pairwise.csv
  comm.csv
  iid_noise.csv
  partition_effects.csv
  partition_spearman.csv
  sd_pair_empirical.csv
  absolute_variance_alpha_posthoc.csv
  claims.csv
  stack_census.csv
  stack_effect.csv
  i7_selected_claims.txt
  i8_i10_selected_claims.txt
  l3_p10_truncation_flag.txt
)

DIFF_REPORT=/tmp/o11_diff_report.txt
: > "$DIFF_REPORT"
DIFFERS=0
for f in "${CITE_GLOBS[@]}"; do
  old="/tmp/o11_committed_analysis/$f"
  new="analysis/$f"
  if [ ! -f "$old" ]; then
    echo "MISSING_COMMITTED $f" | tee -a "$DIFF_REPORT"
    continue
  fi
  if [ ! -f "$new" ]; then
    echo "MISSING_NEW $f" | tee -a "$DIFF_REPORT"
    DIFFERS=1
    continue
  fi
  if cmp -s "$old" "$new"; then
    echo "IDENTICAL $f" | tee -a "$DIFF_REPORT"
  else
    echo "DIFFERS $f" | tee -a "$DIFF_REPORT"
    DIFFERS=1
    diff -u "$old" "$new" | head -40 | tee -a "$DIFF_REPORT" || true
  fi
done
echo "BYTE_DIFFERS_FLAG=$DIFFERS"

echo "===== manuscript-precision compare (O12 gate) ====="
set +e
python scripts/ops/o12_manuscript_precision.py \
  --committed /tmp/o11_committed_analysis \
  --regenerated analysis \
  --report /tmp/o12_manuscript_precision.txt 2>&1 | tee /tmp/o12_precision_stdout.txt
PREC_EXIT=${PIPESTATUS[0]}
set -e
echo "PREC_EXIT=$PREC_EXIT"

# Always restore committed archive (do not overwrite paper tables with ULP noise).
echo "===== restoring committed analysis outputs (keep archive) ====="
for f in "${CITE_GLOBS[@]}"; do
  if [ -f "/tmp/o11_committed_analysis/$f" ]; then
    cp -a "/tmp/o11_committed_analysis/$f" "analysis/$f"
  fi
done

{
  echo "OS=$(uname -s) $(uname -m) $(uname -r)"
  echo "PYTHON=$(python --version 2>&1)"
  echo "DATE_UTC=$(date -u +%Y-%m-%d)"
  cat /tmp/o11_pip_freeze_key.txt
  echo "PYTEST_EXIT=$PYTEST_EXIT"
  echo "BUILD_EXIT=$BUILD_EXIT"
  echo "VAR_EXIT=$VAR_EXIT"
  echo "I8_EXIT=$I8_EXIT"
  echo "VERIFY_EXIT=$VERIFY_EXIT"
  echo "BYTE_DIFFERS_FLAG=$DIFFERS"
  echo "PREC_EXIT=$PREC_EXIT"
} | tee /tmp/o11_env_summary.txt

mkdir -p /work/analysis/logs
cp /tmp/o11_env_summary.txt /work/analysis/logs/o11_env_summary.txt
cp /tmp/o11_diff_report.txt /work/analysis/logs/o11_diff_report.txt
cp /tmp/o11_pip_freeze_key.txt /work/analysis/logs/o11_pip_freeze_key.txt
cp /tmp/o11_pytest.txt /work/analysis/logs/o11_pytest.txt
cp /tmp/o11_verify.txt /work/analysis/logs/o11_verify.txt 2>/dev/null || true
cp /tmp/o11_build_runs.txt /work/analysis/logs/o11_build_runs.txt 2>/dev/null || true
cp /tmp/o12_manuscript_precision.txt /work/analysis/logs/o12_manuscript_precision.txt 2>/dev/null || true
cp /tmp/o12_precision_stdout.txt /work/analysis/logs/o12_precision_stdout.txt 2>/dev/null || true

echo "O11_DONE"
# Fail the container if manuscript precision or verify failed (byte ULP is OK).
if [ "$PYTEST_EXIT" -ne 0 ] || [ "$BUILD_EXIT" -ne 0 ] || [ "$VAR_EXIT" -ne 0 ] \
   || [ "$I8_EXIT" -ne 0 ] || [ "$VERIFY_EXIT" -ne 0 ] || [ "$PREC_EXIT" -ne 0 ]; then
  exit 1
fi
exit 0
