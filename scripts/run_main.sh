#!/usr/bin/env bash
# Main study: all tasks in configs/main_tasks.txt, in batches; each batch runs every arm back to back,
# arm order rotated per batch (ABC, BCA, CAB, ...). Resumable: a batch/arm with a completed, valid
# run (phase=main, same batch, harbor_exit=0, no INVALID.md) is skipped.
# Usage (in WSL, detached): nohup setsid bash scripts/run_main.sh > ~/main.log 2>&1 < /dev/null & disown
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BATCH_SIZE="${BATCH_SIZE:-10}"
export PHASE=main N_CONCURRENT="${N_CONCURRENT:-2}"
mapfile -t TASKS < <(sed 's/\r$//; /^$/d' "$ROOT/configs/main_tasks.txt")
ARMS=(A B C)
n_batches=$(( (${#TASKS[@]} + BATCH_SIZE - 1) / BATCH_SIZE ))

done_already() {  # $1 batch, $2 arm
  for p in "$ROOT"/runs/*_"$2"/provenance.txt; do
    [ -f "$p" ] || continue
    d="$(dirname "$p")"
    grep -qx "phase=main" "$p" && grep -qx "batch=$1" "$p" && grep -qx "harbor_exit=0" "$p" && [ ! -f "$d/INVALID.md" ] && return 0
  done
  return 1
}

for ((b = 0; b < n_batches; b++)); do
  args=()
  for t in "${TASKS[@]:b*BATCH_SIZE:BATCH_SIZE}"; do args+=(-i "$t"); done
  for ((k = 0; k < 3; k++)); do
    arm="${ARMS[(b + k) % 3]}"
    if done_already "$b" "$arm"; then echo "=== batch $b arm $arm: already done, skipping"; continue; fi
    echo "=== batch $b/$((n_batches - 1)) arm $arm start $(date -u +%FT%TZ)"
    BATCH_ID="$b" bash "$ROOT/scripts/run_arm.sh" "$arm" "${args[@]}"
    echo "=== batch $b arm $arm exit $? $(date -u +%FT%TZ)"
  done
done
echo "=== main done $(date -u +%FT%TZ)"
