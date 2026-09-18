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
| 16 Sep 2026 | Shard by (het, data_seed, run_seed) group, not by cell | cell-level modulo sharding put each method on a different instance, confounding method with hardware | Phase D dry-run |
| 16 Sep 2026 | Communication compared only within method across partitions; methods are not ranked by bytes | as implemented, FFA-LoRA uploads A and B (9,011,200 B per client) and downloads B only (3,244,032 B); client/aggregator code is frozen | Phase D smoke bytes |
| 16 Sep 2026 | Launcher fixes before freeze: checkpoint path normalization, no retraining of complete cells, tag check via --points-at, per-cell holdout CSV with workers>1, smoke-grid support | relative vs absolute checkpoint paths caused every cell to fail its holdout check and retrain | run_grid.py review, Phase D |
| 17 Sep 2026 | Phase F gates: keep TinyLlama and LLaMA-3.2-3B on RTX 4090; use --workers 1 for TinyLlama | F1 29.3 min; F2 65.2 min and ~9 GB peak; F3 concurrency throughput 1.06× F1 (<1.6×); upload bytes 9011200 / 9175040 | docs/phase_f_report.md |
| 18 Sep 2026 | LLaMA-3.2-3B production holdout eval uses float16 and frees the tuned model before loading the base; TinyLlama production holdouts remain float32 as run | Dual float32 3B loads OOM on 24 GB during holdout; training already fit (~9 GB). Eval-only change; all prod run_meta stayed freeze-v1 and git_dirty_tracked=false | docs/phase_g_report.md; scripts/evaluate_instruction_holdout.py |
| 18 Sep 2026 | Phase G closed: tl 75/75 and l3 45/45 complete on Mac sync; no freeze-v2 retrain | grid_status acceptance; training code/configs unchanged from freeze-v1 | docs/phase_g_report.md; scripts/grid_status.py |
| 18 Sep 2026 | `--max-retries 5` used instead of 1 | host instability on M3 (GPU hang / CPU thrash); healers killed and resumed cells | results/launch/l3_shard*.jsonl; docs/phase_g_report.md |
| 18 Sep 2026 | `freeze-v2` tags the eval-only float16 change | post-freeze holdout OOM fix for LLaMA-3.2-3B; training provenance stays freeze-v1; analysis can name the eval code | scripts/evaluate_instruction_holdout.py sha256 201b79752f63ccc0...; docs/phase_g_report.md |
