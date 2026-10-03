"""Build derived datasets from raw run evidence (read-only over runs/).

Outputs (regenerable at any time):
  data/calls.jsonl         one row per tool call (trajectory + critic record joined on call id)
  data/tasks.jsonl         one row per trial (task outcome, tokens, cost, timings)
  data/excluded_runs.json  runs skipped because they carry INVALID.md

Usage: python scripts/collect.py
"""
import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS, DATA = ROOT / "runs", ROOT / "data"
PRICES = json.loads((ROOT / "scripts" / "pricing.json").read_text(encoding="utf-8"))
VERDICT_RE = re.compile(r"\n\n\[tool-check\] [^\n]*$")


def cost(model: str, tokens_in: int, tokens_out: int) -> float | None:
    p = PRICES.get(model)
    return None if p is None else (tokens_in * p["input"] + tokens_out * p["output"]) / 1e6


def secs(span: dict | None) -> float | None:
    if not span or not span.get("started_at") or not span.get("finished_at"):
        return None
    f = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00"))
    return (f(span["finished_at"]) - f(span["started_at"])).total_seconds()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()] if path.exists() else []


def provenance(run: Path) -> dict:
    """provenance.txt, plus post-hoc PHASE annotation for runs made before phase tagging existed."""
    p, ph = run / "provenance.txt", run / "PHASE"
    prov = dict(l.split("=", 1) for l in p.read_text(encoding="utf-8").splitlines() if "=" in l) if p.exists() else {}
    if "phase" not in prov and ph.exists():
        prov["phase"] = ph.read_text(encoding="utf-8").strip()
    return prov


def tool_status(trial: Path) -> dict[str, tuple[str, str | None]]:
    """callID -> (final status, error text) from OpenCode's raw event stream (Harbor's trajectory drops errors)."""
    status: dict[str, tuple[str, str | None]] = {}
    f = trial / "agent" / "opencode.txt"
    for line in f.read_text(encoding="utf-8", errors="replace").splitlines() if f.exists() else []:
        try:
            part = json.loads(line).get("part") or {}
        except json.JSONDecodeError:
            continue
        if part.get("type") == "tool" and part.get("callID"):
            st = part.get("state") or {}
            status[part["callID"]] = (st.get("status"), st.get("error"))
    return status


def critic_cost(rec: dict) -> float | None:
    u, m = rec.get("usage") or {}, rec.get("critic_model")
    if not m:
        return None
    return cost(m, u.get("prompt_tokens", u.get("input_tokens", 0)), u.get("completion_tokens", u.get("output_tokens", 0)))


def collect_trial(run: Path, prov: dict, trial: Path) -> tuple[dict, list[dict]]:
    res = json.loads((trial / "result.json").read_text(encoding="utf-8"))
    traj_path = trial / "agent" / "trajectory.json"
    traj = json.loads(traj_path.read_text(encoding="utf-8")) if traj_path.exists() else {"steps": []}
    critic = {r["call_id"]: r for r in read_jsonl(trial / "agent" / "critic.jsonl")}
    status = tool_status(trial)

    base = {"run": run.name, "phase": prov.get("phase"), "arm": prov.get("arm"), "critic_mode": prov.get("critic_mode"),
            "task": res["task_name"], "trial": res["trial_name"]}
    calls, idx = [], 0
    for step in traj["steps"]:
        outputs = {o.get("source_call_id"): o.get("content") for o in (step.get("observation") or {}).get("results", [])}
        for tc in step.get("tool_calls") or []:
            raw = outputs.get(tc["tool_call_id"])
            st, err = status.get(tc["tool_call_id"], (None, None))
            if raw is None and err:
                raw = f"ERROR: {err}"
            rec = critic.get(tc["tool_call_id"], {})
            calls.append({
                **base, "call_index": idx, "step_id": step["step_id"], "call_id": tc["tool_call_id"],
                "tool": tc["function_name"], "args": tc["arguments"], "tool_status": st,
                "output_raw": raw,  # as the agent saw it (includes [tool-check] line in arms B/C)
                "output": VERDICT_RE.sub("", raw) if isinstance(raw, str) else raw,  # verdict stripped
                "critic_logged": bool(rec), "critic_state": rec.get("state"),
                "truncated_chars": rec.get("truncated_chars"), "critic_model": rec.get("critic_model"),
                "probs": rec.get("probs"), "critic_latency_ms": rec.get("latency_ms"),
                "critic_error": rec.get("error"), "critic_usage": rec.get("usage"),
                "critic_cost_usd": critic_cost(rec), "injected": rec.get("injected"),
            })
            idx += 1

    ar = res.get("agent_result") or {}
    model = (res.get("agent_info") or {}).get("model_info", {}).get("name")
    n_in, n_out = ar.get("n_input_tokens") or 0, ar.get("n_output_tokens") or 0
    rewards = (res.get("verifier_result") or {}).get("rewards") or {}
    task_row = {
        **base, "reward": rewards.get("reward"), "exception": (res.get("exception_info") or {}).get("exception_type")
        if res.get("exception_info") else None,
        "n_tool_calls": len(calls), "n_steps": len(traj["steps"]),
        "n_critic_records": len(critic), "n_critic_errors": sum(1 for r in critic.values() if r.get("error")),
        "agent_model": model, "agent_version": (res.get("agent_info") or {}).get("version"),
        "agent_tokens_in": n_in, "agent_tokens_cached": ar.get("n_cache_tokens"), "agent_tokens_out": n_out,
        "agent_cost_usd_upper": cost(model, n_in, n_out),
        "critic_cost_usd": sum(c["critic_cost_usd"] or 0 for c in calls),
        "critic_latency_ms_total": sum(c["critic_latency_ms"] or 0 for c in calls),
        "agent_exec_s": secs(res.get("agent_execution")), "agent_setup_s": secs(res.get("agent_setup")),
        "trial_s": secs(res), "git_commit": prov.get("git_commit"), "dataset_sha256": prov.get("dataset_sha256"),
    }
    return task_row, calls


def main() -> None:
    DATA.mkdir(exist_ok=True)
    tasks, calls, excluded = [], [], []
    for run in sorted(p for p in RUNS.iterdir() if p.is_dir()):
        if (run / "INVALID.md").exists():
            excluded.append({"run": run.name, "reason": (run / "INVALID.md").read_text(encoding="utf-8")})
            continue
        prov = provenance(run)
        for trial in sorted(p.parent for p in run.glob("jobs/*/*/result.json") if (p.parent / "agent").is_dir()):
            t, c = collect_trial(run, prov, trial)
            tasks.append(t)
            calls.extend(c)
    for name, rows in (("tasks.jsonl", tasks), ("calls.jsonl", calls)):
        (DATA / name).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    (DATA / "excluded_runs.json").write_text(json.dumps(excluded, indent=1), encoding="utf-8")
    unmatched = sum(1 for c in calls if not c["critic_logged"])
    print(f"trials={len(tasks)} calls={len(calls)} excluded_runs={len(excluded)} calls_without_critic_record={unmatched}")


if __name__ == "__main__":
    main()
