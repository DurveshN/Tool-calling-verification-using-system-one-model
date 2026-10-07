# Analysis: phase `main`

Labelled calls: 19706 / 21784

**Incomplete labels:**
- 6c807349 (A adaptive-rejection-sampler): 120/244 calls labelled
- 9c0d7248 (A polyglot-rust-c): 223/395 calls labelled
- effca077 (B schemelike-metacircular-eval): 259/407 calls labelled
- 660f2855 (C raman-fitting): 0/19 calls labelled
- cd01c05c (C make-doom-for-mips): 183/243 calls labelled
- c6bf4bb9 (C dna-insert): 0/26 calls labelled
- b638c561 (C extract-elf): 0/16 calls labelled
- e6462197 (B extract-moves-from-video): 0/93 calls labelled
- c709167c (B compile-compcert): 0/41 calls labelled
- 8726d2aa (A sparql-university): 0/17 calls labelled
- 733b83a0 (A make-doom-for-mips): 80/210 calls labelled
- 9a7c11f3 (B make-mips-interpreter): 47/100 calls labelled
- 01fdcad0 (B circuit-fibsqrt): 629/818 calls labelled
- dc017621 (B write-compressor): 0/72 calls labelled
- 67aac5e7 (A git-multibranch): 0/93 calls labelled
- 2aa59a72 (B dna-assembly): 74/147 calls labelled
- ca41437f (B git-leak-recovery): 0/11 calls labelled
- 2c0260e7 (C bn-fit-modify): 0/28 calls labelled
- 951052a1 (B path-tracing-reverse): 307/357 calls labelled
- 2ac57431 (A raman-fitting): 0/32 calls labelled
- a8fd4396 (B feal-differential-cryptanalysis): 128/258 calls labelled
- 37797818 (B build-pov-ray): 10/83 calls labelled
- bbcb755c (A polyglot-c-py): 260/405 calls labelled
- 6bd27219 (A make-mips-interpreter): 89/167 calls labelled
- eeb73213 (A tune-mjcf): 0/205 calls labelled

## 1. Hallucination by arm (judge labels)

| arm | tasks passed | calls | strict halluc. | strict / call | broad errors | broad / call | false/unsupported claims | final claim false |
|---|---|---|---|---|---|---|---|---|
| A | 22/87 | 7434 | 283 | 0.038 | 1679 | 0.226 | 96 | 16 |
| B | 31/87 | 6467 | 151 | 0.023 | 1998 | 0.309 | 80 | 20 |
| C | 31/87 | 5805 | 188 | 0.032 | 1392 | 0.240 | 81 | 16 |

## 2. Strict hallucinations / calls, per task

| task | A | B | C |
|---|---|---|---|
| adaptive-rejection-sampler | 6/120 | 6/199 | 0/97 |
| bn-fit-modify | 2/26 | 2/37 | – |
| break-filter-js-from-html | 3/8 | 0/3 | 0/2 |
| build-cython-ext | 3/71 | 0/72 | 0/70 |
| build-pmars | 2/42 | 0/27 | 0/26 |
| build-pov-ray | 38/677 | 0/10 | 2/61 |
| caffe-cifar-10 | 0/20 | 1/48 | 1/33 |
| cancel-async-tasks | 2/11 | 0/7 | 1/11 |
| chess-best-move | 2/22 | 0/6 | 1/158 |
| circuit-fibsqrt | 3/32 | 0/629 | 8/159 |
| cobol-modernization | 5/30 | 11/130 | 3/111 |
| code-from-image | 0/6 | 0/6 | 0/6 |
| compile-compcert | 1/50 | – | 3/35 |
| configure-git-webserver | 0/18 | 0/2 | 3/25 |
| constraints-scheduling | 2/13 | 1/12 | 1/13 |
| count-dataset-tokens | 0/18 | 0/14 | 1/15 |
| crack-7z-hash | 3/43 | 1/37 | 2/48 |
| custom-memory-heap-crash | 3/28 | 0/31 | 19/318 |
| db-wal-recovery | 0/24 | 3/20 | 2/20 |
| distribution-search | 0/12 | 2/219 | 0/34 |
| dna-assembly | 5/68 | 2/74 | 3/123 |
| dna-insert | 9/31 | 6/32 | – |
| extract-elf | 1/15 | 0/15 | – |
| extract-moves-from-video | 4/101 | – | 5/186 |
| feal-differential-cryptanalysis | 55/484 | 4/128 | 0/22 |
| feal-linear-cryptanalysis | 5/79 | 7/109 | 1/49 |
| filter-js-from-html | 0/19 | 0/13 | 0/15 |
| financial-document-processor | 3/38 | 0/23 | 0/49 |
| fix-code-vulnerability | 0/29 | 0/18 | 0/21 |
| fix-git | 0/22 | 0/20 | 0/20 |
| fix-ocaml-gc | 12/309 | 3/145 | 4/96 |
| gcode-to-text | 0/94 | 3/43 | 0/22 |
| git-leak-recovery | 0/18 | – | 1/17 |
| git-multibranch | – | 1/28 | 2/43 |
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
| make-doom-for-mips | 2/80 | 8/114 | 11/183 |
| make-mips-interpreter | 16/89 | 6/47 | 14/168 |
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
| path-tracing-reverse | 6/548 | 5/307 | 8/415 |
| polyglot-c-py | 4/260 | 3/269 | 1/312 |
| polyglot-rust-c | 2/223 | 2/258 | 1/326 |
| portfolio-optimization | 0/17 | 0/16 | 0/17 |
| protein-assembly | 6/217 | 2/129 | 2/453 |
| prove-plus-comm | 0/17 | 0/13 | 0/14 |
| pypi-server | 0/21 | 0/17 | 0/22 |
| pytorch-model-cli | 0/21 | 2/32 | 1/45 |
| pytorch-model-recovery | 1/14 | 1/13 | 0/6 |
| query-optimize | 0/12 | 1/15 | 0/24 |
| raman-fitting | – | 1/26 | – |
| regex-chess | 0/15 | 0/18 | 0/16 |
| regex-log | 11/77 | 0/14 | 1/8 |
| reshard-c4-data | 0/16 | 0/24 | 0/26 |
| rstan-to-pystan | 2/37 | 3/37 | 4/30 |
| sam-cell-seg | 0/12 | 0/28 | 1/22 |
| sanitize-git-repo | 0/13 | 0/15 | 0/14 |
| schemelike-metacircular-eval | 12/152 | 16/259 | 29/496 |
| sparql-university | – | 0/8 | 0/9 |
| sqlite-db-truncate | 1/21 | 1/17 | 2/28 |
| sqlite-with-gcov | 2/8 | 1/10 | 2/9 |
| torch-pipeline-parallelism | 0/15 | 2/28 | 2/67 |
| torch-tensor-parallelism | 0/13 | 0/9 | 0/7 |
| train-fasttext | 3/22 | 3/24 | 1/16 |
| tune-mjcf | – | 11/124 | 10/140 |
| video-processing | 4/39 | 17/738 | 0/28 |
| vulnerable-secret | 0/9 | 0/15 | 0/14 |
| winning-avg-corewars | 10/1445 | 0/865 | 0/94 |
| write-compressor | 1/55 | – | 1/55 |

## 3. Label distribution

| label | A | B | C |
|---|---|---|---|
| bad_args | 210 | 128 | 157 |
| fabricated_tool | 6 | 6 | 5 |
| misread_output | 14 | 9 | 16 |
| none | 5755 | 4469 | 4413 |
| schema_violation | 44 | 3 | 5 |
| trajectory_error | 1010 | 1515 | 698 |
| unnecessary_call | 386 | 332 | 506 |
| wrong_tool | 9 | 5 | 5 |

## 4. Critic quality vs judge labels (positive = strict hallucination; score = 1 − P(grounded_call))

| critic | source | n | positives | AUROC | ECE | recall@0.5 | precision@0.5 | false-alarm rate |
|---|---|---|---|---|---|---|---|---|
| gpt-5-mini | online, arm B | 6360 | 81 | 0.612 | 0.117 | 0.210 | 0.034 | 0.077 |
| clef | online, arm C | 5686 | 114 | 0.773 | 0.301 | 0.456 | 0.077 | 0.112 |
| clef | replay, all arms (p50 669 ms) | 19695 | 622 | 0.796 | 0.295 | 0.514 | 0.115 | 0.129 |
| clef-flash | replay, all arms (p50 353 ms) | 19694 | 622 | 0.605 | 0.307 | 0.090 | 0.030 | 0.096 |
| gpt-5-mini | replay, all arms (p50 1774 ms) | 15676 | 488 | 0.709 | 0.095 | 0.273 | 0.117 | 0.066 |

Strict = ['bad_args', 'fabricated_tool', 'misread_output', 'schema_violation', 'wrong_tool']; broad adds trajectory_error, unnecessary_call.
Labels: data/judge/main/labels_gpt6luna (single blinded LLM judge; validate against human labels and the second judge).
