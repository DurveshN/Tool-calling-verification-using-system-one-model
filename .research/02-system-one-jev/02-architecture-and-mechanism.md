# Architecture and mechanism (as far as sources show)

## What it is
A "System One model" evaluates a state and returns typed answers with probabilities; the term borrows Kahneman's fast/intuitive System 1 (search-result summary of docs, S2). Jev is the first. The name comes from Jevons (S6). I found no acronym expansion for "JEV". [Unverified] that "JEV" means anything beyond a stylisation of "Jev".

## Interface (documented)
- Input: `state` (text, JSON, array of text) plus a `questions` map. Text only. Context 32K (OpenRouter, explainx) or 64k (ayautomate citing docs) [conflict].
- Primitives: Noul (P(yes)), Choice (up to 255 options; per-option probabilities plus confidence), Score (value on ordered descriptive levels plus probability and confidence).
- Questions in one request are evaluated in parallel against the same state.
- Endpoint: POST https://api.typesafe.ai/v1/systemone (S16).

## Internals (NOT disclosed)
- No paper, parameter count, weights or compute disclosure (S14). Details kept "close to the chest" (S6/S14). TypeSafe mentions a "hardware-aware parallel sampler" (S9).
- JEPA / joint-embedding / energy-based? No source says so. Classifier? Behaviourally yes (typed outputs). Commenter speculation: "an encoder-only transformer with classification heads" [Speculation, S6]. noze.it: public material is not enough to say it is an LLM with logits read in one pass [S9]. Open reimplementations (S17) are constrained-decoding LLMs, LoRA heads on Qwen, or ModernBERT; they replicate behaviour, not TypeSafe's design.
- [Inference] Docs say confidence is "derived from the probability distribution the answer already gives you", which suggests a softmax-like distribution over options. Not confirmed.

## Training
- RLCD, Reinforcement Learning for Calibrated Decisions: optimises "calibration - a model that says '70% confident' should be right about 70% of the time" (S6/S14). Contrasted with RLHF and RLVR. Data, reward design and size undisclosed.
- Task-specific training: not required per sources (you describe questions; S11 calls it a "universal classifier requiring no training data", tool paraphrase). Fine-tuning on custom (call, result, label) triples: not documented anywhere I found (S9, S10). [Unverified] whether offered privately.

## Calibration
Claimed by design (RLCD). Docs themselves say calibration is group-level. Third-party results show it depends on task and primitive (see 03).
