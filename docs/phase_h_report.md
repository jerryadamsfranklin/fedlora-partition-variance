# Phase H report

Date: 18 Sep 2026. Branch `phase-h`. Verifier: `scripts/verify_varpart.py` exits 0 on V1 to V8 and V11 (V9 deferred to Phase L).

## Float16 holdout decision (LLaMA-3.2-3B)

Sequential float32 spot-check on three L3 cells spanning the production `tuned_loss` range (lowest, median, highest). Artifacts: `analysis/holdout_l3_fp32_spotcheck.csv` and `results/downstream_instruction_fp32_spotcheck/` (JSON only; prod holdouts untouched).

| cell | tuned_loss fp16 | tuned_loss fp32 | abs diff | base_loss fp32 |
|---|---:|---:|---:|---:|
| lowest (`fedit` iid 2001/7003) | 1.7898843463 | 1.7898428486 | 4.15e-5 | 2.1689717057 |
| median (`flora` a01 2003/7002) | 1.8058933683 | 1.8058813760 | 1.20e-5 | 2.1689717057 |
| highest (`ffa_lora` a01 2003/7002) | 1.8391503169 | 1.8391267481 | 2.36e-5 | 2.1689717057 |

Max `|fp16-fp32|` on tuned_loss is 4.1e-5, about 250x below the 0.01 effect scale. Keep float16 for L3 production holdouts; no full re-eval. TinyLlama holdouts remain float32.

## Eval provenance

- Production eval script sha256: `201b79752f63ccc06aab8c612c8fb450e9c7f18ee04fff2a31aaf6808458df30`
- `freeze-v2` tags commit `4f9fcf8` (eval-only float16 + sequential free); training provenance stays `freeze-v1`
- TinyLlama recorded `eval_dtype=torch.float32`; the float16 CUDA default did not alter TL results

## V10 resume and retry census (informational)

| grid | method | cells | attempt>1 | resumed | failed_atts |
|---|---|---:|---:|---:|---:|
| tl | fedit | 25 | 0 | 0 | 0 |
| tl | ffa_lora | 25 | 0 | 0 | 0 |
| tl | flora | 25 | 2 | 1 | 7 |
| l3 | fedit | 15 | 7 | 0 | 73 |
| l3 | ffa_lora | 15 | 7 | 0 | 72 |
| l3 | flora | 15 | 8 | 2 | 92 |

The LLaMA failed-attempt counts are eval OOMs before the float16 fix; they left no partial training. The material exposure is the three checkpoint resumes, all on FLoRA.

## Resume-cell range check

Group key: `(grid, het, data_seed, method)`. Held-out loss is production `tuned_loss`.

| cell_id | heldout_loss | group min | group max | n | inside range |
|---|---:|---:|---:|---:|---|
| `tl_flora_a01_d2004_r7001` | 1.6947523958 | 1.6946910218 | 1.6947523958 | 2 | yes |
| `l3_flora_iid_d2001_r7003` | 1.8045553556 | 1.8031979222 | 1.8046552587 | 3 | yes |
| `l3_flora_a01_d2004_r7002` | 1.8035178138 | 1.8034098083 | 1.8035178138 | 2 | yes |

All three resumed held-out losses fall inside their cell-group range. The two a01 pairs differ from their sibling seed by less than 1e-4; the iid resume sits between the other two seeds.

## Adapter note

As of 18 Sep 2026, Mac and M3 each hold 25 of 120 `final_adapter_state.pt` files (gitignored; M1/M2 destroyed earlier). Phase I uses holdout JSONs and run metadata only. Do not destroy M3 until adapters are recovered or explicitly waived.
