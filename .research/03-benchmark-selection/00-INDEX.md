# 03 Benchmark selection - index

Recommendation: **Terminal-Bench 2.0 (89 tasks) run through Harbor with the built-in `opencode` agent.** Use all 89 tasks (about 100) per condition, same task set in A/B/C (paired design). Secondary: **MCPMark filesystem split (30 tasks)** for an MCP-tool slice (needs a custom OpenCode runner).

Why: well known (arXiv 2601.11868, Stanford/Laude), Harbor has an `opencode.py` agent (opened on GitHub), binary auto-verifier independent of the Opus judge, long multi-step tool trajectories, Apache-2.0. Cost: Docker required (Windows: Docker Desktop with WSL2 backend, or cloud sandboxes Daytona/Modal).

Main risk: the critic must be injected into OpenCode's loop inside the container; Harbor does not provide that. Needs an OpenCode plugin or wrapper [Inference, not verified]. Also likely low pass rates for a mid-size model.

Files: 01-candidates.md, 02-recommendation.md, 03-references.md. Anything not opened is marked [Unverified].
