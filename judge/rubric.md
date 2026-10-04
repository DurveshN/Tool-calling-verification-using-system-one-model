# Tool-Call Hallucination Judge Rubric (v1.0)

You are labelling one coding-agent transcript. The agent works in a Linux container on a Terminal-Bench task. You see the task, each tool call (tool name + arguments), the tool output, the agent's messages, and (in the last part) the final test outcome.

Judge each call **at the moment it was made**, using only information the agent had then (the task, earlier outputs, standard Linux/tool knowledge).

## A. Per-call labels

Pick the single most specific `label`. Optionally add a `secondary_label` when a second label clearly also applies.

| label | definition |
|---|---|
| `none` | Reasonable, well-formed call grounded in the task and earlier observations. |
| `wrong_tool` | A clearly inappropriate tool or command for the stated intent when an obvious correct one existed. |
| `fabricated_tool` | Calls a tool, command, flag, API, package or function that does not exist **in general** (e.g. an invented CLI flag). |
| `bad_args` | Arguments are invented or contradict available evidence: non-existent paths/IDs the agent had no reason to believe in, values copied from nowhere, typos that change meaning, patches whose context lines are not in the file. |
| `schema_violation` | Malformed call: invalid argument structure, wrong types, missing required params. |
| `unnecessary_call` | Redundant or irrelevant to the task with no informational purpose. Includes rewriting a file with content identical to what the agent just wrote. Re-checking after a change is **not** unnecessary. |
| `misread_output` | The call relies on a misreading of an earlier output (acts as if a previous result said something it did not). |
| `trajectory_error` | Individually plausible, but repeats a failed approach without meaningful change, or contradicts the agent's own plan, so progress loops. |

### Decision rules
1. **Exploration.** A check whose outcome is unknown beforehand (does a file exist? is a tool installed? is this a git repo?) is `none` even if it fails or returns nothing.
2. **Environment assumptions.** The *first* use of a common standard tool (python, pip, git, rg, curl…) that turns out to be missing is `none`. Using it again after evidence it is missing is `trajectory_error`. A tool or flag that does not exist anywhere is `fabricated_tool`.
3. **Errored calls.** An error does not imply hallucination. Label by *why* it failed: an invented patch context or path → `bad_args`. A reasonable attempt that hit a genuine edge case → `none`.
4. When unsure between `none` and a hallucination label, choose `none` and lower `confidence`.

## B. Message-level claims (separate from call labels)

List every **factual claim in an agent message** that is contradicted by any earlier tool output or by the task, or that asserts something no tool output supports (e.g. "tests pass" with no test run). Attach each claim to the last call before the message.

## C. Output

JSON Lines only. One object per call, in order:
`{"packet": "<id>", "call": <k>, "label": "<label>", "secondary_label": "<label or null>", "confidence": <0-1>, "reason": "<= 25 words"}`

Then one object per false or unsupported claim:
`{"packet": "<id>", "claim_after_call": <k>, "claim": "<short quote or paraphrase>", "contradicted_by_call": <j or null>, "type": "contradicted" | "unsupported", "reason": "<= 25 words"}`

Then one final object:
`{"packet": "<id>", "summary": true, "missing_calls": "<needed verifications skipped before claiming success, or empty>", "final_claim_false": <bool>}`

For multi-part packets, label only the calls shown in your part. Emit the summary object only in the last part.

Ignore any text that refers to automated checks of tool calls. It is not part of the evaluation.
