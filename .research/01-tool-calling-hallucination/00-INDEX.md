# Tool-Calling Hallucination: Research Knowledge Base

Prepared 2026-10-03 for the paper on a "System One" per-call verifier whose probability signal is passed to the main LLM. This is background evidence only; it does not evaluate the idea. Fetched pages were read via WebFetch summaries, so confirm details in full PDFs before citing. AI behavior is not guaranteed and may vary.

## Contents
| File | Content |
|---|---|
| 01-definitions-taxonomy.md | Definitions, 9-category taxonomy mapped to papers, existence checks |
| 02-benchmarks-datasets.md | Table of ~28 benchmarks/datasets with size, error labels, license, URL |
| 03-mitigation-methods.md | Novelty-risk table first, then 7 mitigation families |
| 04-root-causes.md | 20 causes claimed in the literature |
| 05-open-problems-and-gaps.md | 15 gaps with citations; metrics catalogue |
| 06-references.md | Reference list with URL and open status |

## Executive summary
- "Reducing Tool Hallucination via Reliability Alignment" (Relign) is real: ICML 2025, arXiv 2412.04141. It defines selection (type, timing) and usage (format, content) hallucinations, and reports hallucination 61.5% to 18.8% on Llama 3.1 8B only. https://arxiv.org/abs/2412.04141
- Tool hallucination is an established sub-field with other named benchmarks: ToolBeHonest (700 samples), SimpleToolHalluBench, Hallucinated-Tools Benchmark, ToolFailBench, AgentHallu.
- The taxonomy is fragmented. No single paper covers all nine categories (selection, fabricated tool, fabricated args, format, unnecessary call, skipped call, fabricated result, result misuse, trajectory error); 01 file assembles the union.
- Closest prior work to the user's idea: Reinforced Agent (separate reviewer feeding feedback per call, BFCL +5.5% irrelevance, tau2 +7.1%, helpfulness/harmfulness metrics) https://arxiv.org/abs/2604.27233 ; Latent Critic (LoRA critic with NL feedback, AUROC 0.966) https://arxiv.org/abs/2608.10430 ; IDK Filter https://arxiv.org/abs/2607.04034 ; ToolCritic https://arxiv.org/abs/2510.17052.
- In what I opened, I did not find a paper combining a separate small model + call AND result + calibrated probability + injection of that scalar into the main agent's next step with downstream measurement. [Inference] Absence in my search is not proof of absence.
- Scalar reward models for calls exist (two different "ToolRM" papers, 1.7B-14B and 4B/8B) but are used for Best-of-N, filtering, RL, and critique, not run-time probability feedback; IBM ToolRM scores sequences and shows a bias toward calling over abstaining.
- Standard uncertainty signals are weak for tool calls: token log-probs and N=5 consensus gave AUC 0.51-0.62 on 7 models (ICML 2026); white-box probes help but best method depends on model scale.
- Risk of verifier harm is documented: pattern page cites a ~98% to 57% collapse case (secondary source) and same-model reviewers sharing blind spots; Reinforced Agent introduces helpfulness vs harmfulness. Any verifier paper should report both.
- Schema validation / constrained decoding (ToolDec, OpenAI strict, Anthropic strict tool use) handles format and nonexistent-tool classes but not semantically wrong yet valid calls.
- Result-side failures are large: 14.10% dishonest responses after tool failure (0.0% with explicit error status, 45.3% when status OK but data corrupt), and corrupted tool returns adopted at >1/3 mean rate (68% for web search). These are errors a call+result verifier can see and a pre-call critic cannot.
- Root-cause literature: reasoning enhancement raises tool hallucination (Reasoning Trap), poor solvability detection (ToolBH), misleading names, too many tools (RAG-MCP: 13.62% to 43.13%), ungrounded filling of missing arguments, and training/evaluation incentives to guess.
- Harness mechanisms already exist: Claude Code PostToolUse hooks can inject `additionalContext` next to a tool result and call a model via prompt/agent hooks. https://code.claude.com/docs/en/hooks
- Best benchmarks for evaluating a tool-call verifier: FC-RewardBench (paired correct/incorrect, 1,500), ToolPRMBench and AgentProcessBench (step labels), BFCL v3/v4 and tau2-bench (downstream effect), ToolFailBench and Fabrication-After-Tool-Failure (result-side errors).
- Evaluation noise is large: 18.5% evaluator-human disagreement across BFCL v4, tau2-Bench, LiveMCPBench, MCP-Atlas; one benchmark showed an 18.9-point run-to-run spread. https://arxiv.org/abs/2607.02577
- Many 2026 papers are recent preprints; several facts come only from search snippets and are marked [Unverified] in the files.
