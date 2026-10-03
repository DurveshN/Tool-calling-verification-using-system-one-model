# Pilot Report (Phase 2)

Date: 2026-10-03/04. Runs: `runs/20261003T182904Z_A`, `runs/20261003T191503Z_B`, `runs/20261003T194224Z_C` (phase=pilot, commit a59e002).
Tasks (seed 20261003, stratified): bn-fit-modify (hard), path-tracing-reverse (hard), adaptive-rejection-sampler, constraints-scheduling, git-multibranch (medium).
**n = 5 tasks × 1 run. Nothing here is statistically meaningful. These numbers are for engineering decisions only.**

## 1. Outcomes

| task | A (none) | B (gpt-5-mini) | C (clef) |
|---|---|---|---|
| adaptive-rejection-sampler | 0 (18 calls) | setup timeout | setup timeout |
| bn-fit-modify | 0 (23) | **1** (21) | 0 (27) |
| constraints-scheduling | 0 (13) | **1** (12) | 0 (18) |
| git-multibranch | **1** (59) | **1** (40) | 0 (67) |
| path-tracing-reverse | 0 (439, agent timeout) | 0 (124) | 0 (410, agent timeout) |
| **pass** | 1/5 | 3/4 | 0/4 |

## 2. Critic behaviour

| | B gpt-5-mini | C clef |
|---|---|---|
| critic calls | 197 | 518 |
| critic errors | 0 | 0 |
| latency p50 / p95 | 1943 / 2443 ms | 761 / 1402 ms |
| mean P(correct) | 0.795 | 0.635 |
| share P < 0.5 (flagged) | 12.2% | 24.9% |
| share P < 0.2 | 5.6% | 10.0% |
| critic cost (pilot total) | $0.15 | $0.27 |

Replay smoke test (same logged input, 4 critics): large disagreement on identical calls (e.g. gpt-4o 1.00 vs clef-flash 0.15).

## 3. Findings that change the design

**F1. The primary question conflates "the call failed" with "the call was a hallucination".** [Inference, from inspecting C/git-multibranch: 33 of 67 calls flagged.] Clef gave low P(correct) to reasonable exploratory calls whose output was negative: `git status` in a non-repo (0.39), `glob` returning "No files found" (0.32), `ls -la /` (0.41). The rubric treats informative failed exploration as `none`. Other flags look like real hallucinations (assuming `sshpass` / `rg` are installed → fabricated_tool). So the primary score must measure *groundedness given what the agent knew*, not *success*.

**F2. Possible harm from false alarms.** [Speculation, n=1 per task] C passed 0/4, including git-multibranch, which A and B passed. Clef flags twice as often as gpt-5-mini. Injecting low scores on reasonable calls may derail the agent. This is exactly the harm the paper must measure, but the treatment design should not cause it by asking the wrong question (F1).

**F3. Errored tool calls were invisible to the critic.** OpenCode's `tool.execute.after` does not fire when a tool throws (12 pilot calls, all `apply_patch` "Failed to find expected lines", i.e. patching code that isn't in the file). **Fixed** (commit 3099eef): logged via the event hook for offline replay, and the error text is recovered in `collect.py`. Online, the agent already sees the error.

**F4. Setup timeouts are infrastructure noise.** 2/15 trials hit `AgentSetupTimeoutError` (Node/OpenCode install > 360 s). **Fixed**: 3× setup timeout, retries only for this error.

**F5. Runaway loops dominate cost.** path-tracing-reverse ran 439 and 410 calls. Agent cost upper bound is $11.39 for that one trial, against ~$0.04 median for others. 99.5% of agent input tokens were cache reads, but CallMissed's cache price is not published, so true cost is unverified. Pilot total: agent ≤ $24.92 (upper bound), critics $0.41.

## 4. Proposed v1.0 decisions (need approval)

1. **Primary question → `grounded_call`**: "Given only what the agent knew at this point (task, earlier outputs), was this call a reasonable, well-grounded action? Exploratory calls that fail informatively count as yes. Invented paths, commands, flags or file contents count as no." Keep `executed_ok`, `args_grounded`, `tool_fit`, `output_consistent` as diagnostics; drop `overall_correct` as primary.
2. **Injection policy → alert-only**: inject the `[tool-check]` line only when the primary P < 0.5. This matches real guardrail deployments, reduces noise, and makes "false alarm" well defined. (Alternative: always inject, which is noisier.)
3. **Runaway control**: keep Terminal-Bench default timeouts (benchmark-standard, comparable to the leaderboard). Accept the cost, *or* cap the agent at N steps via OpenCode config [cap mechanism unverified].
4. **Re-pilot** the 5 tasks × 3 arms with v1.0 questions before the main run, since the treatment changed.
