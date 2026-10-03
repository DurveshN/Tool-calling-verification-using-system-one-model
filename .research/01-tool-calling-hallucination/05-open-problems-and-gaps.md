# 05 - Open Problems, Gaps, and Evaluation Metrics

> Gaps are listed with the citation that supports the existence of the gap. "[Inference]" marks my own reading. This file does not judge the user's idea. AI behavior is not guaranteed and may vary.

## 1. Gaps tied to citations

| # | Gap | Supporting citation | Why it matters for a call+result verifier |
|---|---|---|---|
| G1 | Verifiers mostly score the call before execution; result-side verification (call + returned result) is rare in the work I opened | Reinforced Agent reviews "provisional" calls pre-dispatch (https://arxiv.org/abs/2604.27233); Latent Critic intercepts pre-execution (https://arxiv.org/abs/2608.10430); ToolRM input excludes results (https://arxiv.org/abs/2509.11963). ToolCritic names output misinterpretation but timing is unclear (https://arxiv.org/abs/2510.17052) | Result-grounding errors (fabrication after failure 14.10%, corrupted-return adoption >1/3) occur after the call: https://arxiv.org/abs/2609.14758 ; https://arxiv.org/abs/2609.05587 |
| G2 | Scalar/probabilistic verifier output fed back into the agent context is not established; existing feedback is textual or a hard block | Reinforced Agent (approve/reject/revise + text); IDK filter replaces call with abstention (https://arxiv.org/abs/2607.04034); Cleanlab gives a score but leaves action to developer (https://help.cleanlab.ai/tlm/tutorials/tlm_tool_calls/) | Whether an LLM uses a number appropriately is an open empirical question [Inference] |
| G3 | Calibration of verifiers for tool calls under distribution shift | MICE calibrates same-model confidence (https://arxiv.org/abs/2504.20168); Latent Critic OOD AUROC drop 0.966 to 0.925; probe OOD 0.782 to 0.616 (numbers from blog summary https://codex.danielvaughan.com/2026/08/17/actionable-hallucination-detection-latent-critic-specification-grounding-codex-cli-posttooluse-hooks-guardian/) | Probability signal is only useful if calibrated |
| G4 | Harm from false alarms (verifier degrading correct calls) is under-reported | Reinforced Agent introduces harmfulness metric (https://arxiv.org/abs/2604.27233); pattern page cites ~98% to 57% collapse case (https://agentpatterns.ai/patterns/agent-design/inference-time-tool-call-reviewer/, secondary); Huang et al. self-correction can degrade (https://arxiv.org/abs/2310.01798) | Must report helpfulness AND harmfulness |
| G5 | Latency/cost of per-call review | External judge 884 ms vs <10 ms latent critic (blog-reported); synchronous review "doubles round-trips" (pattern page) | Motivates "fast System One" framing; quantify added latency per call |
| G6 | Small-model verifier training data for incorrect calls is limited to BFCL-derived single-turn pairs and a few step-level benchmarks | FC-RewardBench 1,500 pairs (https://arxiv.org/abs/2509.11963); ToolPRMBench and AgentProcessBench (https://arxiv.org/abs/2601.12294 ; https://arxiv.org/abs/2603.14465) | Results-bearing negatives (call + result) are not the main format [Inference] |
| G7 | Reward/verifier models biased toward calling over abstaining | ToolRM irrelevance errors 185 to 210 (https://arxiv.org/abs/2509.11963) | Verifier must handle "no call needed" |
| G8 | Best detector depends on model scale; no universal approach | https://icml.cc/virtual/2026/67820 | A black-box separate verifier avoids white-box dependence [Inference] |
| G9 | Generalisation of tool-hallucination mitigation beyond one model/benchmark | Relign limitations: only Llama 3.1 8B and StableToolBench (https://arxiv.org/abs/2412.04141) | Evaluate across main-model families and benchmarks |
| G10 | Reasoning models hallucinate more with tools, and mitigation costs utility | https://arxiv.org/abs/2510.22977 | Test with reasoning-mode main models |
| G11 | Multi-step localisation of tool-use errors is very weak | AgentHallu 11.6% tool-use step localisation (https://arxiv.org/abs/2601.06818) | Per-step verifier is a natural localiser |
| G12 | Benchmark validity and variance | https://arxiv.org/abs/2607.02577 (18.5% misalignment; 18.9-pt run spread in LiveMCPBench) | Need repeated runs, confidence intervals |
| G13 | Verifier independence: same-base reviewers inherit blind spots | agentpatterns page (cites arXiv 2507.02778, not opened); Huang et al. | Use a different model family/size for the verifier; test correlation of errors |
| G14 | MCP / multi-registry settings reveal new hallucinations in frontier models | HTB: 154 additional hallucinations in MCP tests (https://arxiv.org/abs/2609.19425) | |
| G15 | Prompt-only mitigation is marginal for deception/fabrication under constraint | https://arxiv.org/abs/2512.04864 ; but status-flag prompt worked on one set (https://arxiv.org/abs/2609.14758) | Compare verifier vs prompt baselines |

## 2. Evaluation metrics used in the field

| Metric | Definition (as used in sources) | Where |
|---|---|---|
| AST accuracy | Parse call to AST; match function name, required params, types, values against ground truth | BFCL https://gorilla.cs.berkeley.edu/blogs/8_berkeley_function_calling_leaderboard.html ; Gorilla |
| Executable accuracy | Run the call; exact match / real-time (+-20% numeric) / structure match | BFCL |
| Relevance / irrelevance detection | Model must produce no call when no function fits (irrelevance) and a call when it does (relevance) | BFCL |
| Hallucination rate (API) | Fraction of generated calls naming an API not in the database (AST sub-tree matching) | Gorilla https://arxiv.org/abs/2305.15334 |
| Tool Hallucination Rate | Proportion of hallucinated tool calls per task, averaged | Relign https://arxiv.org/abs/2412.04141 |
| Benefit-Cost Utility / Ratio | +20 success, -10 hallucinated answer, -1 per excess call, floor -10; ratio = success / avg tool cost | Relign |
| Pass Rate / Win Rate | Task completion within call limit; LLM-judged preference vs reference | ToolEval https://github.com/OpenBMB/ToolBench |
| pass^k | Probability all k trials succeed (reliability) | tau-bench https://arxiv.org/abs/2406.12045 |
| Full-sequence match, partial match, win rate, F1 on names/params | Nested call sequences | NESTFUL https://arxiv.org/abs/2409.03797 |
| Milestone / minefield scoring | Intermediate and final state checks | ToolSandbox https://arxiv.org/abs/2408.04682 |
| Reward-model accuracy (pairwise); Best-of-N gain; Pearson with downstream accuracy | | ToolRM https://arxiv.org/abs/2509.11963 (0.84 Pearson FC-RewardBench vs task accuracy) |
| AUROC / AUC, accuracy of detection | Detector vs ground truth call correctness | Latent Critic, Noel et al., Amazon |
| Expected calibration error (smoothed) and expected tool-calling utility | Calibration and utility under risk levels | MICE https://arxiv.org/abs/2504.20168 |
| Helpfulness / Harmfulness | % of base-agent errors corrected / % of correct responses degraded | Reinforced Agent https://arxiv.org/abs/2604.27233 |
| Step localisation accuracy | Identify first erroneous step | AgentHallu https://arxiv.org/abs/2601.06818 |
| Clean Tool-Use Rate; Tool-Skip / Result-Ignore / Output-Fabrication / Unnecessary-Use rates | | ToolFailBench https://arxiv.org/abs/2607.04686 |
| Timely abstention recall | | Agentic Abstention https://arxiv.org/abs/2606.28733 |
| Dishonesty rate | Assert unsupported value after tool failure | https://arxiv.org/abs/2609.14758 |
| Corrupted-return adoption rate | | https://arxiv.org/abs/2609.05587 |

## 3. Suggested metric set for a verifier paper [Inference]
Detection: AUROC, AUPRC, ECE/Brier, precision at fixed recall of error. System: downstream task success delta, helpfulness, harmfulness, added latency per call and per task, extra tokens. Subgroup: by taxonomy category (see 01 file).
