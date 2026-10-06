# Analysis: phase `pilot2`

Labelled calls: 1043 / 1043

## 1. Hallucination by arm (judge labels)

| arm | tasks passed | calls | strict halluc. | strict / call | broad errors | broad / call | false/unsupported claims | final claim false |
|---|---|---|---|---|---|---|---|---|
| A | 2/5 | 594 | 24 | 0.040 | 200 | 0.337 | 11 | 2 |
| B | 2/5 | 235 | 5 | 0.021 | 60 | 0.255 | 5 | 2 |
| C | 1/5 | 214 | 7 | 0.033 | 36 | 0.168 | 10 | 4 |

## 2. Strict hallucinations / calls, per task

| task | A | B | C |
|---|---|---|---|
| adaptive-rejection-sampler | 0/70 | 0/21 | 0/23 |
| bn-fit-modify | 5/27 | 0/18 | 2/26 |
| constraints-scheduling | 1/12 | 2/18 | 1/16 |
| git-multibranch | 2/56 | 3/61 | 4/56 |
| path-tracing-reverse | 16/429 | 0/117 | 0/93 |

## 3. Label distribution

| label | A | B | C |
|---|---|---|---|
| bad_args | 22 | 5 | 7 |
| misread_output | 2 | 0 | 0 |
| none | 394 | 175 | 178 |
| trajectory_error | 2 | 3 | 9 |
| unnecessary_call | 174 | 52 | 20 |

## 4. Critic quality vs judge labels (positive = strict hallucination; score = 1 − P(grounded_call))

| critic | source | n | positives | AUROC | ECE | recall@0.5 | precision@0.5 | false-alarm rate |
|---|---|---|---|---|---|---|---|---|
| gpt-5-mini | online, arm B | 234 | 5 | 0.870 | 0.075 | 0.200 | 0.091 | 0.044 |
| clef | online, arm C | 214 | 7 | 0.818 | 0.272 | 0.000 | 0.000 | 0.077 |
| clef | replay, all arms (p50 752 ms) | 1043 | 36 | 0.724 | 0.330 | 0.472 | 0.070 | 0.223 |
| clef-flash | replay, all arms (p50 514 ms) | 1043 | 36 | 0.730 | 0.316 | 0.250 | 0.099 | 0.081 |
| gpt-4o | replay, all arms (p50 866 ms) | 891 | 27 | 0.650 | 0.040 | 0.111 | 0.136 | 0.022 |
| gpt-5-mini | replay, all arms (p50 1924 ms) | 1041 | 36 | 0.607 | 0.116 | 0.167 | 0.053 | 0.106 |

Strict = ['bad_args', 'fabricated_tool', 'misread_output', 'schema_violation', 'wrong_tool']; broad adds trajectory_error, unnecessary_call.
Labels: data/judge/pilot2/labels_gpt6luna (single blinded LLM judge; validate against human labels and the second judge).
