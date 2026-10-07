# Main Results (Terminal-Bench 2.0, 89 tasks × 3 arms)

Date: 2026-10-07. Plan: `.research/05-experiment-plan.md` v1.0 + deviations D1 (judge = gpt-6-luna) and D2 (gpt-4o on a 3,000-call sample).
Sources: `results/main/summary.md` (descriptives), `results/main/stats.md` (tests), `results/main/test_retest.txt`, `results/pilot2_gpt6luna/judge_agreement.txt`.
**Status: complete data. Judge labels cross-checked by an independent LLM annotator (Claude Sonnet), not yet by humans** (150-call blinded sheet `data/human/main/`). Everything below is conditional on the gpt-6-luna judge.

## Setup recap
- Agent: OpenCode 1.18.34 + `gpt-6-luna` (CallMissed), Harbor 0.23.0, Azure DC8as_v5, 2 concurrent trials, batch-interleaved arms.
- Arms: A no critic · B `gpt-5-mini` critic · C Clef critic. Alert injected when P(grounded_call) < 0.5.
- 21,784 tool calls; judge labelled 100% (346 packet parts). Replay coverage: Clef 100%, Clef-flash 100%, gpt-5-mini 21,783/21,784, gpt-4o 3,000/3,000 sample.

## RQ1: critic quality on identical inputs (offline replay)

All calls (n = 21,783, 745 strict hallucinations):

| critic | AUROC [95% CI] | ECE | latency p50 / p95 | $ per 1k checks |
|---|---|---|---|---|
| **Clef** | **0.799 [0.749, 0.839]** | 0.294 | **668 / 1410 ms** | $0.51 |
| gpt-5-mini | 0.710 [0.675, 0.739] | 0.101 | 1770 / 2956 ms | $0.55 |
| Clef-flash | 0.600 [0.528, 0.672] | 0.305 | 359 / 899 ms | $0.19 |

- **Clef − gpt-5-mini AUROC = +0.089, 95% CI [+0.053, +0.116].** H1c (non-inferiority, margin −0.05) is **met**, and the CI excludes 0, so Clef ranks hallucinations *better* on this judge.
- gpt-4o sample (n = 3,000, 99 positives): Clef 0.798 vs gpt-4o 0.666, **Δ +0.132 [+0.064, +0.205]**. gpt-5-mini vs gpt-4o −0.010 [−0.074, +0.059], so the larger GPT critic is not better.
- **H1a (faster): supported.** Clef p50 is 2.6× faster than gpt-5-mini, and its p95 is 1.4 s vs 3.0 s (gpt-4o p95 6.9 s).
- **H1b (cheaper): only weakly supported.** Clef is about 7% cheaper per check than gpt-5-mini and about 9.6× cheaper than gpt-4o. "Very cheap" holds against gpt-4o, not against gpt-5-mini.
- **Calibration: Clef is poorly calibrated** (ECE 0.29 vs 0.10 gpt-5-mini, 0.04 gpt-4o). Its scores rank well but are not probabilities. A recalibration step (Platt/isotonic) is needed before reading P(grounded) literally.
- **Clef-flash (the fastest System-One variant) is significantly worse** than gpt-5-mini (Δ −0.109 [−0.175, −0.048]). Speed alone does not make a good critic.
- **Consistency (test-retest on identical inputs):** Clef verdict flips 0.62% (36/5,833), mean |ΔP| 0.0085. gpt-5-mini flips 9.6% (695/7,229), mean |ΔP| 0.111. Clef is not perfectly deterministic at scale (pilot showed 0/214), but it is ~15× more consistent.

## RQ2: effect on the agent (online arms, paired by task)

| | A none | B gpt-5-mini | C Clef |
|---|---|---|---|
| tasks passed / 89 | 22 | 31 | 31 |
| tool calls | 8,430 | 7,400 | 5,954 |
| strict hallucinations / call | 3.93% | 2.95% | 3.29% |
| strict hallucinations / task | 3.72 | 2.45 | 2.20 |

- **Pass rate:** A vs B and A vs C: 3 vs 12 discordant tasks each, exact McNemar p = 0.035, **Holm-adjusted p = 0.106: not significant** after the pre-registered correction. B vs C identical (7 vs 7).
- **Strict hallucinations, B − A:** −0.98 pp per call [−2.25, −0.08] and −1.27 per task [−2.53, −0.23], **significant**.
- **Strict hallucinations, C − A:** −0.63 pp per call [−2.33, +0.80] and −1.52 per task [−3.20, +0.05], **not significant** (per-task borderline).
- **Excluding the 26 tasks where any arm hit the agent timeout:** every arm difference has a CI including 0.
- C made 29% fewer tool calls than A. B had more "broad" errors (trajectory/unnecessary) per call (+6.8 pp, n.s.).

**Interpretation [Inference]:** both critics move the agent in the right direction, with modest evidence. The better *detector* (Clef) did **not** produce a larger *agent* improvement than gpt-5-mini. Plausible reasons to test next: (1) Clef's higher false-alarm rate at 0.5 (13% vs 7.5%) means more alerts on reasonable calls; (2) one run per task gives low power at the task level; (3) alert format and threshold were tuned on 5 pilot tasks only. A calibrated threshold per critic (equal false-alarm rate) is the obvious follow-up experiment.

## Judge validation: independent cross-family annotator (Claude Sonnet), 150 blinded calls
Sample stratified by judge label (50 strict / 50 broad-only / 50 none, balanced by arm). Sonnet saw the same blinded items as a human would (no arm, no judge label, no critic verdict). Files: `results/main/sonnet_vs_judge_agreement.txt`, `results/main/critic_ranking_by_annotator.txt`.
- Strict hallucination: agreement 81.3%, **Cohen's κ 0.517 (moderate)**, below the pre-registered 0.6 target. Broad κ 0.297, exact label κ 0.345.
- **Direction of disagreement:** Sonnet marked 24 strict; the judge marked 50, of which Sonnet agreed with 23. So gpt-6-luna flags many calls as hallucinations that Sonnet calls reasonable (judge precision 0.46, recall 0.96 relative to Sonnet). On pilot 2, gpt-6-luna was *more lenient* than Opus, so the three LLM judges do not agree on where the line is. Absolute hallucination rates are therefore judge-dependent and should be reported with that caveat.
- **Critic ranking is robust to the annotator:** on the 150 items, AUROC Clef 0.771 vs gpt-5-mini 0.628 with Sonnet labels (0.728 vs 0.648 with judge labels); Clef-flash lowest under both. The Clef > gpt-5-mini conclusion does not depend on which LLM defines the positives.
- This is cross-model agreement, **not human validation**. `data/human/main/labels.csv` remains available for human annotators.

## Threats to validity
1. **Judge = agent model** (gpt-6-luna), and the same family as the arm-B critic. Agreement with other LLM judges is moderate-to-substantial (strict κ 0.685 vs Opus on pilot 2; 0.517 vs Sonnet on the main sample), with inconsistent direction (more lenient than Opus, stricter than Sonnet). Absolute rates are judge-dependent; critic rankings were stable across judges. No human labels yet.
2. The positive class (strict hallucination) is defined by that judge. Critic AUROCs measure agreement with the judge, not ground truth.
3. One run per task. Pilots showed large run-to-run variance in pass/fail.
4. Terminal-Bench is bash-heavy, so other tool types are under-represented.
5. Clef performance claims are first-party; this is an independent evaluation on one benchmark only.
6. CallMissed monthly quota interrupted the replay. Gaps were filled from a second account (same models). Replay-key fingerprints are recorded in CONTEXT.md.

## Claims the data supports (pending human validation)
- A System-One critic (Clef) **detects tool-call hallucinations better than small and large GPT critics** on identical inputs (AUROC +0.09 vs gpt-5-mini, +0.13 vs gpt-4o), **at ~2.6× lower median latency**, with **~15× more consistent verdicts**.
- It is **not** better calibrated, **not** much cheaper than gpt-5-mini, and its faster variant (Clef-flash) is worse.
- Feeding critic alerts back **reduces strict hallucinations per task** (significant for gpt-5-mini, borderline for Clef). **Task success improves in both critic arms but not significantly** after multiple-comparison correction.
