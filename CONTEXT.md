# CONTEXT

## Project
Research prototype: reduce LLM tool-calling hallucination by verifying each (tool call + result) with a fast "System One" model (TypeSafe Jev) and feeding P(correct) back to the agent.

## Status (2026-10-03)
- Research phase done. No code yet.
- `.research/01-tool-calling-hallucination/`: taxonomy, benchmarks, mitigations, prior work, gaps.
- `.research/02-system-one-jev/`: Jev architecture, claims vs. evidence, access, fit analysis.
- `.research/00-SYNTHESIS.md`: assessment, reframing, architecture, evaluation plan.

## Key decisions / findings
- "Jev doesn't hallucinate" applies only to output form. Treat Jev as one verifier arm, not a guarantee.
- Close prior work exists (Reinforced Agent, Latent Critic, ToolCritic, ToolRM, IDK Filter). The contribution must be framed comparatively (per-class detection, feedback-format ablation, calibration-in-loop, result-side checks).
- All subagent-sourced quotes and numbers are unverified (WebFetch summaries) and must be checked before citing.

## Experiment design (2026-10-03, revised)
- Claim: a System One critic is faster/cheaper with fewer critic errors than a small-LLM critic.
- Harness: OpenCode. Agent model: `gpt-6-luna` via CallMissed.
- Arms: A no critic | B small-LLM critic | C Cloudflare Clef (`@cf/cloudflare/clef`, Jev-API-compatible; see `.research/04-cloudflare-clef/`).
- Haiku is NOT available as a text LLM on CallMissed (voice-only); user chose CallMissed-only critics.
- Benchmark: Terminal-Bench 2.0 (89 tasks) via Harbor's built-in opencode agent (`.research/03-benchmark-selection/`). Needs Docker + WSL2.
- Judge: Opus subagent, blinded to arm. Validate against a human-labelled sample.

- Arm B critic = `gpt-5-mini` (CallMissed, OpenAI-compatible base `https://api.callmissed.com/v1`). gpt-4o + clef-flash evaluated offline via replay.
- Full plan: `.research/05-experiment-plan.md` (RQs, arms, architecture, files, judging, stats, phases).
- Injection point: OpenCode plugin hook `tool.execute.after` (verified; mutated output is what OpenCode records as the tool result).

## Phase 0 (done 2026-10-03)
- Harbor 0.23.0 in WSL; TB2 (89 tasks: 4 easy/55 medium/30 hard) downloaded to WSL ~/datasets/terminal-bench.
- Runner: `wsl bash scripts/run_arm.sh <A|B|C> [harbor args]` → `runs/<ts>_<arm>/` with provenance + redaction + MANIFEST.sha256.
- Plugin `critic/critic.js` verified: verdict appears in recorded tool output; critic.jsonl per trial at `.../agent/critic.jsonl`.
- Smoke runs on fix-git: A, B, C all reward 1.0. Two invalid runs kept with INVALID.md.
- WSL /mnt/e cwd glitch → runner cds to $HOME.

## Pilots (2026-10-03/04)
- Pilot 1 → design fixes (grounded_call question, alert-only, errored-call logging, setup retries). Report: `.research/06-pilot-report.md`.
- Pilot 2 judged (Opus, 1043 calls): strict hallucinations/task A 6.8, B 1.2, C 2.0 (loop task dominates; without it 2.5/1.2/1.5). Tables: `results/pilot2/summary.md`.
- CallMissed limit: 60 req/min per key → one key per role.

## Status: plan FROZEN v1.0 (git tag v1.0)
## Next
User adds `CALLMISSED_CRITIC_API_KEY` and `CALLMISSED_REPLAY_API_KEY` to `.env` → launch `scripts/run_main.sh` detached in WSL (2 concurrent). Then replay, judge (Sonnet), analyze, human κ sample.
