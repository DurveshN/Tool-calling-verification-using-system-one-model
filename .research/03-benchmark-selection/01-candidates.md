# Candidates (facts only from pages opened; otherwise [Unverified])

| Benchmark | Size | License | Tests | Outcome check | OpenCode fit | Tool-call load | Setup |
|---|---|---|---|---|---|---|---|
| Terminal-Bench 2.0 | 89 tasks | Apache-2.0 (repos); paper CC BY 4.0 | multi-step terminal tasks | binary 0/1 auto tests | Harbor `opencode` agent exists | max 200 agent turns default; avg [Unverified] | Docker default; cloud options |
| Terminal-Bench core v0.1.x (legacy) | README says ~100 tasks beta; core size [Unverified] | Apache-2.0 | same | tests | superseded by Harbor | [Unverified] | Docker + uv |
| SWE-bench Verified / Multimodal / Lite | 500 / 480 / Lite size not on page [Unverified] | MIT | issue to patch | Docker test harness | no known adapter [Unverified]; could run opencode on repo and export patch | high | Docker, 120GB disk, 16GB RAM, WSL on Windows |
| tau2-bench (README lists mock, airline, retail, telecom, banking_knowledge) | per-domain counts not found [Unverified] | MIT | conversational policy + tools | DB state / expected actions | poor fit (own tools, user simulator) | moderate [Unverified] | Python 3.12+, no Docker stated |
| MCPMark | 127 tasks (FS 30, Notion 28, Playwright 25, GitHub 23, Postgres 21) | Apache-2.0 | MCP use | programmatic verify scripts | OpenCode supports MCP; no MCPMark adapter found | avg 17.4 calls, 16.2 turns | FS needs no accounts; others need Notion/GitHub/Postgres/browser |
| MCP-Atlas | 1,000 tasks, 36 servers, 220 tools (snippet only) | [Unverified] | MCP tool competency | [Unverified] | custom via MCP | [Unverified] | [Unverified] |
| LiveMCPBench | 95 tasks (snippet only) | [Unverified] | MCP navigation | [Unverified] | custom | [Unverified] | [Unverified] |
| MCP-Bench | count not found | [Unverified] | MCP | LLM-as-judge scoring (snippet) | custom | | |
| ToolBeHonest | 700 samples (1,050 over 3 levels) | MIT | hallucination, unsolvable-tool detection | label match | no: tools are names only, single-turn planning | none | none |
| ToolFailBench | 1,000 single-turn tasks, mock tools | not specified | Tool-Skip, Result-Ignore, Output-Fabrication | rule classifier + 2 LLM judges | no: single call, not agentic | 1 | none |
| BFCL, ToolSandbox, AppWorld, GAIA, AgentBench OS, NESTFUL, ToolHop | not researched in this pass | | | | | | [Unverified] |

## Notes
- Terminal-Bench 2.0: Harbor `src/harbor/agents/installed/opencode.py` runs `opencode --model=provider/model run --format=json ...`, writes `~/.config/opencode/opencode.json` (MCP stdio/remote, permission denies), and parses output into ATIF `trajectory.json` with tool calls and observations. This is convenient judge input. Env var OPENCODE_CONFIG_CONTENT supplies inline config.
- MCPMark: its pipeline supports MCPMarkAgent and ReAct agents; opencode not listed. Filesystem split is zero-config.
- ToolFailBench / ToolBeHonest address tool hallucination directly but are not agentic loops, so they cannot exercise OpenCode tools or critic injection. Only useful as side sanity checks.
- tau2: policy-following dialogue; adapting a coding agent is high cost.
