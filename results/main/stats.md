# Significance tests: phase `main` (judge labels: `labels_gpt6luna`)

Bootstrap: 1000 reps, resampling tasks with replacement (task-level clusters; all arms of a task move together). Seed 20261007.

## 1. Task success (secondary)

| arm | passed |
|---|---|
| A | 22/89 |
| B | 31/89 |
| C | 31/89 |

| comparison | only first passed | only second passed | exact McNemar p | Holm p |
|---|---|---|---|---|
| A vs B | 3 | 12 | 0.0352 | 0.1055 |
| A vs C | 3 | 12 | 0.0352 | 0.1055 |
| B vs C | 7 | 7 | 1.0000 | 1.0000 |

## 2a. Hallucination rates: all tasks (n tasks = 89)

| arm | calls | strict / call | strict / task | broad / call |
|---|---|---|---|---|
| A | 8430 | 3.93% | 3.72 | 22.84% |
| B | 7400 | 2.95% | 2.45 | 29.64% |
| C | 5954 | 3.29% | 2.20 | 23.63% |

Differences (second minus first), 95% bootstrap CI:

| comparison | Δ strict / call | Δ strict / task | Δ broad / call |
|---|---|---|---|
| B − A | -0.98 pp [-2.25 pp, -0.08 pp] | -1.270 [-2.528, -0.225] | +6.80 pp [-4.80 pp, +16.52 pp] |
| C − A | -0.63 pp [-2.33 pp, +0.80 pp] | -1.517 [-3.202, +0.045] | +0.80 pp [-10.89 pp, +10.02 pp] |
| C − B | +0.35 pp [-1.06 pp, +1.61 pp] | -0.247 [-1.270, +0.730] | -6.00 pp [-14.87 pp, +2.39 pp] |

## 2b. Hallucination rates: excluding tasks where any arm hit the agent timeout (runaway loops) (n tasks = 63)

| arm | calls | strict / call | strict / task | broad / call |
|---|---|---|---|---|
| A | 2561 | 4.69% | 1.90 | 15.58% |
| B | 2118 | 3.59% | 1.21 | 13.36% |
| C | 2229 | 3.32% | 1.17 | 13.50% |

Differences (second minus first), 95% bootstrap CI:

| comparison | Δ strict / call | Δ strict / task | Δ broad / call |
|---|---|---|---|
| B − A | -1.10 pp [-2.61 pp, +0.70 pp] | -0.698 [-2.048, +0.238] | -2.22 pp [-8.32 pp, +3.54 pp] |
| C − A | -1.37 pp [-2.80 pp, +0.33 pp] | -0.730 [-2.286, +0.429] | -2.08 pp [-9.26 pp, +4.17 pp] |
| C − B | -0.27 pp [-1.89 pp, +1.19 pp] | -0.032 [-0.683, +0.778] | +0.14 pp [-6.40 pp, +5.92 pp] |

## 3a. Critic quality, all calls (offline replay) (n = 21783 calls, 745 strict positives)

| critic | AUROC [95% CI] | ECE | recall@0.5 | precision@0.5 | false-alarm@0.5 | latency p50 / p95 | $ per 1k checks |
|---|---|---|---|---|---|---|---|
| clef | 0.799 [0.749, 0.839] | 0.294 | 0.518 | 0.123 | 0.131 | 668 / 1410 ms | $0.510 |
| clef-flash | 0.600 [0.528, 0.672] | 0.305 | 0.083 | 0.031 | 0.093 | 359 / 899 ms | $0.191 |
| gpt-5-mini | 0.710 [0.675, 0.739] | 0.101 | 0.295 | 0.122 | 0.075 | 1770 / 2956 ms | $0.550 |

AUROC differences vs `gpt-5-mini` (paired, task-cluster bootstrap, 250 reps):

- clef − gpt-5-mini: +0.089 [+0.053, +0.116]
- clef-flash − gpt-5-mini: -0.109 [-0.175, -0.048]

## 3b. Critic quality, seeded gpt-4o sample (n = 3000 calls, 99 strict positives)

| critic | AUROC [95% CI] | ECE | recall@0.5 | precision@0.5 | false-alarm@0.5 | latency p50 / p95 | $ per 1k checks |
|---|---|---|---|---|---|---|---|
| clef | 0.798 [0.727, 0.855] | 0.294 | 0.505 | 0.119 | 0.128 | 668 / 1428 ms | $0.509 |
| clef-flash | 0.597 [0.503, 0.677] | 0.307 | 0.061 | 0.022 | 0.094 | 361 / 883 ms | $0.191 |
| gpt-5-mini | 0.656 [0.606, 0.707] | 0.097 | 0.202 | 0.088 | 0.071 | 1768 / 2905 ms | $0.551 |
| gpt-4o | 0.666 [0.599, 0.730] | 0.040 | 0.040 | 0.059 | 0.022 | 1271 / 6949 ms | $4.875 |

AUROC differences vs `gpt-4o` (paired, task-cluster bootstrap, 250 reps):

- clef − gpt-4o: +0.132 [+0.064, +0.205]
- clef-flash − gpt-4o: -0.069 [-0.153, +0.017]
- gpt-5-mini − gpt-4o: -0.010 [-0.074, +0.059]

H1c (pre-registered): Clef non-inferior to the LLM critic if the lower CI bound of AUROC(clef) − AUROC(gpt-5-mini) > −0.05.
Score = 1 − P(grounded_call); positive = strict hallucination (judge). ECE computed on that score.
Judge: labels_gpt6luna (single LLM judge; agreement with Opus on pilot 2: strict κ 0.685).
