"""Build blinded judge packets from data/calls.jsonl + raw trajectories.

- Removes every [tool-check] verdict from tool outputs and silently deletes agent-message lines that mention it
  (no marker, since a marker would reveal arms B/C).
- Assigns random packet IDs; the packet->run/trial key goes to data/judge/key.json (never shown to the judge).
- Packet order is shuffled with a fixed seed.

Usage: python scripts/judge_packets.py --phase pilot [--seed 7]
Outputs: data/judge/<phase>/packets/<id>_p<k>.md, data/judge/<phase>/key.json
"""
import argparse
import json
import random
import re
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
MENTION_RE = re.compile(r"^.*(tool-check|P\(correct\)|P\(grounded_call\)|possible hallucination).*$", re.IGNORECASE | re.MULTILINE)
HEAD, TAIL = 4000, 2000
MAX_PART = 150_000


def clip(s: str) -> str:
    s = s or ""
    return s if len(s) <= HEAD + TAIL else f"{s[:HEAD]}\n[...{len(s) - HEAD - TAIL} chars omitted...]\n{s[-TAIL:]}"


def text_of(msg) -> str:
    return msg if isinstance(msg, str) else json.dumps(msg, ensure_ascii=False)


def packet_parts(pid: str, task: dict, calls: dict, traj: dict) -> list[str]:
    """Split a transcript into parts of <= MAX_PART chars. Each part repeats the task; call numbers are global."""
    task_text, blocks, k = "", [], 0
    for step in traj.get("steps", []):
        if step.get("source") == "user":
            task_text = text_of(step.get("message", ""))
            continue
        b = []
        msg = MENTION_RE.sub("", text_of(step.get("message") or "")).strip()
        if msg:
            b += ["**Agent:**", "", msg, ""]
        for tc in step.get("tool_calls") or []:
            c = calls.get(tc["tool_call_id"], {})
            b += [f"### Call {k} · `{tc['function_name']}`", "", "```json",
                  json.dumps(tc["arguments"], indent=1, ensure_ascii=False), "```", "", "Output:", "", "~~~~",
                  clip(str(c.get("output", ""))), "~~~~", ""]
            k += 1
        if b:
            blocks.append("\n".join(b))
    groups, cur = [], []
    for b in blocks:
        if cur and sum(map(len, cur)) + len(b) > MAX_PART:
            groups.append(cur)
            cur = []
        cur.append(b)
    groups.append(cur)
    outcome = f"## Final test outcome\n\nreward = {task['reward']} (1.0 = all task tests passed)\n"
    parts = []
    for i, g in enumerate(groups):
        head = f"# Packet {pid} · part {i + 1}/{len(groups)} (total calls: {k})\n\n## Task\n\n{task_text}\n\n"
        if i:
            head += "_Earlier calls are in previous parts; label only the calls shown here._\n\n"
        parts.append(head + "\n".join(g) + "\n" + (outcome if i == len(groups) - 1 else ""))
    return parts


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", required=True)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--tasks", help="file with task names to include (default: all tasks in the phase)")
    a = ap.parse_args()
    keep = set(Path(a.tasks).read_text(encoding="utf-8").split()) if a.tasks else None
    tasks = [t for t in map(json.loads, filter(str.strip, (DATA / "tasks.jsonl").read_text(encoding="utf-8").split("\n")))
             if t["phase"] == a.phase and t["n_tool_calls"] > 0 and (keep is None or t["task"] in keep)]
    calls: dict[tuple, dict] = {}
    for c in map(json.loads, filter(str.strip, (DATA / "calls.jsonl").read_text(encoding="utf-8").split("\n"))):
        calls.setdefault((c["run"], c["trial"]), {})[c["call_id"]] = c
    out_dir = DATA / "judge" / a.phase
    (out_dir / "packets").mkdir(parents=True, exist_ok=True)
    key_path = out_dir / "key.json"
    key = json.loads(key_path.read_text()) if key_path.exists() else {}
    known = {(v["run"], v["trial"]) for v in key.values()}
    random.Random(a.seed).shuffle(tasks)
    for t in tasks:
        if (t["run"], t["trial"]) in known:
            continue  # packet IDs are stable once assigned
        pid = secrets.token_hex(4)
        traj_path = next((ROOT / "runs" / t["run"]).glob(f"jobs/*/{t['trial']}/agent/trajectory.json"), None)
        traj = json.loads(traj_path.read_text(encoding="utf-8")) if traj_path else {}
        tc = calls.get((t["run"], t["trial"]), {})
        parts = packet_parts(pid, t, tc, traj)
        for i, part in enumerate(parts, 1):
            (out_dir / "packets" / f"{pid}_p{i}.md").write_text(part, encoding="utf-8")
        key[pid] = {"run": t["run"], "trial": t["trial"], "arm": t["arm"], "task": t["task"], "n_parts": len(parts),
                    "call_ids": [c for c in sorted(tc, key=lambda x: tc[x]["call_index"])]}
    key_path.write_text(json.dumps(key, indent=1), encoding="utf-8")
    print(f"packets: {len(key)} in {out_dir}")


if __name__ == "__main__":
    main()
