# 03 - Tool-call verification design

Everything here is [Inference] unless it cites the API contract in 01. Clef documents classification of a `state` against typed questions; it does not document verification of agent tool calls, and no Clef result on that task was found. AI behavior is not guaranteed and may vary.

## Fit
- [Inference] Clef sees only the text you give it. It cannot execute, re-query, or check external ground truth. It can judge plausibility and consistency between call, schema, and output, and spot error-looking outputs. Its probabilities are not shown to be calibrated for this task [Unverified]; recalibrate on labeled (call, output, label) data.
- BFCL/API-Bank (98.5 / 91.9 for Clef) concern call selection/construction, a related but different task. When2Call: Jev beats Clef (81.0 vs 72.4). RAGTruth hallucination F1 79.4 is the closest published hallucination-like metric, on RAG grounding rather than tool calls.

## Request shape
`state` accepts an object (documented: "structured data (object/array) such as records, chat logs, or application state"), so pass structured JSON.
```json
{
  "model": "clef-flash",
  "state": {
    "tool_schema": {"name": "read_file", "parameters": {"path": "string"}},
    "recent_context": "<last 1-3 agent turns, compact>",
    "tool_call": {"name": "read_file", "arguments": {"path": "src/auth.ts"}},
    "tool_output": "<truncated output, head+tail>"
  },
  "questions": {
    "args_valid": {"type": "noul", "instructions": "Do the tool_call arguments conform to tool_schema and refer to things that exist in recent_context or tool_output?", "criteria": {"true": "arguments valid and grounded", "false": "arguments malformed, invented, or contradict context"}},
    "output_error": {"type": "noul", "instructions": "Does tool_output indicate a failure, empty result, or an error message?"},
    "output_matches_intent": {"type": "noul", "instructions": "Does tool_output plausibly answer what the tool_call was trying to do?"},
    "verdict": {"type": "choice", "instructions": "Overall assessment of this tool call and its output.", "criteria": {"correct": "Call is valid and output is consistent", "hallucinated_call": "Call uses nonexistent tool, parameter, path, or value", "bad_result": "Call fine but output is an error or unusable", "uncertain": "Not enough information"}},
    "risk": {"type": "score", "instructions": "How likely is it that continuing from this step will derail the task?", "criteria": ["None", "Low", "Medium", "High"]}
  }
}
```
- Several questions share one forward pass (joint head, up to 64 per request), so extra questions should add little beyond input tokens [Inference]. Billing is per input token ($0.09 or $0.24 per M).
- `noul` output is `{type:"noul", noul: p}`, p = "Probability the answer is yes"; keep yes = good (or yes = bad) consistent across questions. `choice` returns `choice`, `probabilities`, `confidence`. `score` returns a probability-weighted level in [0, n-1] plus `legend`.
- Keep `instructions` explicit. The earlier Jev research (02-system-one-jev) recorded a secondary-source result of low accuracy when question descriptions were wrong [Unverified]. Test wording variants.

## Injection into the agent
- Turn the answer into a short note (verdict argmax, p(args_valid), p(output_error)); inject only below a threshold tuned on dev data, to limit noise. Threshold choice is a research variable.
- Log each response with `usage.input_tokens` for cost accounting versus Haiku.

## Cost sketch ([Inference], arithmetic from listed prices)
- 1,500 input tokens per verification: Clef about $0.00036, Clef-flash about $0.000135 per call. Output tokens are not priced on the page.

## Experimental plan against the Haiku critic
1. Run Clef and Clef-flash (same questions) and Haiku on identical (call, output) traces with ground-truth labels.
2. Report accuracy/F1 at a fixed threshold, AUROC, ECE/Brier (vendor reports no calibration metric), p50/p95 latency including network, and cost per 1k verifications.
3. Watch truncation on long outputs: head+tail compaction and a token count check against 65,536.
4. Clef-specific rate limit is unknown (task default 300 rpm [Unverified]); matters for parallel agent runs.
5. Optional third arm: Jev, since the API is the same (only base URL and `model` change; Jev endpoint per earlier notes: https://api.typesafe.ai/v1/systemone).
