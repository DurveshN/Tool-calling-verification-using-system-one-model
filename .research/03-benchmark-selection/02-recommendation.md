# Recommendation

## Primary: Terminal-Bench 2.0 via Harbor + opencode agent
- Subset: all 89 tasks (closest to 100, no sampling bias). If budget forces fewer, take a random sample stratified by category/difficulty with a fixed seed, identical across A/B/C. Category/difficulty split [Unverified: not read].
- For more power: 89 tasks x K=2 repeats per condition.
- Per task: verifier pass/fail is ground truth independent of the Opus judge. The Opus judge labels each tool call hallucinated or not.

## Statistics
- Paired design: same tasks, same model, three conditions. Task-level binary outcomes: exact McNemar on discordant pairs (A vs B, A vs C, B vs C), Holm correction for 3 comparisons. [Inference] with about 20 discordant pairs a 15:5 split gives p about 0.04 uncorrected, so only differences of roughly 15+ percentage points are detectable at n=89.
- Primary hallucination metric: per-tool-call hallucination rate. Calls cluster within tasks, so use a task-level cluster bootstrap (10,000 resamples), paired across conditions. Also report per-task "any hallucinated call" (McNemar) and calls per task.
- With repeats, average per task then bootstrap over tasks.
- Check Opus-judge agreement on a ~10% human-labelled sample.

## Setup (Windows 11)
1. Docker is needed (Harbor default environment). Use Docker Desktop with the WSL2 backend and run Harbor inside WSL2 Ubuntu. Alternative: cloud sandboxes (Daytona, Modal, e2b). Native Windows Harbor support [Unverified].
2. `uv tool install harbor` (or pip).
3. Run roughly `harbor run -d terminal-bench/terminal-bench-2 -a opencode -m provider/model` [exact flags Unverified; check `harbor run --help`]. Dataset: https://hub.harborframework.com/datasets/terminal-bench/terminal-bench-2/latest
4. Critic injection: Harbor runs opencode as a CLI inside the container, so the critic has to hook in. Options [Inference]: (a) an OpenCode plugin using tool-execution hooks that calls Haiku/Clef and appends the verdict to the tool output; (b) an MCP proxy. The OpenCode plugin API was not opened here; verify in opencode.ai docs. Conditions A/B/C then differ only in plugin config, e.g. via OPENCODE_CONFIG_CONTENT.
5. Collect `trajectory.json` (ATIF) per task for the judge.

## Secondary: MCPMark filesystem (30 tasks), optionally plus Postgres (21)
Programmatic verification; whole-benchmark average 17.4 tool calls. Needs a custom runner pointing OpenCode at the MCP server. Exercises MCP tool-name/parameter hallucination.

## Risks
- Critic-injection engineering inside Docker; container needs network to Haiku/Clef.
- Mid-size model may score low, so many runs end in timeout. Fine for hallucination labels, weak for outcome comparisons.
- Cost and time: 89 tasks x 3 conditions with long trajectories.
- Critic verdicts alter trajectories; the judge should see critic text separately from raw tool output.
- Terminal tasks are bash-heavy; glob/list/webfetch/MCP are less exercised.
- tbench.ai warns benchmark data should not appear in training corpora; do not publish transcripts openly.
