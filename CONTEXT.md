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
- Haiku is NOT available as a text LLM on CallMissed (voice-only). Arm B model is pending user choice.
- Benchmark: Terminal-Bench 2.0 (89 tasks) via Harbor's built-in opencode agent (`.research/03-benchmark-selection/`). Needs Docker + WSL2.
- Judge: Opus subagent, blinded to arm. Validate against a human-labelled sample.

- Arm B critic = `gpt-5-mini` (CallMissed, OpenAI-compatible base `https://api.callmissed.com/v1`). gpt-4o + clef-flash evaluated offline via replay.
- Full plan: `.research/05-experiment-plan.md` (RQs, arms, architecture, files, judging, stats, phases).
- Injection point: OpenCode plugin hook `tool.execute.after` (verified in plugin types). Whether output mutation reaches the model is unverified.

## Phase 0 (done 2026-10-03)
- Harbor 0.23.0 in WSL; TB2 (89 tasks: 4 easy/55 medium/30 hard) downloaded to WSL ~/datasets/terminal-bench.
- Runner: `wsl bash scripts/run_arm.sh <A|B|C> [harbor args]` → `runs/<ts>_<arm>/` with provenance + redaction + MANIFEST.sha256.
- Plugin `critic/critic.js` verified: verdict appears in recorded tool output; critic.jsonl per trial at `.../agent/critic.jsonl`.
- Smoke runs on fix-git: A, B, C all reward 1.0. Two invalid runs kept with INVALID.md.
- WSL /mnt/e cwd glitch → runner cds to $HOME.

## Next
Phase 1 remainder: scripts/collect.py, to_markdown.py. Then Phase 2 pilot (5 tasks × 3 arms).
