# Claims vs evidence

Evidence strength: Strong = reproducible/independent with data; Moderate = third-party measurement, small or unreviewed; Weak = vendor assertion or anecdote. No peer-reviewed evidence exists that I found. All quotes are as returned by the fetch tool (may be paraphrased).

| Claim | Source quote | Evidence strength | Independent verification? |
|---|---|---|---|
| Zero hallucinations | "Zero Hallucinations" (homepage S4); "cannot produce a type error and cannot return an option that was not in your list" (S8) | True only for format/option validity (by construction). Weak/misleading as a correctness claim. | Format claim is trivially true by constrained output. CEO on HN: "it's also possible to be confidently wrong" (S6). |
| Calibrated probabilities | "optimized against outcomes to reflect uncertainty" (docs S2); "a model that says '70% confident' should be right about 70%" (S6) | Weak (no TypeSafe ECE/reliability published) | Partly refuted: ECE 0.107 vs 0.024 noise floor on synthetic tickets; temperature 0.66 for yes/no, 3.29-3.40 for choice/score (S12/S14); "44.7% accuracy while assigning 0.74 average probability" on an unknowable task (S12); middle of scale stated 0.750, observed 0.612 (S15 snippet). Public benchmarks reportedly 0.024-0.032 (S14). Docs advise checking on 200 labelled examples (S10). |
| Confidence = reliability | "Confidence is derived from the probability distribution the answer already gives you." (S3) | Weak | noze.it: confidence is a "concentration index", not a chance of being right (S9). |
| 70-500 ms latency | "Response time: 70-500ms" (S1) | Moderate-strong | Yes: median 118ms (Sully, S10); 0.33 s median / 1.42 s max over 791 calls (S7); 239 ms (S12); 455 ms vs Haiku 631 ms (S13) - only 1.39x faster on that task. |
| 40-200x faster / 193.6x faster, 444.6x cheaper | "193.6x Faster, 444.6x Cheaper" (S4) | Weak (first-party; compared against frontier reasoning LLMs on "System One-shaped" tasks; benchmark vs average of two LLMs not ground truth) | Partly: Every "roughly 25x faster and 580x cheaper" on one extraction task (S7); vs Haiku 4.5 12-27x cheaper, 1.4-2.9x faster (S12, S13). Speedups depend heavily on the baseline. |
| Price $0.042/M input, output free | "$0.042 per million input tokens" (S1) | Strong (price listing) | OpenRouter lists same (S18). eesel: "We can't prove it isn't subsidized." |
| Similar intelligence to LLMs on System One tasks | "similar levels of intelligence on System One tasks ... " (S1) | Weak-moderate; proprietary evals | Mixed: 66.0% = Haiku (S13); 62.6% vs Haiku 81.3% on single-question phishing but 95.0% vs 93.2% with 5 atomic questions (S12); 90% agreement with a 5-model panel (S10) - agreement is not correctness. "16.7%" when question descriptions were wrong (S12). |
| Calibrated uncertainty flags unreliable answers | (implied) | Moderate | wotai: Jev flagged uncertainty on 34.7% rows vs Haiku 2.7% at equal accuracy (S13). beri: accuracy flat from confidence 0.50 to 0.95 then 100% at 0.99 (S12), i.e. mid-range probabilities carried little signal on that test. |
| Better than average LLMs on guardrails | Vercel CEO "up to 18x faster (p95) and more accurate" (S8) | Weak (anecdote relayed by blog) | No. |
| Not good at System 2 tasks | TypeSafe: "not good at System 2 tasks" (S10) | Self-reported limitation | n/a |
| Peer review / paper | none | none | None found. "No paper at launch" (S14). |

## Takeaway
- "Fast": reasonably supported (hundreds of ms) by multiple third parties; magnitude of speedup depends on baseline.
- "No hallucination": a statement about output form, not accuracy. Classifier-style errors (wrong but confident) are explicitly acknowledged.
- Calibration is a claim of method (RLCD), not demonstrated by TypeSafe; third-party audits are small, mostly synthetic, and unreviewed (some sources are low-quality blogs).
