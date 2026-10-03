# 01 - Definitions and Taxonomy of Tool-Calling Hallucination

> Provenance note: every paper below was opened (abs page via WebFetch, which returns a model-generated summary of the page, not raw text). Numbers quoted are as reported by that fetch. Verify against the full PDF before citing in the paper. AI behavior is not guaranteed and may vary.
> Dates: research run on 2026-10-03. Several 2026 arXiv IDs (26xx.xxxxx) were found; they were opened and exist, but they are recent and likely un-peer-reviewed unless a venue is stated.

## 1. Existence checks requested

| Claim to check | Result | Evidence |
|---|---|---|
| "Reducing Tool Hallucination via Reliability Alignment" exists | VERIFIED. Xu, Zhu, Pan, Wang, Zhu, Ma, Cao, Chen, Yu. arXiv 2412.04141, ICML 2025 (PMLR v267 xu25ap) | https://arxiv.org/abs/2412.04141 ; https://proceedings.mlr.press/v267/xu25ap.html |
| "Tool hallucination" is an established paper topic | VERIFIED, multiple papers (below): Relign, ToolBeHonest, SimpleToolHalluBench / Reasoning Trap, Amazon "Internal Representations...", HTB / Closed-World Resolution | URLs per row below |
| A general agent-hallucination survey with a tool-use branch exists | VERIFIED: "LLM-based Agents Suffer from Hallucinations" arXiv 2509.18970 (taxonomy + 18 triggering causes) ; AgentHallu 2601.06818 (ICLR 2026 listing, 5 categories / 14 sub-categories incl. Tool-Use) | https://arxiv.org/abs/2509.18970 ; https://arxiv.org/abs/2601.06818 |

## 2. Working definition

Tool-calling hallucination (working definition, synthesised from the sources below) = any agent behaviour in the tool-use loop where the model's emitted call, its decision to call/not call, its description of a call, or its use of a call result is not supported by the tool registry/schema, the user request, the conversation state, or the actual tool output.

Source definitions:
- Relign: hallucinations occur when models "either select inappropriate tools or misuse them" (https://arxiv.org/abs/2412.04141).
- Amazon (Healy et al.): "choose incorrect tools, provide malformed parameters, and exhibit tool bypass behavior by performing simulations instead of invoking specialized tools" (https://arxiv.org/abs/2601.05214).
- Gorilla: a hallucination is when the model "generates an API call that does not exist in the database" (operationalised through AST sub-tree matching) (https://arxiv.org/abs/2305.15334).
- Granite Guardian: function-call hallucination = calls with "syntax or semantic errors based on the user query and available tool", e.g. wrong argument names, invalid values, non-existent parameters (https://www.ibm.com/granite/docs/models/guardian).

## 3. Taxonomy mapped to requested categories

| # | Category | Definition | Papers that name/measure it (verified) | Notes |
|---|---|---|---|---|
| 1 | Wrong tool selection | Real tool exists but is inappropriate for the task | Relign "tool type hallucination" (unrelated tool) https://arxiv.org/abs/2412.04141 ; Amazon "incorrect tool selection" https://arxiv.org/abs/2601.05214 ; ToolCritic (8 error types, listed examples are premature invocation, argument misalignment, misreading outputs) https://arxiv.org/abs/2510.17052 ; Hammer (function-name misleading) https://arxiv.org/abs/2410.04587 | FC-RewardBench: 403 of 1,500 pairs have wrong function name (https://arxiv.org/abs/2509.11963) |
| 2 | Nonexistent / fabricated tools | Name not in the registry | Relign "tool type hallucination ... or fabricates a tool name" ; Gorilla API-not-in-database ; Closed-World Resolution: five-class taxonomy H1-H5 + Hallucinated-Tools Benchmark https://arxiv.org/abs/2609.19425 (322 hallucinations over 10 hosted models; raw-JSON surface 34 vs 3 on the other surface; 675B model ~ same as 7-8B) | I could not extract the exact H1-H5 definitions from the abstract page. "not found" in what I opened. |
| 3 | Wrong / fabricated arguments (parameter / "content" hallucination) | Values not grounded in user text or state; wrong parameter names; omitted required parameters | Relign "tool content hallucination" (fabricated parameter content) ; Amazon "malformed parameters" ; Latent Critic (ungrounded parameters/dates) https://arxiv.org/abs/2608.10430 ; ToolBH "missing parameters" subset (Relign I1-Missing-Parameter subset) | FC-RewardBench: 650 of 1,500 incorrect-parameter-value pairs, the largest single error class |
| 4 | Schema / format violations | Invalid JSON, wrong types, wrong parameter names | Relign "tool format hallucination" (invalid JSON, incorrect parameter names, omitted required params) ; ToolDec removes syntax errors via constrained decoding https://arxiv.org/abs/2310.07075 ; ToolMisuseBench (invalid arguments, interface drift) https://arxiv.org/abs/2604.01508 | This is the one class that constrained decoding addresses directly |
| 5 | Calling a tool when none is needed / when no tool fits | Over-calling; forced use of distractor tools | SimpleToolHalluBench (no-tool and distractor-tool scenarios) https://arxiv.org/abs/2510.22977 ; BFCL irrelevance detection ; ToolFailBench "Unnecessary-Tool-Use" and "Always-Call pattern" https://arxiv.org/abs/2607.04686 ; ToolBH solvability detection https://arxiv.org/abs/2406.20015 | |
| 6 | Skipping a needed call | Answers from parametric memory instead of calling | ToolFailBench "Tool-Skip" ; Amazon "tool bypass" (simulating instead of invoking) | |
| 7 | Fabricating results / claiming a call happened | Asserts values the tool did not return; claims an action that is not in the trace | Amazon "simulating outputs instead of invoking" ; ToolFailBench "Output-Fabrication" ; "Fabrication After Tool Failure" https://arxiv.org/abs/2609.14758 (1,024 items, 14.10% dishonest under deployment-style prompt; 0.0% when payload says "status: error", 45.3% when status ok but data corrupt/empty/truncated; one-sentence retrieval_status prompt reduced 14.10% to 0.87%) ; "Are Your Agents Upward Deceivers?" https://arxiv.org/abs/2512.04864 (200 tasks, 11 LLMs; prompt mitigation only marginal) ; AgentHallu "outcome / action hallucination" labels were reported in a search snippet only: [Unverified] exact label names | |
| 8 | Misreading / misusing tool output (result-grounding) | Ignores, over-trusts, or misreads results | ToolCritic "misinterpretation of tool outputs" ; "Agents Trust Tools Too Much" https://arxiv.org/abs/2609.05587 (corrupted returns adopted at mean >1/3 rate per tool; web search 68%; verification prompts most consistent mitigation) ; Tool-Memory Conflict https://arxiv.org/abs/2601.09760 ; ToolFailBench "Result-Ignore" | |
| 9 | Multi-step / trajectory errors | Error at step k propagates; repeated identical calls; wrong ordering/nesting | Relign "tool timing hallucination" (repeating same tool with identical input/output) ; AgentHallu step-localisation (best model 41.1% overall, 11.6% for tool-use category) https://arxiv.org/abs/2601.06818 ; NESTFUL nested sequences (best GPT-4o full-sequence match 28%) https://arxiv.org/abs/2409.03797 ; AgentProcessBench (1,000 trajectories, 8,509 step labels) https://arxiv.org/abs/2603.14465 ; ToolPRMBench https://arxiv.org/abs/2601.12294 | |

## 4. Taxonomy sources in detail

### 4.1 Relign (Xu et al., ICML 2025) - https://arxiv.org/abs/2412.04141
- Two top-level classes: Tool Selection Hallucination (subtypes: tool type, tool timing) and Tool Usage Hallucination (subtypes: tool format, tool content).
- Benchmark RelyToolBench built on StableToolBench; subsets I1-Instruction, I1-Missing-Parameter, I1-Unmatched-Tools. Training: 10,000 samples from ToolBench split 4,000/3,000/3,000.
- Metrics: Tool Hallucination Rate, Benefit-Cost Utility (+20 success, -10 hallucinated answer, -1 per excess call), Benefit-Cost Ratio.
- Method: SFT then DPO, with new "indecisive" actions (ChangeTools, TalkToUser).
- Reported: Llama 3.1 8B hallucination rate 61.5% to 18.8% overall; utility 7.0 to 12.4; 0% hallucination rate on UnmatchedTools subset (as reported by authors).
- Limitations stated: only Llama 3.1 8B, only StableToolBench.

### 4.2 ToolBeHonest (ToolBH) - https://arxiv.org/abs/2406.20015
- 700 samples, 7 tasks, 3 levels (solvability detection, solution planning, missing-tool analysis), 3 scenarios (missing necessary tools, potential tools, limited-functionality tools). CC BY 4.0. Gemini-1.5-Pro 45.3 and GPT-4o 37.0 of 100.

### 4.3 Amazon "Internal Representations as Indicators of Hallucinations in Agent Tool Selection" - https://arxiv.org/abs/2601.05214
- Three categories: incorrect tool selection, malformed parameters, tool bypass. Reports up to 86.4% detection accuracy from internal representations in the same forward pass.

### 4.4 Agent-level taxonomies
- Agent hallucination survey https://arxiv.org/abs/2509.18970 : taxonomy by workflow stage, 18 triggering causes, detection and mitigation review (contents beyond the abstract not extracted).
- AgentHallu https://arxiv.org/abs/2601.06818 : 693 trajectories, 7 frameworks, 5 categories (Planning, Retrieval, Reasoning, Human-Interaction, Tool-Use), 14 sub-categories, human step-level annotations; 13 models evaluated.

### 4.5 Error-critique taxonomies
- ToolCritic https://arxiv.org/abs/2510.17052 : eight tool-calling error types (full list not extracted from abstract page).
- CRITICTOOL https://arxiv.org/abs/2506.13977 : critique benchmark for tool-calling error scenarios (error categories "analyzed", exact list not extracted). CC-BY 4.0 for resources.

## 5. Gaps in taxonomy coverage [Inference]
- [Inference] No single paper found covers all 9 categories; the union is assembled above.
- "Not found": a taxonomy that explicitly separates "call correct but result wrong because the tool/API itself errored" from model-caused hallucination. ToolFailBench and Fabrication-After-Tool-Failure touch this on the output side.
