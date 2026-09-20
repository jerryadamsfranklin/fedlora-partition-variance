#!/usr/bin/env bash
# N8 10-minute health loop: log status, restart hung grids, advance TL→L3.
# stdout is the watcher log (do not also tee to the same file — that doubles lines).
set +e
set -u
REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"
export TZ="${TZ:-America/New_York}"
SSH_OPTS="-o BatchMode=yes -o ConnectTimeout=15 -o StrictHostKeyChecking=accept-new -o LogLevel=ERROR -o UserKnownHostsFile=/dev/null"
LOG_DIR="$REPO/logs"
mkdir -p "$LOG_DIR"
# Single place for status (same as yesterday): logs/prod_v2_health.log
HEALTH_LOG="$LOG_DIR/prod_v2_health.log"
PROGRESS_FILE="$LOG_DIR/prod_v2_health_progress.txt"
# Keep latest as a mirror of the last block for quick open
LATEST="$LOG_DIR/prod_v2_health_latest.txt"

BOXES=(
  "M0|60.250.87.179|59442|0|tl_a05_n8_m0|l3_ext_n8_m0"
)

restart_grid() {
  local port=$1 host=$2 session=$3 grid=$4
  ssh $SSH_OPTS -p "$port" "root@$host" "bash -s" <<EOF
set +e
cd /workspace/fedlora-partition-variance || exit 1
test -f grids/${grid}.yaml || exit 1
if ! test -x .venv/bin/python; then
  echo "ERROR: missing .venv/bin/python (refusing /venv/main — no datasets)"; exit 1
fi
export HF_TOKEN=\$(tr -d '\n' < /workspace/.hf_home/token 2>/dev/null)
test -n "\$HF_TOKEN" || export HF_TOKEN=\$(tr -d '\n' < ~/.cache/huggingface/token 2>/dev/null)
mkdir -p logs
tmux kill-session -t ${session} 2>/dev/null
tmux new-session -d -s ${session} "bash -lc 'cd /workspace/fedlora-partition-variance && source .venv/bin/activate && export PATH=/workspace/fedlora-partition-variance/.venv/bin:\$PATH && export HF_TOKEN=\$(tr -d \\\"\\\\n\\\" < /workspace/.hf_home/token 2>/dev/null) && python -c \"import datasets\" && python scripts/run_grid.py --grid grids/${grid}.yaml --shard 0 --num-shards 1 --device cuda --production --workers 1 --max-retries 2 2>&1 | tee logs/n8_${session}.log; echo EXIT=\$? | tee -a logs/n8_${session}.log'"
echo RESTARTED_${session}_on_${grid}
EOF
}

heal_box() {
  local name=$1 host=$2 port=$3 tl=$4 l3=$5 reason=$6 grid=$7
  echo "[heal] $name reason=$reason grid=$grid"
  case "$reason" in
    no_run_grid|no_run_experiment|train_hang|ssh_fail)
      local which
      which=$(ssh $SSH_OPTS -p "$port" "root@$host" "bash -s" <<EOF
cd /workspace/fedlora-partition-variance 2>/dev/null || { echo none; exit 0; }
PY=.venv/bin/python; test -x \$PY || PY=/venv/main/bin/python
\$PY - <<'PY'
from pathlib import Path
from collections import Counter
from scripts.run_grid import load_grid, enumerate_cells, classify_cell
def done(name):
    p=Path(f"grids/{name}.yaml")
    if not p.is_file(): return False
    cells=enumerate_cells(load_grid(p))
    c=Counter(classify_cell(x) for x in cells)
    return c.get("complete",0)>=len(cells) and len(cells)>0
tl_done=done("$tl")
l3_done=done("$l3")
if not tl_done: print("tl")
elif not l3_done: print("l3")
else: print("all_done")
PY
EOF
)
      which=$(echo "$which" | tail -1 | tr -d '\r')
      if test "$which" = "tl"; then
        restart_grid "$port" "$host" "n8_tl_${name}" "$tl" || true
      elif test "$which" = "l3"; then
        restart_grid "$port" "$host" "n8_l3_${name}" "$l3" || true
      else
        echo "[heal] $name $which — no restart"
      fi
      ;;
  esac
}

cycle=0
while true; do
  cycle=$((cycle + 1))
  ts=$(date +"%Y-%m-%d %H:%M:%S %Z")
  echo ""
  echo "===== N8 watch cycle $cycle @ $ts ====="

  report=$("$REPO/scripts/ops/watch_prod_v2_health.sh" 2>&1) || true
  # Human block only (drop MACHINE= parse lines) → stdout (= prod_v2_health.log via daemon)
  block=$(printf '%s\n' "$report" | awk '/^MACHINE=/{next} {print}')
  echo ""
  printf '%s\n' "$block"
  printf '%s\n' "$block" > "$LATEST"
  echo "$report" | awk '/^PROGRESS:/{print; exit}' > "$PROGRESS_FILE"

  while IFS= read -r raw; do
    case "$raw" in
      MACHINE=*)
        # Parse fields without eval (eval PROGRESS=5/12 overwrote $PROGRESS_FILE path)
        name=$(echo "$raw" | sed -n 's/.*MACHINE=\([^ ]*\).*/\1/p')
        hostport=$(echo "$raw" | sed -n 's/.*HOST=\([^ ]*\).*/\1/p')
        status=$(echo "$raw" | sed -n 's/.*STATUS=\([^ ]*\).*/\1/p')
        reason=$(echo "$raw" | sed -n 's/.*REASON=\([^ ]*\).*/\1/p')
        grid=$(echo "$raw" | sed -n 's/.*GRID=\([^ ]*\).*/\1/p')
        host=${hostport%%:*}
        port=${hostport##*:}
        tl=""; l3=""
        for b in "${BOXES[@]}"; do
          IFS='|' read -r bn bh bp bi btl bl3 <<<"$b"
          if test "$bn" = "$name"; then tl=$btl; l3=$bl3; host=$bh; port=$bp; break; fi
        done
        if test "$status" = "UNHEALTHY" && test -n "$tl"; then
          echo "[heal] triggering $name reason=$reason"
          heal_box "$name" "$host" "$port" "$tl" "$l3" "$reason" "$grid"
        fi
        ;;
    esac
  done <<<"$report"

  for b in "${BOXES[@]}"; do
    IFS='|' read -r name host port idx tl l3 <<<"$b"
    adv=$(ssh $SSH_OPTS -p "$port" "root@$host" "bash -s" <<EOF
cd /workspace/fedlora-partition-variance 2>/dev/null || { echo skip; exit 0; }
PY=.venv/bin/python; test -x \$PY || PY=/venv/main/bin/python
\$PY - <<'PY'
from pathlib import Path
from collections import Counter
from scripts.run_grid import load_grid, enumerate_cells, classify_cell
def status(name):
    p=Path(f"grids/{name}.yaml")
    if not p.is_file(): return "missing"
    cells=enumerate_cells(load_grid(p))
    c=Counter(classify_cell(x) for x in cells)
    if c.get("complete",0)>=len(cells): return "done"
    return "busy"
print("tl="+status("$tl"))
print("l3="+status("$l3"))
PY
pgrep -f 'scripts/run_grid.py' >/dev/null && echo grid=1 || echo grid=0
EOF
) || adv="skip"
    if echo "$adv" | grep -q 'tl=done' && echo "$adv" | grep -qE 'l3=busy|l3=missing' && echo "$adv" | grep -q 'grid=0'; then
      if ! echo "$adv" | grep -q 'l3=done'; then
        echo "[advance] $name TL complete, launching L3"
        restart_grid "$port" "$host" "n8_l3_${name}" "$l3" || true
      fi
    fi
  done

  echo "Next check in 10 minutes…"
  sleep 600
done
