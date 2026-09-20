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
# Pin the CUDA 12.1 wheel explicitly. Plain `torch==2.2.0` from the default
# index does not replace a newer preinstalled image torch (seen: 2.11+cu128,
# 2.14+cu130 on two of three prod_v2 hosts).
pip install torch==2.2.0+cu121 --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt pytest statsmodels
python - <<'EOF'
import sys
import torch
print("torch", torch.__version__, "cuda", torch.version.cuda, torch.cuda.get_device_name(0))
if torch.__version__ != "2.2.0+cu121":
    print(
        f"ERROR: expected torch 2.2.0+cu121, got {torch.__version__!r}",
        file=sys.stderr,
    )
    sys.exit(1)
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
