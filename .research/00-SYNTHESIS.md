# Synthesis: System-One Verifier for Tool-Call Hallucination

Date: 2026-10-03. Sources: `01-tool-calling-hallucination/`, `02-system-one-jev/`.
Caveat: subagents read pages through WebFetch summaries. Every number and quote is **[Unverified] until it is checked against the original PDF or page**.

## 1. Proposed idea (user)
After each tool call, send (call + result) to a System One model (TypeSafe Jev). It returns P(correct), and the harness injects that value into the main LLM's next step.

## 2. Assessment

| Aspect | Verdict | Basis |
|---|---|---|
| Core direction (separate fast verifier, signal fed back) | Sound, active area | 01/03-mitigation-methods.md |
| Novelty as stated | **Weak**: close prior work exists (Reinforced Agent 2604.27233, Latent Critic 2608.10430, IDK Filter 2607.04034, ToolCritic 2510.17052, ToolRM 2509.11963, Cleanlab TLM) | 01/03, 01/05 |
| Premise "System One does not hallucinate" | **Not supported**. Holds only for output *form*. Third-party tests report confident errors (44.7% acc at 0.74 avg prob; ECE 0.107) | 02/03-claims-vs-evidence.md |
| Jev as sole core | Risky: closed, undisclosed architecture, no fine-tuning on custom triples, no peer review | 02/04, 02/06 |
| Can verifier know the result is true? | No. It only sees text and cannot execute or retrieve | 02/06 |

## 3. Reframing (recommended)
Do not frame the paper as "a non-hallucinating model fixes tool hallucination". Frame it as:

> **Calibrated, low-latency tool-call verification as a feedback signal: which verifier types (schema rules, System-One classifier, fine-tuned encoder, small LLM judge) detect which hallucination classes, and when does feeding the signal back help or hurt the agent?**

Jev becomes one arm in a comparison rather than an assumption. That way the paper still produces a result if Jev underperforms.

### Candidate contributions (gaps not found closed in surveyed work, [Inference])
1. **Per-class detection matrix**: verifier type × hallucination class (selection, argument, format, result-grounding, fabricated result after failure).
2. **Feedback-format ablation**: raw probability vs. binned label vs. natural-language reason vs. hard gate (block/retry). Measure helpfulness *and* harmfulness, since reviewers can hurt near-ceiling agents.
3. **Calibration in the loop**: does post-hoc recalibration (Platt/isotonic) of the verifier change downstream agent success?
4. **Result-side verification**: score the *result's* consistency with the call and the task, not only the call. Prior work focuses mostly on pre-dispatch call checking.
5. **Cost/latency Pareto**: accuracy gain per ms and per $ across verifiers.

## 4. Proposed prototype architecture
```
Agent LLM ──tool_call──▶ [Layer 0: deterministic checks: schema, tool exists, types, enums]
                               │ fail → immediate structured error back to agent
                               ▼
                         Tool executes → result
                               ▼
              [Layer 1: System-One verifier(s): Jev | encoder | small-LLM judge]
                 typed questions: right tool? args grounded in user msg? result
                 answers the call? result indicates error? ...
                               ▼
                 calibrator (fit on labelled dev set) → P(correct), per-question flags
                               ▼
              policy: P≥τ_hi pass silently | τ_lo≤P<τ_hi annotate | P<τ_lo retry/ask
                               ▼
                 injected into next agent turn (format = ablation variable)
```
Rationale: Layer 0 catches format hallucinations at zero cost. The verifier is asked decomposed questions (third-party data showed split questions help Jev: 62.6% → 95.0% on phishing). The policy thresholds keep the agent from being swamped with noise.

## 5. Evaluation plan
- **Verifier-only (offline)**: FC-RewardBench (1,500 pairs), ToolPRMBench, AgentProcessBench, plus synthetic corruptions of BFCL calls and results. Metrics: AUROC, ECE, per-class recall, latency, cost.
- **In-the-loop (online)**: BFCL (incl. irrelevance), tau2-bench, ToolFailBench. Conditions: no verifier / schema-only / self-reflection / each verifier × feedback format. Metrics: task success, hallucination rate, harmful-intervention rate, tokens, latency.
- Report benchmark noise (18.5% evaluator–human disagreement audit, 2607.02577) and use multiple seeds.

## 6. Immediate next steps
1. Read in full: Reinforced Agent, Latent Critic, IDK Filter, ToolCritic, Relign (2412.04141), and verify the numbers.
2. Get Jev access (console.typesafe.ai or OpenRouter `typesafe/jev-1.13`) and confirm the API schema from the official docs.
3. Build the prototype harness with pluggable verifiers (Jev, a cheap LLM judge, a heuristic baseline).
4. Run the offline verifier evaluation first. Only move to in-the-loop if some verifier beats the baselines.

> AI behavior is not guaranteed and may vary.
