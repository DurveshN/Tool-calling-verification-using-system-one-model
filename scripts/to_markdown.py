"""Render readable transcripts from data/tasks.jsonl + raw trajectories.

Output: data/transcripts/<run>/<trial>.md with the task prompt, every agent message, every tool call
(full args + full output), and the critic verdict (probabilities, latency, cost) for each call.
Run scripts/collect.py first. Usage: python scripts/to_markdown.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def fence(text: str, lang: str = "") -> str:
    ticks = "`" * max(3, max((len(r) for r in text.split("\n") for r in [r[: len(r) - len(r.lstrip("`"))]]), default=0) + 1)
    return f"{ticks}{lang}\n{text}\n{ticks}"


def render(task: dict, calls: dict[str, dict], traj: dict) -> str:
    out = [
        f"# {task['task']} · arm {task['arm']} ({task['critic_mode']})",
        "",
        "| field | value |", "|---|---|",
        *(f"| {k} | {task[k]} |" for k in ("run", "trial", "reward", "exception", "agent_model", "agent_version",
                                            "n_steps", "n_tool_calls", "n_critic_errors", "agent_tokens_in",
                                            "agent_tokens_out", "agent_cost_usd_upper", "critic_cost_usd",
                                            "agent_exec_s", "critic_latency_ms_total", "git_commit")),
        "",
    ]
    for step in traj.get("steps", []):
        src = step.get("source")
        out.append(f"## Step {step['step_id']} · {src}")
        if step.get("message"):
            out += ["", fence(step["message"] if isinstance(step["message"], str) else json.dumps(step["message"], indent=1)), ""]
        for tc in step.get("tool_calls") or []:
            c = calls.get(tc["tool_call_id"], {})
            out += [f"### Tool call `{tc['function_name']}` · `{tc['tool_call_id']}`", "",
                    fence(json.dumps(tc["arguments"], indent=1, ensure_ascii=False), "json"), "", "**Output** (verdict stripped):", "",
                    fence(str(c.get("output", ""))), ""]
            if c.get("probs"):
                p = c["probs"]
                out += [f"**Critic** `{c['critic_model']}` · {c['critic_latency_ms']} ms · ${c['critic_cost_usd'] or 0:.6f}", "",
                        "| question | P(yes) |", "|---|---|", *(f"| {k} | {v:.3f} |" for k, v in p.items()), "",
                        f"Injected to agent: `{(c.get('injected') or '').strip()}`", ""]
            elif c.get("critic_error"):
                out += [f"**Critic error:** `{c['critic_error']}`", ""]
    return "\n".join(out) + "\n"


def main() -> None:
    tasks = [json.loads(l) for l in (DATA / "tasks.jsonl").read_text(encoding="utf-8").split("\n") if l.strip()]
    calls_by_trial: dict[tuple, dict] = {}
    for l in filter(str.strip, (DATA / "calls.jsonl").read_text(encoding="utf-8").split("\n")):
        c = json.loads(l)
        calls_by_trial.setdefault((c["run"], c["trial"]), {})[c["call_id"]] = c
    for t in tasks:
        traj_path = next((ROOT / "runs" / t["run"]).glob(f"jobs/*/{t['trial']}/agent/trajectory.json"), None)
        traj = json.loads(traj_path.read_text(encoding="utf-8")) if traj_path else {}
        dest = DATA / "transcripts" / t["run"] / f"{t['trial']}.md"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(render(t, calls_by_trial.get((t["run"], t["trial"]), {}), traj), encoding="utf-8")
    print(f"transcripts written: {len(tasks)}")


if __name__ == "__main__":
    main()
