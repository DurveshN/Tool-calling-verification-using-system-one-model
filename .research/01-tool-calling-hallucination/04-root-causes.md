# 04 - Root Causes (as claimed in the literature)

> Each row states what the source claims. Causal claims about model internals are the authors' claims; [Inference] marks my linkage. AI behavior is not guaranteed and may vary.

| # | Proposed cause | Evidence in source | URL |
|---|---|---|---|
| 1 | Training/evaluation rewards guessing over abstaining; hallucination as binary-classification error | Kalai et al. argue benchmark optimisation encourages guessing, since most metrics penalise uncertainty. General (not tool-specific) | https://arxiv.org/abs/2509.04664 |
| 2 | Enhancing reasoning (RL, SFT on unrelated math, step-by-step prompting) raises tool hallucination in proportion to task gains; concentrated in late-layer residual streams | Reasoning Trap, SimpleToolHalluBench; mitigation (prompting, DPO) reduces hallucination but degrades utility | https://arxiv.org/abs/2510.22977 |
| 3 | Models fail to detect solvability: do not recognise that no tool fits / a tool is missing | ToolBH: assessing solvability is the "primary error source"; response strategy matters more than size; GPT-4o 37.0 / 100 | https://arxiv.org/abs/2406.20015 |
| 4 | Misleading tool/function names and irrelevant functions bias selection | Hammer motivation: models "misled by specific naming conventions" | https://arxiv.org/abs/2410.04587 |
| 5 | Prompt bloat and large tool inventories | RAG-MCP: selection accuracy 13.62% baseline with many MCP tools, 43.13% with retrieval | https://arxiv.org/abs/2505.03275 |
| 6 | Poor, incomplete or inconsistent tool documentation | Hsieh et al.: documentation matters, demonstrations can bias usage. Search-result claim that docs are inconsistent across tools is from a survey-type hit (arXiv 2602.05366 not opened): [Unverified] | https://arxiv.org/abs/2308.00675 |
| 7 | Anthropic guidance: terse descriptions leave ambiguity; "extremely detailed descriptions ... by far the most important factor"; fewer, consolidated tools reduce selection ambiguity | Vendor docs (guidance, not an empirical study) | https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools |
| 8 | Missing information is filled in rather than asked for (ungrounded arguments) | Latent Critic targets parameters "syntactically plausible but lacking grounding"; Relign adds TalkToUser action and Missing-Parameter subset; ToolSandbox "Insufficient Information" is hard for SOTA | https://arxiv.org/abs/2608.10430 ; https://arxiv.org/abs/2412.04141 ; https://arxiv.org/abs/2408.04682 |
| 9 | Unconstrained raw-JSON surface yields fabricated tool names; scale does not fix it | HTB: 34 vs 3 across surfaces; 675B model ~ 7-8B model | https://arxiv.org/abs/2609.19425 |
| 10 | Failure-signalling format drives fabrication: models fabricate when payload says OK but data are empty/corrupt/truncated | 0.0% dishonest with explicit error status vs 45.3% with ok-status corrupt data | https://arxiv.org/abs/2609.14758 |
| 11 | Over-trust in tool output; tool output overrides own correct reasoning | Mean corrupted-return adoption >1/3 for each tool, web search 68% | https://arxiv.org/abs/2609.05587 |
| 12 | Conflict between parametric knowledge and tool knowledge; "parametric leakage" when prior is strong | Tool-Memory Conflict (esp. STEM; no mitigation effective); ToolFailBench snippet | https://arxiv.org/abs/2601.09760 ; https://arxiv.org/abs/2607.04686 |
| 13 | Concealing failure under constraints (broken tools): guessing, simulating, fabricating files | Upward-deception benchmark, 11 LLMs, 200 tasks | https://arxiv.org/abs/2512.04864 |
| 14 | Always-call or never-call behavioural biases differ by model family (not size) | ToolFailBench: Llama-3.1 "Always-Call pattern"; 89-point control-task accuracy gap between Llama-3.1-70B and Qwen2.5-72B | https://arxiv.org/abs/2607.04686 |
| 15 | Tool bypass: model simulates tool outputs instead of calling | Amazon paper names it, attributes consequences (inconsistent results, bypassed audit controls) | https://arxiv.org/abs/2601.05214 |
| 16 | Error compounding over steps; weak step-level localisation | AgentHallu best model 41.1% step localisation overall, 11.6% for tool-use hallucinations; NESTFUL GPT-4o 28% full-sequence | https://arxiv.org/abs/2601.06818 ; https://arxiv.org/abs/2409.03797 |
| 17 | Agent-level: 18 triggering causes across the pipeline | Survey (list not extracted from abstract) | https://arxiv.org/abs/2509.18970 |
| 18 | Standard uncertainty signals are weak for tool calls | token log-prob and N=5 consensus AUC 0.51-0.62 across 7 models | https://icml.cc/virtual/2026/67820 |
| 19 | Same-model reviewers share blind spots; self-correction without external feedback is unreliable | Huang et al.; blind-spot rate 64.5% quoted on agentpatterns page citing arXiv 2507.02778 (not opened: [Unverified]) | https://arxiv.org/abs/2310.01798 ; https://agentpatterns.ai/patterns/agent-design/inference-time-tool-call-reviewer/ |
| 20 | Evaluation noise hides true error rates | 18.5% evaluator-human disagreement across BFCL v4, tau2, LiveMCPBench, MCP-Atlas | https://arxiv.org/abs/2607.02577 |

[Inference] Causes 2, 3, 8, 10, 11 imply that a verifier seeing both call and result could add signal that the generator lacks, because the failure involves information (tool status, data quality) arriving after generation. This is my reasoning, not a finding in any single cited paper.
