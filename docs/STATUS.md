# STATUS

Last updated: 19 Sep 2026

Replace this file in the Claude Project whenever the state changes. Keep only one copy.

## Current phase

Phase N8 in progress: 54 stack-drifted cells quarantined; **default 3-shard launch blocked** (100% imbalance). Waiting on Jerry to rent M1+M3. M2 PASS (torch 2.2.0+cu121, RTX 4090). Phase O1–O4 may proceed on Mac; no results text until N8-6.

## Blocking before launch

1. Rent 2 more RTX 4090s; run N8-0 gate on each (destroy on fail)
2. Launch with **rebalanced grids** `grids/{tl_a05,l3_ext}_n8_m{i}.yaml` (spread 11%), NOT default `--num-shards 3`
3. Keep M2; assign it machine index from `results/launch/n8_rebalance_assignment.json`

## N8-2 balance (default shards — FAIL)

| Shard | tl fresh | l3 fresh | Hours |
|---|---:|---:|---:|
| 0 | 21 | 9 | 22.25 |
| 1 (M2 clean) | 0 | 0 | 0.00 |
| 2 | 18 | 6 | 16.90 |

Rebalance: ~13.8 / 12.3 / 13.1 h (11% spread). See `analysis/n8_balance_check.txt`.

## Quarantine

- `results/quarantine_stackdrift/` holds 54 raw runs + holdouts
- `grid_status`: tl_a05 complete=21 fresh=39; l3_ext complete=9 fresh=15

## Next

1. Jerry rents M1+M3 → N8-0 → staggered launch on filtered grids
2. Sync / V2-cross-tag / I8–I10 after retrain (N8-5–6)
3. O1–O4 manuscript mechanics now

## Venue

- IEEE Access primary; IJACSA fallback; never both at once
