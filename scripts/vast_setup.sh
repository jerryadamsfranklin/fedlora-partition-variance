#!/usr/bin/env bash
set -euo pipefail
: "${HF_TOKEN:?set HF_TOKEN}"
: "${REPO_URL:?set REPO_URL}"          # private repo URL with a read-only deploy key or gh auth
FREEZE_TAG="${FREEZE_TAG:-freeze-v1}"
cd /workspace
git clone "$REPO_URL" fedlora-partition-variance
cd fedlora-partition-variance
git fetch --tags
git checkout "$FREEZE_TAG"
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
echo "setup ok at $(git describe --tags --exact-match)"
