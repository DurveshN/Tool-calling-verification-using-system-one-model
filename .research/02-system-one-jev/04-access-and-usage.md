# Access and usage

Status: available now as a hosted, proprietary API. Not open weights. Dates are from secondary sources; verify on console.typesafe.ai.

## Access routes
1. TypeSafe console/API: sign in at https://console.typesafe.ai/ (homepage S4). Docs: https://docs.typesafe.ai/ ; index https://docs.typesafe.ai/llms.txt . Python and JavaScript SDKs are mentioned in the docs (S3).
   - Raw HTTP: POST https://api.typesafe.ai/v1/systemone, Bearer token, JSON body with `state` and `questions` (S16). Exact question schema not captured; read docs primitives page.
2. Waitlist vs open: explainx and orcarouter report "Jev's waitlist is gone" / waitlist "removed ... new accounts start with $5 of credit" from 2026-09-21 (~120M tokens at the listed price). nicolasdeville/noze/eesel still say "waitlist" [stale or conflicting]. [Unverified] current state; try signing up.
3. OpenRouter: `typesafe/jev-1.13` (32,000 ctx, $0.042/M input, free output), `typesafe/jev-latest`. `typesafe/jev-router` is a different product (model router). Note: OpenRouter's chat-style interface may not expose typed Noul/Choice/Score primitives [Unverified]; explainx says Jev has "no standard API ... requires bespoke client integration".
4. Cloudflare Workers AI id `typesafe/jev` (eesel S8) [Unverified].

## Pricing and limits
- $0.042 per million input tokens; output free (S1, S18). Example: ~5,000 requests about $2 (S10).
- Context: 32K (OpenRouter) vs 64k (docs per ayautomate) [conflict]. Choice up to 255 options. Text only. English best.
- Rate limits: docs mention retry policy/rate-limit pages (S3); values not obtained.
- No public pricing page (S13) [may have changed].

## License / weights / fine-tuning
- Proprietary; no weights, no paper (S14). Terms/Privacy/Acceptable Use pages exist on typesafe.ai (not read).
- Fine-tuning/custom training: not documented. You cannot train it on (tool call, result, label) triples as far as public docs show. You can only define questions and recalibrate its outputs externally.

## Concrete steps for a researcher
1. Create an account at console.typesafe.ai, get API key, use $5 credit if offered.
2. Read docs Primitives and Confidence pages; send {state: "<tool call + result text>", questions: {ok: Noul ...}}.
3. Log raw probabilities for your labelled set; fit Platt/isotonic; report ECE/Brier.
4. Pin the model version (e.g. jev-1.13); "jev-latest" is a moving target, which hurts reproducibility.

## Reproducibility risks
Closed, versioned-by-vendor, possibly subsidised pricing (S8); behaviour may change. For a paper, also run an open verifier (see 05).
