#!/usr/bin/env bash
# Launch one or more arms in sequence, detached from the calling shell (survives the caller being killed).
# Usage (in WSL): PHASE=<phase> [N_CONCURRENT=1] scripts/launch_detached.sh <task_list_file> <arm> [<arm>...]
# Log: ~/<phase>_<arms>.log ; check with: grep -E "^===|Mean|Run stored|Refusing" ~/<phase>_*.log
set -euo pipefail
: "${PHASE:?set PHASE}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TASKS="$1"; shift
ARMS=("$@")
LOG="$HOME/${PHASE}_$(IFS=; echo "${ARMS[*]}").log"
mapfile -t TASK_ARGS < <(sed 's/\r$//; /^$/d; s/^/-i\n/' "$TASKS")

nohup setsid bash -c '
  root=$1; shift; arms=$1; shift
  for a in $arms; do
    echo "=== arm $a $(date -u +%T)"
    bash "$root/scripts/run_arm.sh" "$a" "$@"
  done
  echo "=== done $(date -u +%T)"
' _ "$ROOT" "${ARMS[*]}" "${TASK_ARGS[@]}" > "$LOG" 2>&1 < /dev/null &
disown
sleep 5
echo "launched; log: $LOG"
head -2 "$LOG"
