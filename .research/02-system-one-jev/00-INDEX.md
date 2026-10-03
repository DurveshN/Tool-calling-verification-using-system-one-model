# 02 - System One models / Jev (typesafe.ai): research index

Research date: 2026-10-03. Method: WebFetch/WebSearch only. IMPORTANT: WebFetch returns a small-model summary of each page, not raw HTML, so "quotes" below are as returned by that tool and may be paraphrased by it. [Unverified] against raw page text. Many sources are secondary blogs (several look SEO-style). Re-check key quotes on the primary pages before citing in a paper.

## Files
- 01-source-notes.md - per-source notes and quotes
- 02-architecture-and-mechanism.md
- 03-claims-vs-evidence.md
- 04-access-and-usage.md
- 05-related-concepts-and-alternatives.md
- 06-fit-for-tool-call-verification.md
- 07-references.md

## Executive summary
- "Jev" is TypeSafe AI's first "System One model": a non-generative model returning typed decisions (Choice / Score / Noul = yes-no probability), each with a probability and a "confidence". Launched 2026-09-15, early access. The name comes from Jevons (per explainx), not an acronym; I found no expansion of "JEV". The training algorithm acronym is RLCD (Reinforcement Learning for Calibrated Decisions).
- Architecture is NOT disclosed (no paper, parameter count, or weights). No source says it is JEPA or energy-based; do not claim that. [Inference] Behaviourally it is classifier-like with constrained outputs.
- Access: hosted proprietary API (https://api.typesafe.ai/v1/systemone), console.typesafe.ai. Sources conflict on waitlist vs open signup (two say the waitlist was removed 2026-09-21 with $5 credit). Also on OpenRouter (typesafe/jev-1.13) and Cloudflare Workers AI. $0.042/M input tokens, output free. No fine-tuning documented. Open-weight lookalikes exist.
- "Doesn't hallucinate" holds only narrowly: output is schema-valid and drawn from your options. It does NOT mean correct. Per explainx/eesel, TypeSafe's CEO conceded on HN "it's also possible to be confidently wrong". Third-party tests show miscalibration and task-dependent accuracy (62.6% vs Haiku 81.3% on single-question phishing; ECE 0.107 on synthetic tickets; 16.7% accuracy when question descriptions were wrong).
- "Fast": supported by several third-party latency measurements (about 118-455 ms medians). The "193.6x faster / 444.6x cheaper" headline is first-party and compares against a generative workload.
- Fit for tool-call verification: plausible as a cheap plausibility/consistency scorer; cannot know ground truth of a tool result beyond the text it is given; probabilities must be recalibrated on your own (call, result, label) data. Use as one candidate verifier plus baselines, not as a correctness guarantee. See 06.
