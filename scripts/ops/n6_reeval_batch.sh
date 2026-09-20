#!/usr/bin/env bash
# Campaign tooling (n6 re-eval batch); not part of the analysis path.
# Re-eval anomalous l3 prod_v2 holdouts on torch 2.2.0 host.
set -u
cd /workspace/fedlora-partition-variance
source .venv/bin/activate
export CUDA_VISIBLE_DEVICES=0 NVIDIA_VISIBLE_DEVICES=0 PYTHONUNBUFFERED=1
export HF_TOKEN="$(tr -d '\n' < /workspace/.hf_token)"
export HUGGING_FACE_HUB_TOKEN="$HF_TOKEN"
export HF_HOME=/workspace/.hf_home
export TOKENIZERS_PARALLELISM=false

LIST=/tmp/n6_anomalous.txt
n=0
total=$(grep -c . "$LIST")
while read -r dir; do
  [ -z "$dir" ] && continue
  n=$((n + 1))
  ckpt="$dir/final_adapter_state.pt"
  rel="${dir#results/raw/}"
  hold="results/downstream_instruction/${rel}/instruction_holdout.json"
  rm -f "$hold"
  echo "===== [$n/$total] $dir $(date -u) ====="
  python scripts/evaluate_instruction_holdout.py \
    --checkpoint "$ckpt" \
    --device cuda \
    --dataset databricks/databricks-dolly-15k \
    --start-index 3000 \
    --num-examples 500 \
    --max-seq-length 256 \
    --summary-csv analysis/n6_reeval_batch.csv
  python3 - "$hold" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))["row"]
print("OK", r["base_loss"], r["tuned_loss"], r["eval_dtype"])
PY
done < "$LIST"
echo BATCH_DONE
