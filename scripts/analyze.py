"""Join judge labels with calls (+ replay) and report hallucination rates and critic quality.

Usage: python scripts/analyze.py --phase pilot2 [--out results/pilot2]
Inputs: data/calls.jsonl, data/tasks.jsonl, data/judge/<phase>/{key.json,labels/*.jsonl}, data/replay.jsonl (optional)
Outputs: <out>/summary.md (tables, in git) and data/analysis/<phase>/calls_labelled.jsonl (per-call data, not in git)
"""
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STRICT = {"fabricated_tool", "bad_args", "misread_output", "wrong_tool", "schema_violation"}
BROAD = STRICT | {"trajectory_error", "unnecessary_call"}
PRIMARY = "grounded_call"


def jsonl(p: Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []


def auroc(scores: list[float], labels: list[int]) -> float | None:
    """P(score of a positive > score of a negative), ties = 0.5. Positive = hallucinated, score = 1 - P(grounded)."""
    pos = [s for s, y in zip(scores, labels) if y]
    neg = [s for s, y in zip(scores, labels) if not y]
    if not pos or not neg:
        return None
    wins = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return wins / (len(pos) * len(neg))


def ece(probs_hall: list[float], labels: list[int], bins: int = 10) -> float:
    b = defaultdict(list)
    for p, y in zip(probs_hall, labels):
        b[min(int(p * bins), bins - 1)].append((p, y))
    return sum(len(v) / len(labels) * abs(sum(p for p, _ in v) / len(v) - sum(y for _, y in v) / len(v)) for v in b.values())


def critic_metrics(rows: list[tuple[float, int]]) -> dict:
    scores = [1 - p for p, _ in rows]  # P(hallucinated)
    ys = [y for _, y in rows]
    flagged = [p < 0.5 for p, _ in rows]
    tp = sum(f and y for f, y in zip(flagged, ys))
    fp = sum(f and not y for f, y in zip(flagged, ys))
    pos, neg = sum(ys), len(ys) - sum(ys)
    return {
        "n": len(rows), "positives": pos, "auroc": auroc(scores, ys), "ece": ece(scores, ys),
        "recall@0.5": tp / pos if pos else None, "precision@0.5": tp / (tp + fp) if tp + fp else None,
        "false_alarm_rate": fp / neg if neg else None,
    }


def fmt(v) -> str:
    return "–" if v is None else f"{v:.3f}" if isinstance(v, float) else str(v)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", required=True)
    ap.add_argument("--out")
    ap.add_argument("--labels-dir", default="labels", help="judge label directory under data/judge/<phase>/")
    a = ap.parse_args()
    out = Path(a.out) if a.out else ROOT / "results" / a.phase
    out.mkdir(parents=True, exist_ok=True)
    jdir = DATA / "judge" / a.phase
    key = json.loads((jdir / "key.json").read_text(encoding="utf-8"))

    labels, claims, summaries, missing = {}, defaultdict(list), {}, []
    for pid, v in key.items():
        rows = [r for i in range(1, v["n_parts"] + 1) for r in jsonl(jdir / a.labels_dir / f"{pid}_p{i}.jsonl")]
        calls = {r["call"]: r for r in rows if "call" in r and "label" in r}
        if len(calls) != len(v["call_ids"]):
            missing.append(f"{pid} ({v['arm']} {v['task']}): {len(calls)}/{len(v['call_ids'])} calls labelled")
        for k, cid in enumerate(v["call_ids"]):
            if k in calls:
                labels[(v["run"], v["trial"], cid)] = calls[k]
        claims[pid] = [r for r in rows if "claim" in r]
        summaries[pid] = next((r for r in rows if r.get("summary")), {})

    calls = [c for c in jsonl(DATA / "calls.jsonl") if c["phase"] == a.phase]
    tasks = {(t["run"], t["trial"]): t for t in jsonl(DATA / "tasks.jsonl") if t["phase"] == a.phase}
    for c in calls:
        lab = labels.get((c["run"], c["trial"], c["call_id"]))
        c["judge"] = lab
        c["strict"] = int(bool(lab) and lab["label"] in STRICT)
        c["broad"] = int(bool(lab) and lab["label"] in BROAD)
    labelled = [c for c in calls if c["judge"]]
    (DATA / "analysis" / a.phase).mkdir(parents=True, exist_ok=True)
    (DATA / "analysis" / a.phase / "calls_labelled.jsonl").write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in labelled), encoding="utf-8")

    md = [f"# Analysis: phase `{a.phase}`", "", f"Labelled calls: {len(labelled)} / {len(calls)}"]
    if missing:
        md += ["", "**Incomplete labels:**", *(f"- {m}" for m in missing)]

    # 1. Agent-level hallucination by arm
    arms = sorted({c["arm"] for c in labelled})
    md += ["", "## 1. Hallucination by arm (judge labels)", "",
           "| arm | tasks passed | calls | strict halluc. | strict / call | broad errors | broad / call | false/unsupported claims | final claim false |",
           "|---|---|---|---|---|---|---|---|---|"]
    for arm in arms:
        cs = [c for c in labelled if c["arm"] == arm]
        pids = [p for p, v in key.items() if v["arm"] == arm]
        trs = [t for t in tasks.values() if t["arm"] == arm and t["n_tool_calls"] > 0]
        s, b = sum(c["strict"] for c in cs), sum(c["broad"] for c in cs)
        md.append(f"| {arm} | {sum(1 for t in trs if t['reward'] == 1.0)}/{len(trs)} | {len(cs)} | {s} | {s / len(cs):.3f} | {b} | {b / len(cs):.3f} | "
                  f"{sum(len(claims[p]) for p in pids)} | {sum(1 for p in pids if summaries[p].get('final_claim_false'))} |")

    # 2. Per task × arm
    md += ["", "## 2. Strict hallucinations / calls, per task", "", "| task | " + " | ".join(arms) + " |", "|---|" + "---|" * len(arms)]
    for task in sorted({c["task"] for c in labelled}):
        cells = []
        for arm in arms:
            cs = [c for c in labelled if c["task"] == task and c["arm"] == arm]
            cells.append(f"{sum(c['strict'] for c in cs)}/{len(cs)}" if cs else "–")
        md.append(f"| {task} | " + " | ".join(cells) + " |")

    # 3. Label distribution
    md += ["", "## 3. Label distribution", "", "| label | " + " | ".join(arms) + " |", "|---|" + "---|" * len(arms)]
    for lab in sorted({c["judge"]["label"] for c in labelled}):
        md.append(f"| {lab} | " + " | ".join(str(sum(1 for c in labelled if c["arm"] == arm and c["judge"]["label"] == lab)) for arm in arms) + " |")

    # 4. Critic quality vs judge (online verdicts on own arm; replay on all calls)
    md += ["", "## 4. Critic quality vs judge labels (positive = strict hallucination; score = 1 − P(grounded_call))", "",
           "| critic | source | n | positives | AUROC | ECE | recall@0.5 | precision@0.5 | false-alarm rate |", "|---|---|---|---|---|---|---|---|---|"]
    for arm in ("B", "C"):
        rows = [(c["probs"][PRIMARY], c["strict"]) for c in labelled if c["arm"] == arm and c.get("probs") and PRIMARY in c["probs"]]
        if rows:
            m = critic_metrics(rows)
            critic = next(c["critic_model"] for c in labelled if c["arm"] == arm and c.get("critic_model"))
            md.append(f"| {critic} | online, arm {arm} | {m['n']} | {m['positives']} | {fmt(m['auroc'])} | {fmt(m['ece'])} | "
                      f"{fmt(m['recall@0.5'])} | {fmt(m['precision@0.5'])} | {fmt(m['false_alarm_rate'])} |")
    replay = defaultdict(dict)
    for r in jsonl(DATA / "replay.jsonl"):
        if r.get("phase") == a.phase and r.get("probs") and PRIMARY in r["probs"]:
            replay[r["critic_model"]][(r["run"], r["trial"], r["call_id"])] = r
    lab_by_key = {(c["run"], c["trial"], c["call_id"]): c for c in labelled}
    for critic, recs in sorted(replay.items()):
        pairs = [(recs[k]["probs"][PRIMARY], lab_by_key[k]["strict"], recs[k]["latency_ms"]) for k in recs if k in lab_by_key]
        if not pairs:
            continue
        m = critic_metrics([(p, y) for p, y, _ in pairs])
        lat = sorted(l for *_, l in pairs)
        md.append(f"| {critic} | replay, all arms (p50 {lat[len(lat) // 2]} ms) | {m['n']} | {m['positives']} | {fmt(m['auroc'])} | {fmt(m['ece'])} | "
                  f"{fmt(m['recall@0.5'])} | {fmt(m['precision@0.5'])} | {fmt(m['false_alarm_rate'])} |")

    md += ["", f"Strict = {sorted(STRICT)}; broad adds trajectory_error, unnecessary_call.",
           f"Labels: data/judge/{a.phase}/{a.labels_dir} (single blinded LLM judge; validate against human labels and the second judge)."]
    (out / "summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
