# System-One Critics for Tool-Call Hallucination

Research prototype comparing a System-One model critic (Cloudflare Clef) with a small-LLM critic (gpt-5-mini) for detecting and reducing tool-call hallucination in a coding agent (OpenCode) on Terminal-Bench 2.0.

- Plan: [`.research/05-experiment-plan.md`](.research/05-experiment-plan.md)
- Background research: [`.research/`](.research/)
- Status: [`CONTEXT.md`](CONTEXT.md)

## Layout
| Path | Purpose |
|---|---|
| `critic/` | OpenCode plugin: critic hook, backends, question set |
| `harbor_ext/` | Harbor agent extension (OpenCode + critic) |
| `configs/` | Per-arm job configs |
| `scripts/` | Collection, transcript, replay, judging, analysis |
| `runs/` | Raw run evidence (append-only, not in git) |
| `data/` | Derived datasets (not in git; published separately) |
| `results/` | Tables and figures |

## Evidence policy
Runs are never deleted or overwritten. Each run lives in `runs/<timestamp>_<arm>/` with a `MANIFEST.sha256`. Upstream versions (OpenCode, Harbor, dataset) are pinned and recorded per run.

## Secrets
Set via environment only: `CALLMISSED_API_KEY`, `CF_ACCOUNT_ID`, `CF_API_TOKEN`.
