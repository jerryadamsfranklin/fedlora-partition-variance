# STATUS

Last updated: 18 Sep 2026

Replace this file in the Claude Project whenever the state changes. Keep only one copy.

## Current phase

Phase N on phase-n. N5a to N5d complete (pre-launch). Ready for Jerry to rent three RTX 4090s and launch per docs/PHASE_N_RUNBOOK.md. Do not destroy gate until 60/60 + 24/24 + 84 adapters.

## Standing rule

Every change request goes into docs/IMPLEMENTATION_PLAN.md as a numbered phase with acceptance checks, and is executed from the plan. No ad-hoc execution.

## Venue decision

- Target: IEEE Access; IJACSA November/December fallback; never dual-submit

## Contribution naming

The Partition-Draw Reporting Protocol (no acronym). Three numbered steps in abstract and discussion.

## Done

- N1 to N4: configs, grids, I8-I10, V12, freeze-v3
- N5 runbook written
- N5a: freeze_tag on all four grids; production_guard requires matching tag; vast_setup honors FREEZE_TAG
- N5b: partition preview appended (alpha 0.5 seeds 2001-2010, min active 10; alpha 0.1 seeds 2007-2010, min active 9); both PASS
- N5c: V7 cross-tag base_loss pooling vs 2.120666 (tl) and 2.168946 (l3)
- N5d: DECISIONS + PROVENANCE cite ed80372 for float32 spot-check CLI
- O2b: Gap paragraph narrowed; FlowerTune setup sentence; five refs verified (refs.bib 14/~25); DECISIONS row

## Next

1. Jerry: regenerate tokens; rent 3x RTX 4090 (exact name gate); follow PHASE_N_RUNBOOK
2. Cursor: Mac sync every 2-3 hours after launch starts; first-cell check (freeze-v3, gpu_name, base_loss 2.120666)
3. N6 already logged in DECISIONS; N7 after runs

## Open items

- Attorney / Cabells / ORCID / Zenodo as before
- Local tooling: use .venv/bin/python

## Run progress

| Grid | Complete | Total | Tag |
|---|---|---|---|
| tl | 75 | 75 | prod_v1 |
| l3 | 45 | 45 | prod_v1 |
| tl_a05 | 0 | 60 | prod_v2 |
| l3_ext | 0 | 24 | prod_v2 |
