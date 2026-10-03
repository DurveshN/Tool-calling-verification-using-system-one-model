# 03 - Mitigation Methods

> Gains are as reported by the cited papers (fetched summaries), not re-measured. Labels: [Inference] = my reasoning, not from a source. AI behavior is not guaranteed and may vary.

## 0. NOVELTY-RISK SECTION FIRST: prior work close to "small fast separate model scores each tool call + result and feeds the score back"

User's design elements: (a) separate fast verifier, (b) runs after every call, (c) sees call AND result, (d) outputs a probability, (e) harness passes the signal to the main LLM on the next step.

| Prior work | (a) separate small model | (b) every call | (c) sees result | (d) probability output | (e) fed back to main LLM | Reported result | URL |
|---|---|---|---|---|---|---|---|
| Reinforced Agent (Ta, Zhu, Shayandeh, 2026) | Yes: separate reviewer agent (o3-mini, GPT-4o tested; not small/fast) | Yes, before dispatch | No: reviews provisional call pre-execution | Not a probability: approve/reject/revise + textual feedback | Yes, as feedback | BFCL irrelevance +5.5%; tau2-Bench multi-turn +7.1%; o3-mini helpful:harmful 3:1 vs GPT-4o 2.1:1; GEPA prompt tuning +1.5-2.8% | https://arxiv.org/abs/2604.27233 |
| ToolCritic (Hamad et al., 2025) | Separate critic component trained on synthetic data | Timing not specified in abstract | Detects misinterpretation of tool outputs (so some result use) | Diagnostic labels + feedback | Yes (feedback to main LLM) | up to +13% tool-calling accuracy on SGD vs zero-shot prompting and self-correction | https://arxiv.org/abs/2510.17052 |
| Latent Critic, "Actionable Hallucination Detection" (Vijayvargiya, Lokesh, 2026) | LoRA adapter on the same frozen base model (not a separate model); reads hidden states | Intercepts at tool-call generation in a ReAct loop | No (pre-execution) | Detection score (AUROC 0.966 ID) + localized NL feedback | Yes, NL feedback within the sequence | ID AUROC 0.966 / OOD 0.925 vs external judge 0.915 / 0.884; latency <10 ms vs 884 ms; specific feedback 61.2% F1, 54.8% relative recovery gain over generic blocking (numbers from a secondary blog summary https://codex.danielvaughan.com/2026/08/17/actionable-hallucination-detection-latent-critic-specification-grounding-codex-cli-posttooluse-hooks-guardian/ ; abstract page confirmed AUROC 0.966, >80% localization) | https://arxiv.org/abs/2608.10430 |
| "The I Don't Know Filter" (Broecker et al., 2026) | Lightweight trainable classifier; uses output inconsistency across repeated calls as uncertainty proxy | per call | Not stated | Classifier decision | No: it replaces the call with an explicit abstention | New metric of negative outcomes of incorrect calls; numeric results not extracted | https://arxiv.org/abs/2607.04034 |
| Cleanlab TLM tool-call scoring | Uses TLM, "doesn't use a separate model" per docs summary; wraps existing LLM API | per call | Scores call vs request | Yes, trustworthiness 0-1 (examples 0.88-1.0 clear, 0.13 invalid parameter) | Docs suggest fallback/escalation by developer, not a standard feedback-to-LLM | no benchmark numbers in tutorial | https://help.cleanlab.ai/tlm/tutorials/tlm_tool_calls/ |
| ToolRM, IBM (Dec 2025/Jan 2026 v2) | Yes: 1.7B / 7B / 14B scalar reward models (Qwen-2.5 base) | Scores a candidate call or sequence | No (input = spec, history, generated calls) | Scalar reward | Used for Best-of-N, data filtering, RL; not run-time feedback | FC-RewardBench ~82% (14B) vs 45-80% baselines; Best-of-32 up to +24.9 pts for small models; limitation: favors calling over "no call" (irrelevance errors 185 to 210); scores whole sequences, not individual calls | https://arxiv.org/abs/2509.11963 |
| ToolRM, Li et al. ("Towards Agentic Tool-Use Reward Modeling") | Yes: Qwen3 4B/8B RMs | per candidate | No | Pairwise / scalar + generative critique | Critique used for self-correction: +11.4 pts over no critic, +2.0 over a baseline critic (search snippet; not on abstract page) ; ACEBench output tokens -66% | up to +17.94% pairwise accuracy | https://arxiv.org/abs/2510.26167 |
| Granite Guardian (IBM) | Yes: 8B (v4.1) / earlier 2B,5B etc. | Designed to evaluate intermediate agent steps | Not stated | Risk label / probability [Inference: Guardian emits Yes/No with score; not verified here] | Developer-defined | Apache 2.0; paper reports AUC 0.871/0.854 on harm / RAG-hallucination benchmarks (not function calling) | https://www.ibm.com/granite/docs/models/guardian ; https://arxiv.org/abs/2412.07724 |
| Probe-based detectors (Amazon; Yeats et al.; Noel et al.) | Internal to the generating model (not separate) | per call | No | Probability/AUC | Not fed back in what I read | Amazon up to 86.4% accuracy; Noel et al. (ICML 2026) token log-probs and N=5 consensus AUC 0.51-0.62, LMM probe 0.957 at 3B, spectral 0.888 at 8B, LMM 0.917 at 14B; Yeats et al.: 18 models on BFCL, probes generalise somewhat to novel error types | https://arxiv.org/abs/2601.05214 ; https://arxiv.org/abs/2608.27750 ; https://icml.cc/virtual/2026/67820 |
| MICE for CATs (NAACL 2025) | Classifier on layer-wise logit-lens features of the same model | per call | No | Calibrated probability | Used to decide whether to call (utility metric) | better/equal ECE vs baselines on STE dataset, Llama3; new "expected tool-calling utility" | https://arxiv.org/abs/2504.20168 |
| LLM2 dual-process (System 1 LLM + System 2 process verifier) | Verifier trained as process-based | per step | n/a (reasoning) | Process feedback | Guides generation | not extracted; applied to math reasoning, not tool use [Inference from search snippet] | https://arxiv.org/abs/2412.20372 |
| Inference-time tool-call reviewer (design pattern page) | Separate reviewer | per call | No | Approve/reject/revise | Yes | cites Ta et al. numbers; warns: self-critique can degrade near-ceiling tasks (~98% to 57% cited case), same-model reviewers share blind spots (64.5% cited), sync review doubles round-trips | https://agentpatterns.ai/patterns/agent-design/inference-time-tool-call-reviewer/ |

### Novelty assessment inputs (not a verdict)
- Found: separate reviewer that feeds textual feedback to the agent per call (Reinforced Agent, ToolCritic); lightweight same-model critic (Latent Critic); trainable lightweight filter that abstains (IDK filter); scalar reward models for calls (ToolRM x2); calibrated per-call confidence (MICE, probes, Cleanlab TLM).
- Not found in what I opened [Inference: absence in my search is not proof of absence]: a paper that (1) uses a separate small/fast model, (2) conditions on call AND returned result, (3) outputs a calibrated probability, (4) injects that scalar into the main agent's next-step context, and (5) measures effect on the main agent's downstream success and on false-alarm harm. Closest single paper on (1)+(4): Reinforced Agent; on (3)+(5)-like gating: IDK filter and MICE.
- Risk items to read in full before submission: Reinforced Agent (2604.27233), Latent Critic (2608.10430), IDK filter (2607.04034), ToolCritic (2510.17052). I only read abstracts/summaries.
- Harness mechanism already exists in products: Claude Code PostToolUse hooks can return `additionalContext` placed "next to tool result", and `updatedToolOutput`; prompt/agent hook types call a model (https://code.claude.com/docs/en/hooks). Also Codex-style hooks are discussed on a blog (https://codex.danielvaughan.com/2026/08/10/idk-filter-confident-hallucination-tool-calling-uncertainty-codex-cli-pretooluse-approval-policy-abstention/ ; secondary source, not opened in full).

## 1. Constrained decoding and schema validation

| Item | How it works | Reported gains | Limitations | URL |
|---|---|---|---|---|
| ToolDec (Zhang et al., 2023) | Finite-state machine constrains decoding to valid tool names/syntax | Removes all syntax errors in tool use (as claimed); Mistral-Instruct 0% to 52%, comparable to ToolLLM-tuned | Syntax only, does not check semantic correctness [Inference from scope] | https://arxiv.org/abs/2310.07075 |
| OpenAI Structured Outputs / strict mode | Constrained decoding to supplied JSON Schema | Docs state strict mode makes the model "always generate responses that adhere to your supplied JSON Schema" | JSON Schema subset only; structural not semantic validity; token-limit truncation can still yield invalid output | https://developers.openai.com/api/docs/guides/structured-outputs |
| Anthropic strict tool use | `strict: true` schema validation on tool inputs; docs call it "guarantee schema-valid tool inputs" (docs wording) | n/a | Schema only; forced tool_choice not supported on some models | https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools ; https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use (linked, not opened) |
| "Let Me Speak Freely?" (Tam et al.) | Study of format restriction (JSON/XML) | Finds significant decline in reasoning under format restrictions; stricter constraint, larger drop | Applies to structured outputs generally, not specifically tool calls | https://arxiv.org/abs/2408.02442 |
| Closed-World Resolution (HTB paper) | Training-free resolver: registry membership + signature validity before any gate | Targets fabricated tool/undeclared-argument calls | Registry check only; 2026 preprint | https://arxiv.org/abs/2609.19425 |
| ToolMisuseBench | Schema-aware methods evaluated under fault injection | "fault-specific improvements", overall success constrained | benchmark paper | https://arxiv.org/abs/2604.01508 |

[Inference] Schema validation covers categories 2-4 of the taxonomy; it does not address wrong-but-valid values, wrong tool among real ones, or result-grounding. This is the gap a semantic verifier addresses. FC-RewardBench paper itself includes rule-based schema validation as a baseline (https://arxiv.org/abs/2509.11963).

## 2. Self-verification and reflection

| Item | How | Reported | Limitations | URL |
|---|---|---|---|---|
| Reflexion | Verbal self-reflection stored in episodic memory after feedback | HumanEval 91% pass@1 vs GPT-4 80% | Needs a feedback signal; learning from trial and error still hard (authors) | https://arxiv.org/abs/2303.11366 |
| CRITIC (ICLR 2024) | LLM critiques own output using external tools, then revises | Improves QA, math program synthesis, toxicity | Emphasises external feedback matters | https://arxiv.org/abs/2305.11738 |
| Huang et al. (ICLR 2024) | Study of intrinsic self-correction | Finds LLMs struggle to self-correct reasoning without external feedback; can degrade | Shows motivation for external verifier | https://arxiv.org/abs/2310.01798 |
| ToolVerifier (Meta, EMNLP Findings 2024) | Self-asks contrastive questions between top-2 tools and for parameters | avg +22% over few-shot on 4 ToolBench tasks, 17 unseen tools | Same-model verification; synthetic Llama-2-70B data | https://arxiv.org/abs/2402.14158 |
| Reflect, Retry, Reward | Self-reflection trained by RL, rewarding reflection tokens if retry succeeds | up to +18.1% function calling; small models 1.5-7B beat 10x larger (search snippet; abstract page not opened) | Needs verifiable reward | https://arxiv.org/abs/2505.24726 |
| Verification prompts / retrieval_status flag | One-sentence prompt to emit OK/FAILED | 14.10% to 0.87% dishonesty (Fabrication after tool failure); verification prompts best for over-trust (Agents Trust Tools Too Much) | Prompt-level; Upward-Deceiver paper found prompt mitigation only marginal | https://arxiv.org/abs/2609.14758 ; https://arxiv.org/abs/2609.05587 ; https://arxiv.org/abs/2512.04864 |

## 3. External verifiers, critics, reward models, PRMs

| Item | How | Reported | Limitations | URL |
|---|---|---|---|---|
| ToolRM (IBM) | See table 0 | See table 0 | Whole-sequence scoring; irrelevance bias | https://arxiv.org/abs/2509.11963 |
| ToolRM (Li et al.) | Lightweight RMs on ToolPref-Pairwise-30K | +17.94% accuracy | single-turn BFCL-derived | https://arxiv.org/abs/2510.26167 |
| Themis / TARA (tool-augmented RM) | RM calls tools (calculator, search) in Thought-Action-Observation-Rationale-Reward loop | +17.7% across 8 preference tasks (ICLR 2024) | Reward models for text preferences, not call correctness | https://arxiv.org/abs/2310.01045 |
| AgentPRM | Monte Carlo rollouts for step reward in actor-critic; InversePRM from demos | 3B models beat GPT-4o baselines on ALFWorld | Not tool-call-specific; reward hacking discussed | https://arxiv.org/abs/2502.10325 |
| ToolPRMBench | Benchmark for PRMs on tool agents | Tool-specialised PRMs show "notable potential" | no small PRM trained (per fetch) | https://arxiv.org/abs/2601.12294 |
| AgentProcessBench | Step-level labels for tool trajectories | finds weak models look accurate due to early termination; process signals add to outcome training | benchmark | https://arxiv.org/abs/2603.14465 |
| Other PRM/verifier papers seen only as search hits, not opened: Hybrid Reward Normalization 2509.25598; Verifiable Process Rewards 2605.10325; AgentV-RL 2604.16004; LLM-as-a-Verifier 2607.05391 | - | - | [Unverified] | via search results |
| LLM-judge baselines | General judges; in ToolRM paper six LLM judges (70B-685B) scored below ToolRM-14B on FC-RewardBench | see above | latency/cost; Latent Critic reports 884 ms external judge | https://arxiv.org/abs/2509.11963 ; https://arxiv.org/abs/2608.10430 |

## 4. Uncertainty / confidence estimation for tool calls

| Item | How | Reported | Limitations | URL |
|---|---|---|---|---|
| MICE | See table 0 | Better calibration; zero-shot to unseen APIs | Needs white-box access | https://arxiv.org/abs/2504.20168 |
| Noel et al. (ICML 2026) | Attention-spectral and hidden-state probes | token log-prob and consensus near chance (AUC 0.51-0.62) on 7 models | Best detector depends on model scale; "match the guardrail to depth and attention type" | https://icml.cc/virtual/2026/67820 |
| Trajectory-adapted UQ (Bouchard, Chauhan 2026) | White-box, black-box consistency, reflexive scorers on multi-turn BFCL-v4 and tau2 | Transfer "often useful but uneven"; reflexive scores strong cheap baseline; black-box self-consistency generally strongest | token-prob sensitive to aggregation | https://arxiv.org/abs/2608.11552 |
| IDK filter | consistency across repeated calls as proxy | see table 0 | | https://arxiv.org/abs/2607.04034 |
| Cleanlab TLM | black-box trust score | see table 0 | commercial; method details not in tutorial | https://help.cleanlab.ai/tlm/tutorials/tlm_tool_calls/ |
| Verbalized confidence as judge signal | VERDI / "Rethinking Verbalized Confidence" (search hits only) | - | [Unverified] | https://arxiv.org/abs/2605.11334 ; https://arxiv.org/abs/2609.10996 |

## 5. Abstention and irrelevance training

| Item | How | Reported | Limitations | URL |
|---|---|---|---|---|
| Relign | SFT+DPO with indecisive actions (ChangeTools, TalkToUser) | 61.5% to 18.8% hallucination rate (Llama 3.1 8B) | Single model/benchmark | https://arxiv.org/abs/2412.04141 |
| Hammer | Function masking + irrelevance-augmented data | State of the art among on-device-size models (as claimed) | Training-time | https://arxiv.org/abs/2410.04587 |
| BFCL relevance/irrelevance | Evaluation of abstention | - | Binary | https://gorilla.cs.berkeley.edu/leaderboard.html |
| Agentic Abstention / CONVOLVE (2026) | Context-engineered stopping rules from interaction histories | WebShop Llama-3.3-70B timely recall 26.7% to 57.4% | Larger models sometimes worse at timely abstention | https://arxiv.org/abs/2606.28733 |
| Reasoning Trap | Prompt and DPO mitigation of reasoning-induced hallucination | Reduces hallucination but "consistently degrades utility" | trade-off | https://arxiv.org/abs/2510.22977 |
| ToolRM side effect | Reward model prefers calling over abstaining | irrelevance errors 185 to 210 | | https://arxiv.org/abs/2509.11963 |

## 6. Retrieval of tool documentation / tool retrieval

| Item | How | Reported | Limitations | URL |
|---|---|---|---|---|
| Gorilla + retriever | Retrieve API docs at inference | Hallucination 5.0% to 0.0% on APIBench for Gorilla (fetch summary of PDF) | Constrains to DB entries; APIBench scope | https://arxiv.org/abs/2305.15334 |
| Tool Documentation (Hsieh et al.) | Docs replace demonstrations | Zero-shot docs match few-shot; better on hundreds of tools | Depends on doc quality | https://arxiv.org/abs/2308.00675 |
| RAG-MCP | Semantic retrieval of MCP tools before prompting | Prompt tokens -50%+; tool selection accuracy 13.62% to 43.13% | Retrieval misses = missing tool | https://arxiv.org/abs/2505.03275 |
| Tool-Memory Conflict study | Tests prompt engineering and RAG for conflicts | Neither resolves conflicts | | https://arxiv.org/abs/2601.09760 |

## 7. Runtime guardrails in agent harnesses

| Item | How | Reported | Limitations | URL |
|---|---|---|---|---|
| Claude Code hooks | PreToolUse can deny/modify; PostToolUse can add `additionalContext` or replace output; prompt/agent hook types (experimental) | n/a (product docs) | Rule/command based by default; no built-in calibrated score | https://code.claude.com/docs/en/hooks |
| LlamaFirewall | PromptGuard 2, AlignmentCheck (agent reasoning auditor), CodeShield | claims SOTA jailbreak detection | Security-oriented (injection/misalignment), not correctness of arguments | https://arxiv.org/abs/2505.03574 |
| AgentGuard | Runtime verification: observes I/O, learns MDP, model-checks | search snippet only | [Unverified] details | https://arxiv.org/abs/2509.23864 |
| VeriGuard | Offline verified policy + lightweight online monitor of each action | search snippet only | safety policy focus | https://arxiv.org/abs/2510.05156 |
| Closed-World Resolution | Registry gate | see sec 1 | | https://arxiv.org/abs/2609.19425 |
| Inference-time reviewer pattern | see table 0 | | latency, blind spots | https://agentpatterns.ai/patterns/agent-design/inference-time-tool-call-reviewer/ |
