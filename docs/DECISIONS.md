# Decision log

Record material decisions that affect scope, design, or analysis. Do not edit past rows; append new ones.

| date | decision | reason | evidence |
|---|---|---|---|
| 16 Sep 2026 | Venue IJACSA October cycle (submit by 24 Sep); fall back to November if go/no-go fails on 21 Sep | Conference timeline | IMPLEMENTATION_PLAN Section 1 and Section 14 |
| 16 Sep 2026 | Methods limited to fedit, ffa_lora, flora | Frozen design for partition-variance study | docs/SCOPE.md |
| 16 Sep 2026 | Primary model TinyLlama-1.1B; LLaMA-3.2-3B subject to Phase F timing gate | Cost and fit on on-demand RTX 4090 | docs/SCOPE.md; Phase F gate |
| 16 Sep 2026 | Old-repo local path for Phase M overlap check is federated-lora-experiments | Private reference name fedlora-protocols; local folder differs | Task 01 verification |
| 16 Sep 2026 | Phase B committed directly to main per IMPLEMENTATION_PLAN.md | plan instruction; private single-author repo; rewrite adds risk | commits 2393d04..ec68b81 |
| 16 Sep 2026 | From Phase C: work on branch phase-x, push the branch, after review fast-forward merge into main (git merge --ff-only). No force-push ever | usual branch rule going forward; skip PRs without a reviewer | STATUS.md 16 Sep 2026 |
| 16 Sep 2026 | Add pre-registered partition statistic: effective clients (active clients with at least one optimizer step) and discarded trailing samples, per model | client.py steps only on full accumulation blocks (no drop_last), so clients with n<=12 (TinyLlama) or n<=14 (LLaMA) upload the unchanged global adapter | src/federation/client.py train loop, Phase C preview |
