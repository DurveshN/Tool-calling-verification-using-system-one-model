# Fit for "verify tool call + result -> probability"

Labels: facts from sources cite S-numbers (see 01); anything else is [Inference].

## Input format needed
Documented interface: `state` (text/JSON/array) + typed `questions` (S2, S16). A natural encoding:
- state: JSON {"tool": name, "arguments": {...}, "result": ..., optionally "user_request", "tool_schema", "prior_steps"}
- questions: Noul "Is the tool call correct for the user's goal?", Noul "Is the result consistent with the call and plausible?", Choice "error_type" among fixed options, Score "severity".
TypeSafe docs list "tool call" checks as an intended use (S3, tool paraphrase) but I found no worked example verifying a tool call or published accuracy for it (S16: "No code example"). Question wording matters: accuracy fell to "16.7%" with wrong descriptions (S12), and splitting into several atomic questions raised accuracy from 62.6% to 95.0% on one task (S12). [Inference] Budget for prompt/question engineering and for context limit (32K or 64k, S6/S7).

## Can it know the ground truth of a tool result?
No. It sees only the text you send; it has no tool access, no retrieval, no execution, and generates no reasoning (S2). [Inference] It can only judge (a) plausibility from world knowledge learned in training, (b) internal consistency between call, schema, result and request, (c) stylistic signals of error (error strings, empty results). If a tool returns a wrong-but-plausible value (stale price, wrong record) it cannot detect it unless the correct value is in the context. This is the central hallucination-in-tool-calling case. Docs themselves say to combine with deterministic checks (S2).

## Failure modes
1. Confidently wrong: acknowledged by TypeSafe's CEO (S6). Probabilities may be miscalibrated: ECE 0.107 vs 0.024 floor (S14); "44.7% accuracy while assigning 0.74 average probability" on unknowable task (S12). So a high score is not a safety guarantee.
2. Primitive-dependent calibration: Noul underconfident, Choice/Score overconfident (S12); "calibration error changes by 0.071" with question phrasing (S15, snippet). Prompt sensitivity.
3. Distribution shift: calibration is "not a property of the model but of the distribution of your data" (S11). Tool-call data differs from the unknown training mix.
4. Weak confidence signal in mid-range: accuracy flat 0.50-0.95 on one test (S12); saturated answers, "71.6% of four-class answers sit at exactly 1.00" (S15).
5. System-2 weakness: "not good at System 2 tasks" (S10) - multi-step arithmetic or logic checks of results are out of scope.
6. Non-English/long context/multimodal limits (S9, S2).
7. Feedback-loop risk [Inference]: feeding a probability back to the main LLM may bias it (over-trust or needless retries); this is separate from Jev's accuracy and needs its own ablation.
8. Reproducibility/vendor risk: closed, unversioned "latest", possibly subsidised price (S8).
9. Latency adds per tool call (~100-450 ms, S10/S7/S13) - fine for sync checks, not free in long agent chains.

## Suitability verdict [Inference]
- Suitable as: a cheap, fast, zero-shot first-pass scorer and an interesting baseline; plausible for catching obvious errors (tool errors in output, schema/intent mismatch).
- Not suitable as: the core guarantee of correctness, nor as a ground-truth oracle. The paper should not state it "does not hallucinate and is right"; at most "cannot emit off-schema answers".
- Better paper framing: treat the verifier as a pluggable component; evaluate Jev against a fine-tuned DeBERTa/ModernBERT trained on (call, result, label) triples (which Jev cannot be trained on), with post-hoc calibration, measuring AUROC/ECE and end-task effect of the feedback.
- Require your own labelled tool-call set (>=200 as TypeSafe suggests, S10; more for stable ECE).
