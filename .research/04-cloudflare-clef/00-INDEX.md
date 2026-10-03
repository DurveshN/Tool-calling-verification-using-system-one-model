# 04 - Cloudflare Clef (decision / System One-style model): index
Research date 2026-10-03. Primary sources: Cloudflare docs raw markdown, HF README, Cloudflare blog.

Files: 01-api-reference.md, 02-claims-and-limits.md, 03-tool-call-verification-design.md, 04-references.md

## Key facts
- Model IDs: `@cf/cloudflare/clef` (27B, $0.24/M input tokens, 21818 neurons/M) and `@cf/cloudflare/clef-flash` (9B, $0.09/M, 8182 neurons/M).
- Cloudflare's own model, post-trained from Qwen3.8-27B; open weights (Apache-2.0). Not Jev. Jev-API compatible (same `POST /v1/systemone` body); adds `images`.
- Endpoint: `POST https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/@cf/cloudflare/clef`; binding `env.AI.run(...)`.
- Input: `model`, `state`, `questions` (1-64; types noul/choice/score), optional `images`. Output: `model`, `answers`, `usage`.
- Context 65,536 tokens (long state silently truncated). Free 10,000 neurons/day. Clef-specific rate limit [Unverified]; text-generation default 300 rpm.
- Benchmarks are first-party only; no calibration metrics, no tool-call-verification or Haiku comparison published.
- Gaps: no example response in docs; beta status and language support not stated.
