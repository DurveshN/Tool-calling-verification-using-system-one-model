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

## Status: plan FROZEN v1.0 (git tag v1.0); MAIN RUN STARTED 2026-10-04 14:24Z on Azure
- GitHub: https://github.com/DurveshN/Tool-calling-verification-using-system-one-model (public)
- Azure: RG `research-paper` (centralindia), VM `research-vm` Standard_DC8as_v5 (8 vCPU/32 GB, confidential Ubuntu 24.04, 512 GB), $0.222/h. IP 20.204.118.246, user `researcher`, key `~/.ssh/research_vm`, SSH allowed only from 106.213.84.16.
- VM provisioned by `scripts/setup_vm.sh`; dataset hash verified identical; latency to CallMissed and Cloudflare ~28 ms.
- Kimi considered and rejected by user (keep GPT models).
- VM smoke test (phase=smoke_vm, 2 tasks × 3 arms) passed; per-role key fingerprints: agent 7657643f, critic 466458a0.
- Main: `run_main.sh` detached on VM, log `~/main.log`; progress: `ssh -i ~/.ssh/research_vm researcher@20.204.118.246 'bash ~/status.sh'`.
- Do NOT pull new commits on the VM during the main run.

## Main run DONE 2026-10-05 22:51Z
- Pass (secondary outcome): A 22/89, B 31/89, C 31/89. Critic errors total 3. Tool calls: A 8466, B 7469, C 6086 (critic-logged).
- Evidence pulled to local `runs/` via resumable rsync (WSL `~/pull_runs.sh`). Note: Windows Python can't open >260-char snapshot paths; verify manifests from WSL.
- Deviations (plan §14): judge = gpt-6-luna via `scripts/judge_llm.py` (labels dir `labels_gpt6luna`), all 89 tasks; gpt-4o replay on a seeded 3,000-call sample.
- Judge validity: gpt-6-luna vs Opus on pilot 2: strict κ 0.685, broad κ 0.737. gpt-6-luna is more lenient (36 vs 50 strict positives).
- 2026-10-06: on VM `~/post_main.sh` running judge (`~/judge_main.log`) + replay (`~/replay_main.log`); main = 21,881 calls, 261 packets / 346 parts.

## Post-main (2026-10-07)
- Jobs finished on VM; all outputs pulled locally (`data/judge/main`, `data/replay.jsonl` main rows, `runs/_vm_logs/`). VM no longer needed.
- CallMissed account hit its MONTHLY plan limit (50,000 LLM calls) → gpt-5-mini replay 79.5% done, gpt-4o 0/3000, 25 judge parts failed (retry needs quota).
- Preliminary (`results/main_prelim/`): strict halluc./call A 3.8%, B 2.3%, C 3.2%; paired AUROC on 15,657 common calls: Clef 0.787, gpt-5-mini 0.709 (Δ +0.078, 95% CI [+0.031, +0.115]), Clef-flash 0.599; p50 latency Clef 669 ms vs gpt-5-mini 1774 ms.
- SSH NSG rule updated to 106.213.82.250/32 (user IP changed).
- SECURITY: agent key (fp …643f) was exposed in VM error files (deleted) and in chat → user to rotate.

## Next
Quota (upgrade or monthly reset) → retry: `judge_llm.py --phase main --labels-dir labels_gpt6luna` and `replay.mjs --phase main` (resumable) → final `analyze.py` + significance tests → human κ sample (150 calls) → paper. Delete Azure RG `research-paper` (user decision).
