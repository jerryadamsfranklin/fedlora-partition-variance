#!/usr/bin/env bash
# O11: Linux verify via Docker Desktop (run from an IDE terminal that can reach docker.sock).
set -euo pipefail
cd "$(cd "$(dirname "$0")/../.." && pwd)"
docker pull --platform linux/amd64 python:3.12-slim-bookworm
docker run --rm --platform linux/amd64 \
  -v "$PWD:/work" -w /work \
  python:3.12-slim-bookworm \
  bash scripts/ops/o11_linux_verify.sh
