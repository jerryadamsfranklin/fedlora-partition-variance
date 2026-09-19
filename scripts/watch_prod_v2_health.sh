#!/usr/bin/env bash
# Health check for Phase N prod_v2 boxes (tl_a05 then l3_ext).
# Exit 0 = all OK / done. Exit 1 = at least one box UNHEALTHY.
#
# Human-readable report (timestamp, status, progress) goes to stdout.
# Also suitable for: logs/prod_v2_health.log + logs/prod_v2_health_progress.txt
set -u

SSH_OPTS="-o BatchMode=yes -o ConnectTimeout=12 -o StrictHostKeyChecking=accept-new"
HANG_MINUTES="${HANG_MINUTES:-25}"
WARMUP_SECONDS="${WARMUP_SECONDS:-900}"

# name|host|port|shard
# All prod_v2 boxes synced/destroyed 2026-09-19:
#   M1 shard0 (tl 21 + l3 9), M2 shard1 (tl 21 + l3 9), M3 shard2 (tl 18 + l3 6).
MACHINES=(
)

REMOTE_CHECK=$(cat <<'EOS'
set +e
REPO=/workspace/fedlora-partition-variance
HANG_MINUTES=__HANG_MINUTES__
WARMUP_SECONDS=__WARMUP_SECONDS__
SHARD=__SHARD__

kv() { echo "$1=$2"; }

if ! test -d "$REPO"; then
  kv STATUS UNHEALTHY; kv REASON no_repo; exit 0
fi
cd "$REPO"

GPU=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1 | tr -d '\r')
if test "$GPU" != "NVIDIA GeForce RTX 4090"; then
  kv STATUS UNHEALTHY; kv REASON bad_gpu; kv GPU "$GPU"; exit 0
fi

IFS=',' read -r UTIL MEM_USED TEMP POWER <<EOF
$(nvidia-smi --query-gpu=utilization.gpu,memory.used,temperature.gpu,power.draw --format=csv,noheader,nounits 2>/dev/null | head -1)
EOF
UTIL=$(echo "${UTIL:-0}" | tr -d ' ' | cut -d. -f1)
MEM_USED=$(echo "${MEM_USED:-0}" | tr -d ' ' | cut -d. -f1)
TEMP=$(echo "${TEMP:-0}" | tr -d ' ' | cut -d. -f1)
POWER=$(echo "${POWER:-0}" | tr -d ' ' | cut -d. -f1)
UTIL=${UTIL:-0}; MEM_USED=${MEM_USED:-0}; TEMP=${TEMP:-0}; POWER=${POWER:-0}

TAG=$(git describe --tags --exact-match 2>/dev/null || echo unknown)
HAS_GRID=$(pgrep -f 'scripts/run_grid.py' >/dev/null 2>&1 && echo 1 || echo 0)
EXP_PID=$(pgrep -f 'scripts/run_experiment.py' | head -1)
HAS_EXP=0
EXP_ETIME_S=0
CURRENT_CELL=none
METHOD=none
DATA_SEED=none
RUN_SEED=none
if test -n "${EXP_PID:-}"; then
  HAS_EXP=1
  EXP_ETIME_S=$(ps -o etimes= -p "$EXP_PID" 2>/dev/null | tr -d ' ')
  EXP_ETIME_S=${EXP_ETIME_S:-0}
  ARGS=$(ps -o args= -p "$EXP_PID" 2>/dev/null || true)
  # .../vp_tl_flora_a05.yaml --data-seed 2002 --run-seed 7001
  cfg=$(echo "$ARGS" | sed -n 's/.*--config [^ ]*vp_\([^ ]*\)\.yaml.*/\1/p')
  DATA_SEED=$(echo "$ARGS" | sed -n 's/.*--data-seed \([0-9]*\).*/\1/p')
  RUN_SEED=$(echo "$ARGS" | sed -n 's/.*--run-seed \([0-9]*\).*/\1/p')
  # cfg like tl_flora_a05 or tl_ffa_lora_a05
  METHOD=$(echo "$cfg" | sed -E 's/^tl_//; s/^l3_//; s/_a05$//; s/_a01$//; s/_iid$//; s/_ext$//')
  if test -n "$cfg"; then
    CURRENT_CELL="${METHOD:-?}_d${DATA_SEED:-?}_r${RUN_SEED:-?}"
  fi
fi

COMPLETE=0
TOTAL=0
GRID=tl_a05
IN_PROGRESS=0
if test -x .venv/bin/python || test -x /venv/main/bin/python; then
  PY=.venv/bin/python
  test -x "$PY" || PY=/venv/main/bin/python
  prog=$($PY - <<PY
from pathlib import Path
from collections import Counter
try:
    from scripts.run_grid import load_grid, enumerate_cells, shard_cells, classify_cell
except Exception:
    print("0 0 none 0")
    raise SystemExit
shard = int("$SHARD")
chosen = None
for name in ("tl_a05", "l3_ext"):
    p = Path(f"grids/{name}.yaml")
    if not p.is_file():
        continue
    cells = shard_cells(enumerate_cells(load_grid(p)), shard, 3)
    c = Counter(classify_cell(x) for x in cells)
    done = c.get("complete", 0)
    busy = c.get("resumable", 0) + c.get("orphan", 0) + c.get("needs_holdout", 0)
    chosen = (done, len(cells), name, busy)
    if done < len(cells):
        break
if chosen is None:
    print("0 0 none 0")
else:
    print(f"{chosen[0]} {chosen[1]} {chosen[2]} {chosen[3]}")
PY
)
  COMPLETE=$(echo "$prog" | awk '{print $1}')
  TOTAL=$(echo "$prog" | awk '{print $2}')
  GRID=$(echo "$prog" | awk '{print $3}')
  IN_PROGRESS=$(echo "$prog" | awk '{print $4}')
fi
COMPLETE=${COMPLETE:-0}; TOTAL=${TOTAL:-0}; GRID=${GRID:-tl_a05}; IN_PROGRESS=${IN_PROGRESS:-0}

# Newest file age in the *active* run dir (not global latest.pt — that false-killed L3 flora)
CKPT_AGE=""
if test "$HAS_EXP" = "1"; then
  cfg=$(echo "$ARGS" | sed -n 's/.*--config [^ ]*\/\(vp_[^ /]*\)\.yaml.*/\1/p')
  if test -n "$cfg" && test -n "${DATA_SEED:-}" && test -n "${RUN_SEED:-}" && test "$DATA_SEED" != "none"; then
    RUN_DIR=$(find "results/raw/${cfg}" -type d -path "*/seed_${DATA_SEED}_run${RUN_SEED}/prod_v2/*" 2>/dev/null | sort | tail -1)
    if test -n "$RUN_DIR"; then
      NEWEST=$(find "$RUN_DIR" -type f -printf '%T@\n' 2>/dev/null | sort -n | tail -1)
      if test -n "${NEWEST:-}"; then
        NOW=$(date +%s)
        CKPT_AGE=$(python3 -c "print(int($NOW - float('$NEWEST')))" 2>/dev/null || echo "")
      fi
    fi
  fi
fi

SHARD_DONE=0
if test "$TOTAL" -gt 0 && test "$COMPLETE" -ge "$TOTAL"; then
  SHARD_DONE=1
fi

REASON=ok
STATUS=OK
if test "$SHARD_DONE" = "1" && test "$HAS_GRID" = "0"; then
  STATUS=DONE; REASON=shard_complete
elif test "$HAS_GRID" = "0"; then
  STATUS=UNHEALTHY; REASON=no_run_grid
elif test "$HAS_EXP" = "0"; then
  if test -n "${CKPT_AGE:-}" && test "$CKPT_AGE" -lt 900; then
    STATUS=OK; REASON=between_cells
  else
    STATUS=UNHEALTHY; REASON=no_run_experiment
  fi
else
  HANG_S=$((HANG_MINUTES * 60))
  if test "$EXP_ETIME_S" -gt "$WARMUP_SECONDS"; then
    IDLE=0
    test "$UTIL" -lt 5 && test "$POWER" -lt 80 && IDLE=1
    STALE_CKPT=0
    test -z "${CKPT_AGE:-}" || test "$CKPT_AGE" -gt "$HANG_S" && STALE_CKPT=1
    if test "$IDLE" = "1" && test "$STALE_CKPT" = "1"; then
      STATUS=UNHEALTHY; REASON=train_hang
    fi
  fi
fi

# One parseable line for the Mac aggregator
echo "STATUS=$STATUS REASON=$REASON TAG=$TAG GRID=$GRID SHARD=$SHARD COMPLETE=$COMPLETE TOTAL=$TOTAL IN_PROGRESS=$IN_PROGRESS CURRENT_CELL=$CURRENT_CELL GPU_UTIL=${UTIL} MEM=${MEM_USED} POWER=${POWER} TEMP=${TEMP} HAS_GRID=$HAS_GRID HAS_EXP=$HAS_EXP EXP_ETIME_S=$EXP_ETIME_S CKPT_AGE_S=${CKPT_AGE:-na}"
EOS
)

bad=0
# Eastern Time (EST/EDT via America/New_York)
export TZ="${TZ:-America/New_York}"
ts=$(date +"%Y-%m-%d %H:%M:%S %Z")
ts_iso=$(date +%Y-%m-%dT%H:%M:%S%z)

declare -a LINES=()
declare -a PROG_BITS=()
total_done=0
total_cells=0
active_grid="tl_a05"

for entry in "${MACHINES[@]}"; do
  IFS='|' read -r name host port shard <<<"$entry"
  script=${REMOTE_CHECK//__HANG_MINUTES__/$HANG_MINUTES}
  script=${script//__WARMUP_SECONDS__/$WARMUP_SECONDS}
  script=${script//__SHARD__/$shard}

  out=$(ssh $SSH_OPTS -p "$port" "root@$host" "bash -s" <<<"$script" 2>/dev/null) || out=""
  line=$(printf '%s\n' "$out" | awk 'NF{l=$0} END{print l}')

  if test -z "$line"; then
    STATUS=UNHEALTHY; REASON=ssh_fail
    COMPLETE=?; TOTAL=?; GRID=?; CURRENT_CELL=none
    GPU_UTIL=?; MEM=?; POWER=?; TEMP=?; EXP_ETIME_S=0; IN_PROGRESS=0
    bad=1
  else
    # shellcheck disable=SC2086
    eval "$(echo "$line" | tr ' ' '\n' | grep -E '^[A-Z0-9_]+=')"
    STATUS=${STATUS:-UNKNOWN}
    REASON=${REASON:-unknown}
    COMPLETE=${COMPLETE:-?}
    TOTAL=${TOTAL:-?}
    GRID=${GRID:-?}
    CURRENT_CELL=${CURRENT_CELL:-none}
    GPU_UTIL=${GPU_UTIL:-?}
    MEM=${MEM:-?}
    POWER=${POWER:-?}
    TEMP=${TEMP:-?}
    EXP_ETIME_S=${EXP_ETIME_S:-0}
    IN_PROGRESS=${IN_PROGRESS:-0}
    case "$STATUS" in UNHEALTHY) bad=1 ;; esac
  fi

  if [[ "$COMPLETE" =~ ^[0-9]+$ && "$TOTAL" =~ ^[0-9]+$ ]]; then
    total_done=$((total_done + COMPLETE))
    total_cells=$((total_cells + TOTAL))
    PROG_BITS+=("${name} ${COMPLETE}/${TOTAL}")
    active_grid="$GRID"
  else
    PROG_BITS+=("${name} ?/?")
  fi

  et_m=$((EXP_ETIME_S / 60))
  # flora_d2002_r7001 -> flora d2002/r7001
  cell_pretty=$(echo "$CURRENT_CELL" | sed -E 's/_d([0-9]+)_r([0-9]+)$/ d\1\/r\2/')
  cell_disp="$cell_pretty"
  if test "$CURRENT_CELL" != "none" && test "$EXP_ETIME_S" -gt 0 2>/dev/null; then
    cell_disp="$cell_pretty (${et_m}m)"
  elif test "$REASON" = "between_cells"; then
    cell_disp="(between cells / holdout)"
  elif test "$STATUS" = "DONE"; then
    cell_disp="(shard complete)"
  fi

  printf -v row "%-3s shard%-1s  %5s  %-9s  GPU %3s%%  %5sMiB  %4sW  %s" \
    "$name" "$shard" "${COMPLETE}/${TOTAL}" "$STATUS" "$GPU_UTIL" "$MEM" "$POWER" "$cell_disp"
  LINES+=("$row")
  # machine-parseable echo kept for grep/tools
  LINES+=("  raw: MACHINE=$name HOST=$host:$port STATUS=$STATUS REASON=$REASON GRID=$GRID PROGRESS=${COMPLETE}/${TOTAL} CELL=$CURRENT_CELL")
done

summary=OK
test "$bad" -eq 0 || summary=UNHEALTHY
prog_join=$(printf '%s | ' "${PROG_BITS[@]}")
prog_join=${prog_join%' | '}

{
  echo "========== $ts =========="
  echo "SUMMARY: $summary"
  echo "PROGRESS: ${active_grid} ${total_done}/${total_cells} cells  (${prog_join})"
  echo ""
  for row in "${LINES[@]}"; do
    # print human rows; skip indent-only? print all
    case "$row" in
      "  raw:"*) ;;
      *) echo "$row" ;;
    esac
  done
  echo "=========================================="
  echo "WATCH_TS=$ts_iso SUMMARY=$summary PROGRESS=${active_grid}:${total_done}/${total_cells}"
  for row in "${LINES[@]}"; do
    case "$row" in
      "  raw:"*) echo "${row#  raw: }" ;;
    esac
  done
} 

if test "$bad" -eq 0; then
  exit 0
fi
exit 1
