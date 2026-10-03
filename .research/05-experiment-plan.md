# Experiment Plan: System-One Critic vs Small-LLM Critic for Tool-Call Hallucination

Status: DRAFT v1 (2026-10-03). Freeze this as v1.0 before any non-pilot run. Record every later change in §14.
Labels: [V] = verified from source this session, [U] = unverified, [I] = inference.

---

## 1. Research questions and hypotheses

| ID | Question | Hypothesis (pre-registered) |
|---|---|---|
| RQ1 | As a *detector* of tool-call hallucination, how do System-One models (Clef, Clef-flash) compare with small-LLM critics (gpt-5-mini, gpt-4o)? | H1a: Clef's latency per check is lower. H1b: Clef's cost per check is lower. H1c: Clef's AUROC is no worse than the LLM critic's (non-inferiority margin 0.05). H1d: Clef has a lower critic-error rate ("critic hallucination" = confident wrong verdict). |
| RQ2 | Does injecting a critic verdict after each tool call reduce agent hallucination and change task success? | H2: hallucinations/task are lower in B and C than in A. Task pass rate is not lower (no net harm). |
| RQ3 | Which hallucination classes does each critic catch? | Exploratory (no directional hypothesis). |
| RQ4 | How much latency, cost and harm (false alarms that derail a correct agent) does each critic add? | H4: Clef adds less wall-clock overhead than the LLM critic. |

Primary claim the paper tests: *a System-One critic gives a faster and cheaper verdict with fewer critic errors than a small-LLM critic.*

## 2. Variables

- **Independent:** critic type (none / LLM / Clef / Clef-flash).
- **Controlled (identical across arms):** agent model `gpt-6-luna` (CallMissed); OpenCode version (pinned); Harbor version (pinned); task set; timeouts; temperature/reasoning settings; critic input-construction function; truncation rule; injection format; Docker images.
- **Dependent:** see §9.

## 3. Arms

| Arm | Online (agent sees verdict) | Critic model | Source |
|---|---|---|---|
| A | none | — | — |
| B | yes | `gpt-5-mini` (CallMissed) | `https://api.callmissed.com/v1` [V] |
| C | yes | `@cf/cloudflare/clef` | Cloudflare Workers AI [V per subagent] |
| Offline only | no | `gpt-4o`, `clef-flash`, `gpt-5-mini`, `clef` | replay (§7) |

**Why gpt-5-mini online:** it is the closest "small, cheap critic" analogue to Haiku. It costs $0.26/M in and $2.08/M out, against gpt-4o at $2.60/$10.42 [V, CallMissed catalogue]. gpt-4o is still evaluated offline at low cost, so both are covered.
**Caveat (threat):** gpt-5-mini and gpt-6-luna are both OpenAI models, so their blind spots may be shared [I]. Report this as a threat to validity.

## 4. Two-phase design (cost-efficient)

1. **Phase 1, online runs:** arms A, B, C on Terminal-Bench 2.0 (89 tasks). This produces trajectories.
2. **Phase 2, offline replay (main RQ1 evidence):** every tool call from **all** arms is replayed through **all four critics** with an identical input. Online labels are not needed for this. The same calls are scored by every critic, giving a paired comparison at the tool-call level (thousands of samples instead of 89).

Why: RQ1 (critic quality) needs many labelled calls, which replay provides cheaply. RQ2 (agent effect) needs the online arms.

## 5. System architecture

```
Harbor (WSL2 + Docker)
 └─ task container (Terminal-Bench 2.0 task)
     └─ opencode run --format=json  (model: callmissed/gpt-6-luna)
         └─ plugin: critic.ts   [tool.execute.after]
              1. build critic input (§6) from {task, recent steps, tool, args, output}
              2. CRITIC_MODE=none | llm | clef      (env var per arm)
              3. call critic → P(correct), per-question probs, latency, tokens
              4. append fixed-format verdict to output.output   (skipped if none)
              5. append JSON record to $LOG_DIR/critic.jsonl     (always, incl. arm A with verdict=null)
```

`tool.execute.after(input:{tool,sessionID,callID,args}, output:{title,output,metadata})` [V, plugin type source]. Whether mutating `output.output` reaches the model is **[U], verify in Phase 0**.

### Files to build

| Path | Purpose |
|---|---|
| `critic/critic.ts` | OpenCode plugin: hook, input builder, backends, injection, logging |
| `critic/questions.json` | the fixed question set, shared by every critic |
| `critic/backends/llm.ts` | CallMissed OpenAI-compatible call. JSON output with probabilities |
| `critic/backends/clef.ts` | Cloudflare `ai/run/@cf/cloudflare/clef` call |
| `harbor_ext/opencode_critic.py` | Harbor agent subclass of `OpenCode`: installs the plugin into `~/.config/opencode/plugins/`, sets the CallMissed provider via `opencode_config`, and passes the `CRITIC_MODE` and API-key env vars |
| `configs/arm_{A,B,C}.yaml` | Harbor job configs (only `CRITIC_MODE` differs) |
| `scripts/collect.py` | joins Harbor `trajectory.json` + `critic.jsonl` + test result → `data/calls.jsonl`, `data/tasks.jsonl` |
| `scripts/to_markdown.py` | readable per-task transcript `.md` (prompt, every model message, tool call, output, critic verdict, latency) |
| `scripts/replay.py` | Phase 2: runs all critics over `data/calls.jsonl` → `data/replay.jsonl` |
| `scripts/judge_packets.py` | builds blinded judge inputs (§8) |
| `scripts/analyze.py` | metrics + statistics (§9–10) → `results/*.csv`, figures |
| `runs/{arm}/{task}/` | raw outputs (gitignored) |

Secrets are kept only in env vars (`CALLMISSED_API_KEY`, `CF_ACCOUNT_ID`, `CF_API_TOKEN`), never in files.

### CallMissed as an OpenCode provider
`opencode_config` overlay [V that the overlay mechanism exists; exact provider schema U]:
```json
{"provider":{"callmissed":{"npm":"@ai-sdk/openai-compatible",
  "options":{"baseURL":"https://api.callmissed.com/v1","apiKey":"{env:CALLMISSED_API_KEY}"},
  "models":{"gpt-6-luna":{}}}}}
```
Run with model `callmissed/gpt-6-luna`.

## 6. Critic input and questions (identical for all critics)

**State** (the same function for every critic):
- `task`: the task instruction (first user message)
- `recent`: the last 3 tool calls (tool + args + first 500 chars of output)
- `call`: `{tool, args}`
- `output`: the tool output, truncated to the head 6k + tail 2k tokens, with an explicit `[...truncated N tokens...]` marker

The same truncation applies to every critic, so Clef's silent 64k truncation never triggers.

**Questions** (yes/no probabilities; `noul` for Clef, JSON probabilities for the LLM):
1. `tool_fit`: Is this tool an appropriate choice for the agent's current step?
2. `args_grounded`: Are the arguments valid and grounded in the task/context (no invented paths, flags, IDs, APIs)?
3. `executed_ok`: Did the call execute successfully (no error, non-zero exit or missing resource)?
4. `output_consistent`: Is the output consistent with what this call should produce?
5. `overall_correct`: Overall, was this a correct and useful tool call? → **primary score P(correct)**

**Injected text** (fixed, the same for B and C. No free-text reasons, so the LLM's explanations don't confound the comparison):
```
[tool-check] P(correct)=0.31  flags: args_grounded=0.22, executed_ok=0.40
```
Flags are listed when a question's probability is below 0.5. The injection threshold (always vs. only when P<τ) is decided in the pilot and then frozen. Default: always inject.

## 7. Benchmark integration (Terminal-Bench 2.0 via Harbor)

- Dataset: `terminal-bench/terminal-bench-2`, all 89 tasks [V per subagent]. The same task list and order are used for every arm.
- Command shape [U, confirm with `harbor run --help`]:
  `harbor run -d terminal-bench/terminal-bench-2 --agent-import-path harbor_ext.opencode_critic:OpenCodeCritic -m callmissed/gpt-6-luna --ak critic_mode=clef`
- Ground truth: Terminal-Bench automatic tests give pass/fail per task [V per subagent].
- Environment: Windows 11 → Docker Desktop + WSL2. Harbor runs inside WSL2.
- Repeats: 1 run per task per arm in the main study. If budget allows, a 2nd repeat for arm A only, to measure run-to-run noise.

## 8. Hallucination labelling (Opus judge)

1. `judge_packets.py` per task-run:
   - strips all `[tool-check]` lines,
   - replaces the arm with a random ID,
   - shuffles the packet order.
2. Opus subagents label **each tool call** using the taxonomy in `.research/01-tool-calling-hallucination/01-definitions-taxonomy.md`:
   - `none | wrong_tool | fabricated_tool | bad_args | schema_violation | unnecessary_call | missing_call | misread_output | fabricated_result_claim | trajectory_error`
   - plus `confidence` and a one-line justification.
3. The judge also labels each final agent message for false claims (e.g. "tests pass" when they don't).
4. **Human validation:**
   - you label a stratified sample of 150 calls, blind to the judge's labels;
   - report Cohen's κ (target ≥ 0.6);
   - if κ < 0.6, revise the rubric and re-judge everything.
5. Label definition for critic evaluation: `hallucinated = label != none`.

## 9. Metrics

**Critic level (RQ1, RQ3, offline replay, n = all tool calls):**
- AUROC and AUPRC of `1 − P(correct)` vs the `hallucinated` label
- ECE (10 bins) and Brier score
- precision/recall/F1 at τ = 0.5
- **critic-error rate**: confident wrong verdicts (P > 0.8 on a hallucinated call, or P < 0.2 on a clean call). This is the operational definition of "critic hallucination".
- per-class recall
- latency p50/p95 (ms)
- cost per 1,000 checks (USD)

**Agent level (RQ2, RQ4, online, n = 89 tasks/arm):**
- task pass rate
- hallucinations per task; hallucination rate per call
- **harm rate**: tasks passing in A but failing in B/C
- **rescue rate**: tasks failing in A but passing in B/C
- false-alarm count (critic flags a clean call)
- wall-clock time per task; agent and critic tokens and cost

## 10. Statistics

- Pass rate: exact McNemar (paired by task) for A–B, A–C, B–C, with Holm correction.
- Per-call/per-task rates: paired cluster bootstrap over tasks (10k resamples), 95% CI.
- AUROC difference: DeLong test (paired by call) or a bootstrap.
- H1c non-inferiority: the lower 95% CI bound of (AUROC_Clef − AUROC_LLM) is greater than −0.05.
- [I] Power: with 89 tasks, only large pass-rate differences (~15 pp) are detectable. The critic-level analysis (thousands of calls) is the well-powered part. Report this openly.

## 11. Phases and exit criteria

| Phase | Work | Exit criterion |
|---|---|---|
| 0. Feasibility | Install WSL2/Docker/Harbor. Run 1 TB2 task with stock OpenCode + CallMissed. Verify plugin mutation reaches the model. Verify Clef + gpt-5-mini API responses. | One task end-to-end in each arm. Verdict visible in trajectory. |
| 1. Build | Plugin, Harbor subclass, collect / markdown scripts | Unit check on 3 synthetic tool calls (one correct, one bad-arg, one error) |
| 2. Pilot | 5 tasks × 3 arms | No crashes. Cost and time per task measured. gpt-6-luna pass rate not 0% (else reconsider model). Injection threshold decided. **Freeze plan v1.0.** |
| 3. Main run | 89 tasks × A, B, C | All trajectories collected |
| 4. Replay | 4 critics over all calls | `replay.jsonl` complete |
| 5. Judge + validate | Opus labels + human 150-call κ | κ ≥ 0.6 |
| 6. Analysis | `analyze.py`, figures, tables | Results for every RQ |
| 7. Write-up | Paper draft | — |

## 12. Budget

Unknown until the pilot: tokens per task for gpt-6-luna on TB2 are not yet measured. After the pilot:
`cost = 89 × 3 × cost_per_task_agent + n_calls × Σ critic_cost + judge_cost`.
Note: the Clef free tier (10k neurons/day ≈ 0.46M input tokens/day [per subagent]) is likely too small, so a paid Workers plan may be needed [I].

## 13. Threats to validity

- The LLM judge may be biased → blinding + human κ.
- Critic and agent are both OpenAI models (gpt-5-mini / gpt-6-luna) → reported. A non-OpenAI critic may be added offline.
- TB2 is bash-heavy → limited coverage of other tool types. A secondary MCPMark-filesystem run is optional.
- Clef performance claims are first-party only → this paper is an independent test.
- Run-to-run nondeterminism → repeat arm A on a subset.
- Truncation may hide errors → the same rule applies to every critic, and the truncation rate is reported.
- LLM-critic probabilities are verbalized, Clef's are native → report this as part of the comparison. Use logprobs if CallMissed returns them [U].

## 14. Change log

| Date | Version | Change | Reason |
|---|---|---|---|
| 2026-10-03 | draft | initial plan | — |
| 2026-10-03 | draft | Evidence policy: runs append-only in `runs/<ts>_<arm>/` with `MANIFEST.sha256` + pinned versions; raw data published as dataset (HF/Zenodo), code on GitHub; no upstream forks unless patching is required | user requirement: never lose evidence, reproducible public repo |
| 2026-10-03 | draft | Phase 0 decisions: (1) plugin runs in ALL arms; arm A = CRITIC_MODE=none logs exact critic input without calling a critic, and replay reuses the logged inputs; (2) LLM critic uses `reasoning_effort: minimal` + JSON mode (1.5 s vs 4 s default); (3) CallMissed returns `logprobs: null`, so LLM probabilities are verbalized; (4) Clef `questions` is a map keyed by id; (5) OpenCode pinned 1.18.34, Harbor 0.23.0, TB2 local copy sha256 561f0e32…; (6) runner refuses dirty git tree | Phase 0 feasibility results |

## 15. Open items (must resolve in Phase 0)

1. Is Docker Desktop + WSL2 installed? (user)
2. Does mutating `output.output` in `tool.execute.after` reach the model? [U]
3. Harbor `--agent-import-path` / agent kwargs flag names [U]
4. CallMissed: is `gpt-6-luna` tool calling OK through the `@ai-sdk/openai-compatible` provider? Are logprobs supported? [U]
5. Clef rate limits [U]
