#!/usr/bin/env bash
# Run one experiment arm on Terminal-Bench 2.0 via Harbor + OpenCode.
# Usage: scripts/run_arm.sh <arm: A|B|C> [extra harbor args, e.g. -l 1 -i <task>]
# Each invocation writes to a NEW directory runs/<UTC timestamp>_<arm>/ (never overwritten).
set -euo pipefail

ARM="${1:?arm required (A|B|C)}"; shift
case "$ARM" in A) CRITIC_MODE=none ;; B) CRITIC_MODE=llm ;; C) CRITIC_MODE=clef ;; *) echo "bad arm" >&2; exit 2 ;; esac

PHASE="${PHASE:?set PHASE=smoke|pilot|main}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="$HOME/.local/bin:$PATH"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
set -a; source <(sed 's/\r$//' "$ROOT/.env"); set +a

AGENT_MODEL="${AGENT_MODEL:-gpt-6-luna}"
DATASET_DIR="${DATASET_DIR:-$HOME/datasets/terminal-bench}"  # from: harbor datasets download terminal-bench@2.0
OPENCODE_VERSION="${OPENCODE_VERSION:-1.18.34}"  # pinned: version used in Phase 0 smoke runs

if [ -n "$(git -C "$ROOT" status --porcelain)" ] && [ "${ALLOW_DIRTY:-0}" != 1 ]; then
  echo "Refusing to run: uncommitted changes (commit first, or ALLOW_DIRTY=1 for debugging)." >&2; exit 3
fi

RUN_DIR="$ROOT/runs/$(date -u +%Y%m%dT%H%M%SZ)_${ARM}"
mkdir -p "$RUN_DIR"

OPENCODE_CONFIG=$(cat <<JSON
{"provider":{"callmissed":{"npm":"@ai-sdk/openai-compatible","name":"CallMissed",
 "options":{"baseURL":"https://api.callmissed.com/v1","apiKey":"{env:CALLMISSED_API_KEY}"},
 "models":{"$AGENT_MODEL":{}}}}}
JSON
)

# Provenance (no secrets).
{
  echo "phase=$PHASE"; echo "arm=$ARM"; echo "critic_mode=$CRITIC_MODE"; echo "agent_model=callmissed/$AGENT_MODEL"
  echo "dataset_dir=$DATASET_DIR"
  echo "dataset_sha256=$(cd "$DATASET_DIR/.." && find "$(basename "$DATASET_DIR")" -type f | sort | xargs -d '\n' sha256sum | sha256sum | cut -d' ' -f1)"
  echo "opencode_version=${OPENCODE_VERSION:-latest}"
  echo "harbor_version=$(harbor --version 2>/dev/null)"
  echo "git_commit=$(git -C "$ROOT" rev-parse HEAD 2>/dev/null)"
  echo "git_dirty=$(git -C "$ROOT" status --porcelain | wc -l)"
  echo "started_utc=$(date -u +%FT%TZ)"
  echo "extra_args=$*"
} > "$RUN_DIR/provenance.txt"

VERSION_ARGS=(); [ -n "$OPENCODE_VERSION" ] && VERSION_ARGS=(--ak "version=$OPENCODE_VERSION")

set +e
cd "$HOME"  # harbor reads Path.cwd(); /mnt drvfs cwd lookups can fail intermittently
harbor run -y \
  -p "$DATASET_DIR" \
  -a harbor_ext.opencode_critic:OpenCodeCritic -m "callmissed/$AGENT_MODEL" \
  --ak "opencode_config=$OPENCODE_CONFIG" "${VERSION_ARGS[@]}" \
  --ae "CALLMISSED_API_KEY=$CALLMISSED_API_KEY" \
  --ae "CF_ACCOUNT_ID=$CF_ACCOUNT_ID" --ae "CF_API_TOKEN=$CF_API_TOKEN" \
  --ae "CRITIC_MODE=$CRITIC_MODE" \
  --allow-agent-host api.callmissed.com --allow-agent-host api.cloudflare.com \
  -o "$RUN_DIR/jobs" -n "${N_CONCURRENT:-1}" \
  --agent-setup-timeout-multiplier 3 \
  --max-retries 2 --retry-include AgentSetupTimeoutError \
  "$@" 2>&1 | tee "$RUN_DIR/harbor.log"
STATUS=${PIPESTATUS[0]}
set -e

echo "finished_utc=$(date -u +%FT%TZ)" >> "$RUN_DIR/provenance.txt"
echo "harbor_exit=$STATUS" >> "$RUN_DIR/provenance.txt"

# Redact secrets that tools may have echoed into logs/configs, then freeze evidence.
python3 "$ROOT/scripts/redact_and_manifest.py" "$RUN_DIR"
echo "Run stored at: $RUN_DIR"
exit "$STATUS"
