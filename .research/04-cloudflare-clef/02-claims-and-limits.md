# 02 - Claims, pricing, limits

Method: raw markdown of Cloudflare docs pages and HF README fetched with curl (not summarized), plus the Cloudflare blog post (HTML stripped). Date 2026-10-03. Vendor benchmarks are first-party. No independent third-party Clef evaluation was searched for or found. [Unverified] independence.

## Identity
- Model ID `@cf/cloudflare/clef` (27B) and `@cf/cloudflare/clef-flash` (9B). Docs: "Cloudflare-hosted", "Vision", task label "Text Generation".
- Provider: Cloudflare, NOT Jev and NOT a TypeSafe-hosted model. Blog (https://blog.cloudflare.com/clef-decision-models, 2026-10-01): "we're releasing two Cloudflare-trained decision models, Clef and Clef-flash, hosted on Workers AI." and "These models are smarter, faster, and fully Jev-API compatible".
- Jev relationship: separate competing model by TypeSafe. HF README: "The Clef API is fully compatible with Jev and SystemOne." Request body is the same as `POST /v1/systemone`. Clef adds `images`. Blog: Jev "only does text classification today" and has "32k" context vs Clef "64k".
- Architecture (disclosed): HF: "post-trained from Qwen/Qwen3.8-27B" (Clef); blog says Qwen3.5-9B for Clef-flash. "Joint schema head: a small transformer head that reads the backbone's final hidden states, routes evidence from the state to each question, and scores all options of all questions jointly." "returns a probability for every allowed option of every question in a single forward pass. There is no free-form text generation and no output parsing." Blog: "The decision step is non-autoregressive"; "rank-256 low-rank adapters"; "label-smoothed cross-entropy ... paired with a Brier loss to refine probability calibration"; "Reinforcement Learning for Calibrated Decisions (RLCD)".
- Weights: open, Apache-2.0, https://huggingface.co/Cloudflare/clef (tested "on a single H200"). Self-hosting is documented in the README.
- Context window: 65,536 tokens (docs); blog "64k". HF local `encode_record` default `max_length` is 16,384 tokens ([Inference] a local-code default that may differ from hosted behavior).

## Pricing (https://developers.cloudflare.com/workers-ai/platform/pricing/)
- Clef: "$0.240 per M input tokens | 21818 neurons per M input tokens". Clef-flash: "$0.090 per M input tokens | 8182 neurons per M input tokens". No output-token price listed (usage returns `output_tokens`; [Unverified] whether billed).
- "$0.011 per 1,000 Neurons"; free: "10,000 Neurons per day at no charge" (Workers Free and Paid). [Inference] 10,000 neurons/day is about 458k Clef input tokens or about 1.22M Clef-flash input tokens per day (arithmetic from the listed rates).
- The pricing page lists paid-required models explicitly; Clef is not in that list.

## Rate limits (https://developers.cloudflare.com/workers-ai/platform/limits/, updated Sep 17, 2026)
- Per task type: "Text Generation: 300 requests per minute, unless the model requires the Workers Paid plan" (then 20 rpm standard billing, 50 rpm prepaid credits).
- The Clef pages state no model-specific limit. [Inference] Clef is labeled "Text Generation" and is not on the paid-required list, so 300 rpm may apply. [Unverified]; test it.
- "Beta models may have lower rate limits". The Clef pages do not label Clef beta. Blog: "We're still early here". Beta/GA status: [Unverified].

## Benchmarks (first-party; HF README "internal run of the Decision Index 0.2.1")
Clef / Clef-flash / Jev (percent unless stated):
- BFCL case exact 98.5 / 98.8 / 95.8
- API-Bank 91.9 / 93.1 / 88.2
- ToolRet nDCG@10 69.2 / 66.4 / 65.3
- When2Call MCQ 72.4 / 65.6 / 81.0 (Jev better)
- RAGTruth hallucination F1 79.4 / 35.6 / 76.5
- HoVer 65.2 / 61.2 / 72.9; NLI4CT 82.9 / 78.6 / 84.1; ANLI 69.8 / 59.1 / 74.8 (Jev better on these)
- ForecastBench Brier (lower better) 13.9 / 10.6 / 17.4
- Workflow evals, Agent trace observability primary action 68.5 / 69.8 / 71.6 (Jev best); Invoice primary action 86.2 / 73.3 / 83.1.
- Latency (benchmark-run request latency): median 209.3 / 38.8 / 524.1 ms; p95 238.6 / 122.4 / 536.0 ms. Blog: Clef domain-classification workflow 2.2 s end-to-end (fetch+render+classify) vs gpt-oss-120b 4.7 s.
- Calibration: training uses a Brier loss "to refine probability calibration" (blog). I found NO published calibration metric (ECE, reliability) for Clef. Calibration of outputs is [Unverified]. Leaderboard: https://clef-evals.workers-ai-mle.workers.dev (not fetched).
- Blog: "Clef is currently the leader when evaluated against the Jev Decision Index" (vendor claim; Cloudflare ran the benchmark).
- Not found: any benchmark comparing Clef against an LLM critic (e.g. Haiku), or on judging tool-call results after execution. BFCL/API-Bank measure choosing/forming calls, not judging a returned result. [Inference]

## Limits and caveats
- Input: 65,536 tokens; "Long text state is truncated to fit the model's token limit" (silent truncation: put the call and key evidence early/compact, [Inference]).
- Images: max 4, 4 MiB and 16 MP each, 8 MiB total, request body max 13 MiB, no remote URLs.
- Questions: 1-64 per request; choice 2-255 options; score 2-10 levels; noul optional true/false criteria.
- Languages: no language support statement found. [Unverified]
- Privacy (blog): "we don't read, store, or train on your requests or responses" (unless using fine-tuning).
- Fine-tuning: FDE-led service now; self-serve later (blog).
- Docs gaps: no example response, no error codes, no streaming statement.
