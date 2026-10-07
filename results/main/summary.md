# Analysis: phase `main`

Labelled calls: 21784 / 21784

## 1. Hallucination by arm (judge labels)

| arm | tasks passed | calls | strict halluc. | strict / call | broad errors | broad / call | false/unsupported claims | final claim false |
|---|---|---|---|---|---|---|---|---|
| A | 22/87 | 8430 | 331 | 0.039 | 1925 | 0.228 | 105 | 19 |
| B | 31/87 | 7400 | 218 | 0.029 | 2193 | 0.296 | 102 | 22 |
| C | 31/87 | 5954 | 196 | 0.033 | 1407 | 0.236 | 86 | 18 |

## 2. Strict hallucinations / calls, per task

| task | A | B | C |
|---|---|---|---|
| adaptive-rejection-sampler | 11/244 | 6/199 | 0/97 |
| bn-fit-modify | 2/26 | 2/37 | 1/28 |
| break-filter-js-from-html | 3/8 | 0/3 | 0/2 |
| build-cython-ext | 3/71 | 0/72 | 0/70 |
| build-pmars | 2/42 | 0/27 | 0/26 |
| build-pov-ray | 38/677 | 4/83 | 2/61 |
| caffe-cifar-10 | 0/20 | 1/48 | 1/33 |
| cancel-async-tasks | 2/11 | 0/7 | 1/11 |
| chess-best-move | 2/22 | 0/6 | 1/158 |
| circuit-fibsqrt | 3/32 | 7/818 | 8/159 |
| cobol-modernization | 5/30 | 11/130 | 3/111 |
| code-from-image | 0/6 | 0/6 | 0/6 |
| compile-compcert | 1/50 | 4/41 | 3/35 |
| configure-git-webserver | 0/18 | 0/2 | 3/25 |
| constraints-scheduling | 2/13 | 1/12 | 1/13 |
| count-dataset-tokens | 0/18 | 0/14 | 1/15 |
| crack-7z-hash | 3/43 | 1/37 | 2/48 |
| custom-memory-heap-crash | 3/28 | 0/31 | 19/318 |
| db-wal-recovery | 0/24 | 3/20 | 2/20 |
| distribution-search | 0/12 | 2/219 | 0/34 |
| dna-assembly | 5/68 | 2/147 | 3/123 |
| dna-insert | 9/31 | 6/32 | 1/26 |
| extract-elf | 1/15 | 0/15 | 1/16 |
| extract-moves-from-video | 4/101 | 5/93 | 5/186 |
| feal-differential-cryptanalysis | 55/484 | 31/258 | 0/22 |
| feal-linear-cryptanalysis | 5/79 | 7/109 | 1/49 |
| filter-js-from-html | 0/19 | 0/13 | 0/15 |
| financial-document-processor | 3/38 | 0/23 | 0/49 |
| fix-code-vulnerability | 0/29 | 0/18 | 0/21 |
| fix-git | 0/22 | 0/20 | 0/20 |
| fix-ocaml-gc | 12/309 | 3/145 | 4/96 |
| gcode-to-text | 0/94 | 3/43 | 0/22 |
| git-leak-recovery | 0/18 | 1/11 | 1/17 |
| git-multibranch | 2/93 | 1/28 | 2/43 |
| gpt2-codegolf | 4/61 | 4/133 | 0/16 |
| headless-terminal | 0/14 | 0/14 | 0/13 |
| hf-model-inference | 0/12 | 1/18 | 0/14 |
| install-windows-3.11 | 0/16 | 2/26 | 2/18 |
| kv-store-grpc | 1/15 | 0/16 | 1/18 |
| large-scale-text-editing | 5/92 | 1/22 | 0/14 |
| largest-eigenval | 0/38 | 0/23 | 2/39 |
| llm-inference-batching-scheduler | 6/588 | 0/80 | 2/33 |
| log-summary-date-ranges | 0/2 | 0/2 | 0/11 |
| mailman | 3/26 | 0/17 | 10/51 |
| make-doom-for-mips | 8/210 | 8/114 | 15/243 |
| make-mips-interpreter | 19/167 | 14/100 | 14/168 |
| mcmc-sampling-stan | 0/19 | 0/24 | 0/40 |
| merge-diff-arc-agi-task | 1/33 | 0/56 | 1/27 |
| model-extraction-relu-logits | 1/54 | 0/20 | 3/96 |
| modernize-scientific-stack | 0/10 | 0/13 | 0/14 |
| mteb-leaderboard | 2/20 | 2/179 | 0/64 |
| mteb-retrieve | 0/8 | 0/6 | 0/10 |
| multi-source-data-merger | 0/15 | 1/14 | 1/14 |
| nginx-request-logging | 0/9 | 0/23 | 0/15 |
| openssl-selfsigned-cert | 0/10 | 0/13 | 1/14 |
| overfull-hbox | 7/228 | 1/15 | 1/90 |
| password-recovery | 0/53 | 1/29 | 4/41 |
| path-tracing | 1/65 | 0/78 | 6/184 |
| path-tracing-reverse | 6/548 | 5/357 | 8/415 |
| polyglot-c-py | 8/405 | 3/269 | 1/312 |
| polyglot-rust-c | 18/395 | 2/258 | 1/326 |
| portfolio-optimization | 0/17 | 0/16 | 0/17 |
| protein-assembly | 6/217 | 2/129 | 2/453 |
| prove-plus-comm | 0/17 | 0/13 | 0/14 |
| pypi-server | 0/21 | 0/17 | 0/22 |
| pytorch-model-cli | 0/21 | 2/32 | 1/45 |
| pytorch-model-recovery | 1/14 | 1/13 | 0/6 |
| query-optimize | 0/12 | 1/15 | 0/24 |
| raman-fitting | 2/32 | 1/26 | 1/19 |
| regex-chess | 0/15 | 0/18 | 0/16 |
| regex-log | 11/77 | 0/14 | 1/8 |
| reshard-c4-data | 0/16 | 0/24 | 0/26 |
| rstan-to-pystan | 2/37 | 3/37 | 4/30 |
| sam-cell-seg | 0/12 | 0/28 | 1/22 |
| sanitize-git-repo | 0/13 | 0/15 | 0/14 |
| schemelike-metacircular-eval | 12/152 | 20/407 | 29/496 |
| sparql-university | 1/17 | 0/8 | 0/9 |
| sqlite-db-truncate | 1/21 | 1/17 | 2/28 |
| sqlite-with-gcov | 2/8 | 1/10 | 2/9 |
| torch-pipeline-parallelism | 0/15 | 2/28 | 2/67 |
| torch-tensor-parallelism | 0/13 | 0/9 | 0/7 |
| train-fasttext | 3/22 | 3/24 | 1/16 |
| tune-mjcf | 9/205 | 11/124 | 10/140 |
| video-processing | 4/39 | 17/738 | 0/28 |
| vulnerable-secret | 0/9 | 0/15 | 0/14 |
| winning-avg-corewars | 10/1445 | 0/865 | 0/94 |
| write-compressor | 1/55 | 7/72 | 1/55 |

## 3. Label distribution

| label | A | B | C |
|---|---|---|---|
| bad_args | 257 | 187 | 164 |
| fabricated_tool | 6 | 7 | 5 |
| misread_output | 15 | 12 | 17 |
| none | 6505 | 5207 | 4547 |
| schema_violation | 44 | 5 | 5 |
| trajectory_error | 1172 | 1598 | 705 |
| unnecessary_call | 422 | 377 | 506 |
| wrong_tool | 9 | 7 | 5 |

## 4. Critic quality vs judge labels (positive = strict hallucination; score = 1 − P(grounded_call))

| critic | source | n | positives | AUROC | ECE | recall@0.5 | precision@0.5 | false-alarm rate |
|---|---|---|---|---|---|---|---|---|
| gpt-5-mini | online, arm B | 7229 | 105 | 0.598 | 0.116 | 0.181 | 0.033 | 0.077 |
| clef | online, arm C | 5833 | 122 | 0.768 | 0.299 | 0.434 | 0.078 | 0.110 |
| clef | replay, all arms (p50 668 ms) | 21784 | 745 | 0.799 | 0.294 | 0.518 | 0.123 | 0.131 |
| clef-flash | replay, all arms (p50 359 ms) | 21784 | 745 | 0.600 | 0.305 | 0.083 | 0.031 | 0.093 |
| gpt-4o | replay, all arms (p50 1271 ms) | 3000 | 99 | 0.666 | 0.040 | 0.040 | 0.074 | 0.017 |
| gpt-5-mini | replay, all arms (p50 1770 ms) | 21783 | 745 | 0.710 | 0.101 | 0.294 | 0.122 | 0.075 |

Strict = ['bad_args', 'fabricated_tool', 'misread_output', 'schema_violation', 'wrong_tool']; broad adds trajectory_error, unnecessary_call.
Labels: data/judge/main/labels_gpt6luna (single blinded LLM judge; validate against human labels and the second judge).
