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

---

# Pilot 2 (v1.0-rc critic: grounded_call + criteria, alert-only)

Runs: `runs/20261003T205115Z_A` (commit 977b754), `runs/20261004T053418Z_B` (977b754), `runs/20261004T082117Z_C` (1b2532a; critic/runner code identical to 977b754). One interrupted arm-B attempt is kept as INVALID (`runs/20261003T213340Z_B`, killed under host memory pressure).

## Outcomes (reward / tool calls)

| task | A | B | C |
|---|---|---|---|
| adaptive-rejection-sampler | **1**/70 | 0/21 | 0/23 |
| bn-fit-modify | 0/27 | **1**/18 | 0/26 |
| constraints-scheduling | 0/12 | 0/18 | 0/16 |
| git-multibranch | **1**/56 | **1**/61 | **1**/56 |
| path-tracing-reverse | 0/429 | 0/117 | 0/93 |
| **pass** | 2/5 | 2/5 | 1/5 |

## Critic behaviour: pilot 1 → pilot 2

| | B pilot1 | B pilot2 | C pilot1 | C pilot2 |
|---|---|---|---|---|
| share P(primary) < 0.5 | 12.2% | **4.7%** | 24.9% | **7.5%** |
| alerts shown to agent | 197 (all) | 11 | 518 (all) | 16 |
| latency p50 / p95 (ms) | 1943 / 2443 | 1980 / 2531 | 761 / 1402 | 752 / 1283 |
| critic errors | 0 | 1 (socket closed) | 0 | 0 |
| critic cost | $0.147 | $0.190 | $0.265 | $0.093 |

## Observations (n = 5 tasks; engineering signals only)

- **P1. The v1.0-rc question cut the flag rate roughly 3×** for both critics. The git-multibranch "harm" seen in pilot 1 (C failed) did not recur (C passed). [Inference] Pilot-1 F2 was likely noise and/or an artifact of the old question.
- **P2. Large run-to-run variance at fixed conditions.** In arm A, adaptive-rejection-sampler went 0 → 1 between pilots. In arm B, constraints-scheduling went 1 → 0. With 1 run per task, pass-rate differences between arms are dominated by chance. **Primary evidence must be call-level** (critic accuracy vs judge labels; hallucinations per call).
- **P3. Alerts mostly hit plausible hallucinations,** with clear false alarms too. [Unverified until judged] path-tracing-reverse alerts target `apply_patch` edits that guess numeric constants with no evidence. After such alerts the next calls often switched to evidence gathering (objdump/struct reads) [Speculation: causal effect unknown]. Clear false alarms: gpt-5-mini flagged a `todowrite` planning call (P=0.02) and a read of the agent's own output file (P=0.12).
- **P4. Possible loop-breaking effect** [Speculation]. path-tracing-reverse: A ran 439/429 calls (timeout both pilots); B 124/117; C 410 → 93 after the critic change. This is a hypothesis for the main run (calls per task and cost by arm), not a finding.
- **P5. Cost is dominated by runaway trajectories.** Agent cost upper bound per arm (5 tasks): A $13.02, B $2.41, C $1.39. CallMissed cache pricing is unpublished, and the connected usage tool shows no LLM rows, so actual spend is **unverified**.
- **P6. Critic latency is stable.** Clef ≈ 2.6× faster than gpt-5-mini at p50.

## Fix before freeze
- Transient critic network error (1 in 449 calls) → `core.js` now retries once on network/5xx/429 errors, never on auth/4xx.

## Freeze proposal (v1.0)
1. Critic, questions, runner and rubric as of the freeze commit.
2. Main run on all 89 tasks × 3 arms, **interleaved by task batches** (each batch runs A, B, C back to back) so time-of-day/API drift does not confound arms and partial results stay balanced if a run stops.
3. Primary analysis = call-level (RQ1 critic quality vs judge labels; hallucinations per call). Task pass rate is secondary, reported with McNemar plus an explicit power caveat.
