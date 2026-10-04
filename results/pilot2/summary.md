# Analysis: phase `pilot2`

Labelled calls: 1043 / 1043

## 1. Hallucination by arm (judge labels)

| arm | tasks passed | calls | strict halluc. | strict / call | broad errors | broad / call | false/unsupported claims | final claim false |
|---|---|---|---|---|---|---|---|---|
| A | 2/5 | 594 | 34 | 0.057 | 236 | 0.397 | 15 | 2 |
| B | 2/5 | 235 | 6 | 0.026 | 71 | 0.302 | 5 | 2 |
| C | 1/5 | 214 | 10 | 0.047 | 56 | 0.262 | 9 | 2 |

## 2. Strict hallucinations / calls, per task

| task | A | B | C |
|---|---|---|---|
| adaptive-rejection-sampler | 0/70 | 0/21 | 0/23 |
| bn-fit-modify | 8/27 | 0/18 | 2/26 |
| constraints-scheduling | 1/12 | 2/18 | 1/16 |
| git-multibranch | 1/56 | 3/61 | 3/56 |
| path-tracing-reverse | 24/429 | 1/117 | 4/93 |

## 3. Label distribution

| label | A | B | C |
|---|---|---|---|
| bad_args | 24 | 5 | 7 |
| misread_output | 10 | 0 | 3 |
| none | 358 | 164 | 158 |
| trajectory_error | 59 | 18 | 18 |
| unnecessary_call | 143 | 47 | 28 |
| wrong_tool | 0 | 1 | 0 |

## 4. Critic quality vs judge labels (positive = strict hallucination; score = 1 − P(grounded_call))

| critic | source | n | positives | AUROC | ECE | recall@0.5 | precision@0.5 | false-alarm rate |
|---|---|---|---|---|---|---|---|---|
| gpt-5-mini | online, arm B | 234 | 6 | 0.787 | 0.071 | 0.167 | 0.091 | 0.044 |
| clef | online, arm C | 214 | 10 | 0.801 | 0.258 | 0.000 | 0.000 | 0.078 |
| clef | replay, all arms (p50 780 ms) | 513 | 27 | 0.634 | 0.349 | 0.370 | 0.057 | 0.340 |
| clef-flash | replay, all arms (p50 518 ms) | 513 | 27 | 0.715 | 0.300 | 0.185 | 0.100 | 0.093 |
| gpt-4o | replay, all arms (p50 986 ms) | 133 | 3 | 0.544 | 0.068 | 0.000 | 0.000 | 0.023 |
| gpt-5-mini | replay, all arms (p50 1845 ms) | 181 | 7 | 0.350 | 0.172 | 0.143 | 0.030 | 0.184 |

Strict = ['bad_args', 'fabricated_tool', 'misread_output', 'schema_violation', 'wrong_tool']; broad adds trajectory_error, unnecessary_call.
Labels come from a single blinded Opus judge, not yet validated against human labels.
