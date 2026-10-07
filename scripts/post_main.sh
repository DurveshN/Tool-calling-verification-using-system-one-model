#!/usr/bin/env bash
# Launcher used on the Azure VM (2026-10-06) for post-main judge + replay jobs. Kept for reproducibility.
# Note: loads .env raw; .env must have LF line endings (see judge_llm CRLF fix).
# Post-main analysis jobs (detached): judge on the agent key, replay on the replay key, in parallel.
cd ~/prototype
set -a; . ./.env; set +a
( python3 scripts/judge_llm.py --phase main --labels-dir labels_gpt6luna --workers 4 --rpm 40 > ~/judge_main.log 2>&1; echo "=== judge exit $?" >> ~/judge_main.log ) &
( node scripts/replay.mjs --phase main --critics gpt-5-mini,clef,clef-flash --concurrency 6 --llm-rpm 50 > ~/replay_main.log 2>&1
  node scripts/replay.mjs --phase main --critics gpt-4o --sample 3000 --seed 20261006 --concurrency 4 --llm-rpm 50 >> ~/replay_main.log 2>&1
  echo "=== replay exit $?" >> ~/replay_main.log ) &
wait
echo "=== post_main done $(date -u +%FT%TZ)" >> ~/judge_main.log
