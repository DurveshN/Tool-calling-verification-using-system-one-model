# Source notes (raw)

Caveat: WebFetch summarised pages with a small model. Quotes are as returned. Secondary sources conflict at points; conflicts are flagged. Full URLs are in 07-references.md.

## S1. Launch blog (primary) https://typesafe.ai/blog/introducing-system-one-models-and-jev
Tool summary: author Diogo Almeida, Founder; page date Sep 28, 2026 (other sources say launch was Sep 15, 2026 [conflict]).
- "similar levels of intelligence on System One tasks compared to existing LLMs, while being two orders of magnitude faster and more efficient."
- Response time 70-500ms vs 3-329 s for frontier LLMs; 40x-200x faster; $0.042 per million input tokens; output "FREE (too cheap to meter)"; "zero hallucinations".
- Training: "Reinforcement Learning for Calibrated Decisions (RLCD)" instead of RLHF/RLVR.
- Use cases include "LLM output verification and guardrailing". Contact hello@typesafe.ai.
Raw full text not obtained.

## S2. Docs concept page (primary) https://docs.typesafe.ai/concepts/system-one
- Inputs: text only (strings, JSON objects, text arrays); no images/audio/video.
- Outputs: Choice, Score, Noul.
- Calibration: probabilities are "optimized against outcomes to reflect uncertainty"; calibration applies to groups of predictions, not individual accuracy (tool paraphrase).
- Models "do not write replies, produce code, or generate explanations of their reasoning".
- Answers are meant to be combined with deterministic code checks.

## S3. Docs intro and llms.txt https://docs.typesafe.ai/introduction , https://docs.typesafe.ai/llms.txt
- "Jev is TypeSafe's flagship model and the first System One model."
- Choice / Score / Noul; "All questions evaluate in parallel against the same state in a single request."
- Noul "returns the probability that the answer is yes".
- Python and JavaScript SDKs, 20+ cookbooks, a "Machine Learning Primer", confidence docs. "Confidence is derived from the probability distribution the answer already gives you."
- Use-case text (as returned by tool): "Place semantic checks on every LLM input, output, and tool call at a fraction of the cost of the LLM call." and "Detect tool-call errors and response-quality failures in real time."
- Cookbook: "Parallel questions" "12.2x cheaper and 10.0x faster" (batching).
- My guessed paths /concepts/confidence and /quickstart returned 404.

## S4. Homepage https://typesafe.ai/
- "193.6x Faster, 444.6x Cheaper"; "$42 Per Billion input tokens"; "238x Lower input price than Claude Fable 5.1"; "Zero Hallucinations"; RLCD addresses "mode dropping and overconfidence". Links: console.typesafe.ai, docs.typesafe.ai, X @typesafeai.

## S5. Manifesto https://typesafe.ai/manifesto
- No technical claims on architecture/calibration. "RLHF, the algorithm almost all of current AI is trained with, directly optimizes for human preference."

## S6. explainx (secondary) https://www.explainx.ai/blog/typesafe-ai-jev-system-one-models-launch-2026
- "TypeSafe hasn't published an architecture paper"; commenters speculated "an encoder-only transformer with classification heads" [Speculation].
- Choice up to 255 options. Context 32K. No OpenAI-style API. Evals are proprietary "workflow evals" vs the average of two frontier LLMs, not ground truth; no public leaderboards.
- CEO on HN: "it's also possible to be confidently wrong".
- Named after Jevons. Founder co-developed RLHF at OpenAI. Launch 2026-09-15; update: waitlist gone, $5 credit (~120M tokens); ~140,000 waitlist signups in 36h.

## S7. ayautomate (secondary) https://www.ayautomate.com/blog/jev-typesafe-system-one-model
- Docs: state plus all questions "64k token budget" [conflicts with 32K].
- OpenRouter test: median 0.33 s, slowest of 791 calls 1.42 s. Every: "roughly 25x faster and 580x cheaper than Claude Fable 5.1 on a single extraction task".
- Benchmarked "against the average answers of two large external models, not a ground-truth key".

## S8. eesel (secondary) https://www.eesel.ai/blog/typesafe-jev
- "produces all its outputs in a single parallel pass and never produces free text at all."
- "cannot produce a type error and cannot return an option that was not in your list"; HN comment: "if it puts a high confidence value on a wrong answer, thats still hallucinating, no?"
- Vercel CEO "up to 18x faster (p95) and more accurate" on safety review [vendor-adjacent anecdote, Unverified].
- Cloudflare Workers AI id `typesafe/jev`; "We can't prove it isn't subsidized." Team: Diogo Almeida, COO Sasha Sheng, CTO Erik Gafni. HN thread size differs by source (1,929 points/508 comments vs 256 comments) [conflict].

## S9. noze.it (secondary) https://www.noze.it/en/insights/jev-system-one-typed-decisions/
- Architecture undisclosed; TypeSafe mentions a "hardware-aware parallel sampler". "The public material does not describe the model in enough detail to reduce it to an ordinary LLM whose logits are read in a single forward pass."
- confidence "does not mean the choice has a 59.6% chance of being right"; a concentration index.
- English primary; "other languages are accepted with lower accuracy". High-cardinality choice: "we do a 2 stage-system of scoring independently then making an explicit choice".

## S10. nicolasdeville notes (aggregator) https://notes.nicolasdeville.com/ai/jev/
- 2,029 phone calls (Muratcan Koylan): AUC 0.78 mid-call. Good Start Labs, 6,003 rubric checks: Jev "agreed with a 5-model panel 90% on average, in a range of 86% to 92%"; caveat "Agreement is evidence about a judge; it doesn't establish who is right." Docs advice: "take 200 labelled examples from your own workflow and check whether the 0.9 bucket is right 90% of the time." Sully.ai median 118ms over 38,012 forecasts. TypeSafe: "not good at System 2 tasks". Fine-tuning not mentioned.

## S11. alexmolas (independent opinion) https://www.alexmolas.com/2026/09/23/jev-cant-be-calibrated.html
- "the same model can be calibrated on one dataset but not on another." Cites a tweet where Jev gave a fair coin heads probability 0.92 (not verified). Noul better calibrated than Choice. Recommends Platt scaling with a few hundred labelled examples.

## S12. beri.net (third-party eval, quality unknown) https://www.beri.net/article/typesafe-jev-typed-decision-model-calibration-decomposition-shadow-eval
- Phishing bench, 1,000 test emails: single-question Jev 62.6% vs Haiku 4.5 81.3% (McNemar p<0.0001); five atomic questions + logistic regression: Jev 95.0%, Haiku 93.2%, regex 91.8% (p=0.063).
- 900 synthetic tickets: ECE 0.107; yes/no underconfident (temperature 0.66), choice/score overconfident (3.29, 3.40); unknowable task "44.7% accuracy while assigning 0.74 average probability".
- Pre-registered: 5,721 calls, 400 items: "95.9% zero-shot"; "16.7%" when question descriptions were wrong; accuracy flat for confidence 0.50-0.95, 100% at 0.99 covering 60.2% of traffic.
- Latency 239 ms median vs Haiku 687 ms; $0.038 vs $0.462 per 1,000 emails.

## S13. wotai https://wotai.co/blog/typesafe-jev-vs-claude-haiku-tested
- 150 passages (rewrite detection): Jev 66.0% = Haiku 66.0%; 455 vs 631 ms; Jev flagged uncertainty on 34.7% of rows vs Haiku 2.7%. "There is no pricing page in their docs".

## S14. orcarouter https://www.orcarouter.ai/blog/jev-typesafe-system-one-what-we-know
- "No paper at launch, no parameter count, no training-compute disclosure, no weights." Evals: Every (caught "six of seven planted defects" vs Claude's seven), pre-registered study, calibration audit (ECE 0.107 vs 0.024 noise floor). Waitlist removed Sep 21, $5 credit.

## S15. layer3labs (search snippet only, not fetched) https://www.layer3labs.io/guides/jev-benchmarks
- "calibration error changes by 0.071 between two ways of posing the same question"; four-class middle "stated 0.750, observed 0.612"; "71.6% of four-class answers sit at exactly 1.00." [Unverified]

## S16. horadecodar https://horadecodar.com.br/?p=45816
- POST https://api.typesafe.ai/v1/systemone, Bearer auth, body {state, questions}. "As the Jev only returns one of the typed options you configured, it doesn't invent new options nor break the output schema." No worked example verifying an LLM output.

## S17. Open alternatives https://rohitraj.tech/notes/jev-alternatives-open-weights-decision-models-2026 , https://huggingface.co/autotrust/JEV
- Laya (421M, ModernBERT-large, Apache-2.0, "0.766" on typed-decisions benchmark); Kev-9B (Qwen3.5 base, "0.852 accuracy with a Brier score of 0.237"); open-alternative-jev (ECE 0.020 on Qwen3.6-27B, 73.7% on 400 cases); openjev (cross-encoder from Qwen3.5-4B-Base, MNLI 0.91). autotrust/JEV-9B: frozen Qwen3.5-9B + 40.2M LoRA + decision head, Apache-2.0, "not affiliated with, endorsed by, or a product of TypeSafe AI". Not independently verified.

## S18. OpenRouter https://openrouter.ai/typesafe , https://runtimewire.com/article/typesafe-jev-router-openrouter-launch
- `typesafe/jev-1.13`: 32,000 ctx, $0.042/M input, free output. `typesafe/jev-router`: 1M ctx, free; a model router, a different product.

## Not found / not public
No paper/arXiv/GitHub/HF weights from TypeSafe, no peer review, no public fine-tuning docs, no TypeSafe-published ECE/reliability numbers, no training data description.
