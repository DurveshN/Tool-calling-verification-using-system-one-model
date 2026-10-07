"""Pre-registered significance tests for the main run (plan §0 primary analyses).

Inputs: data/tasks.jsonl, data/analysis/<phase>/<labels_dir>/calls_labelled.jsonl (from analyze.py), data/replay.jsonl
Output: results/<phase>/stats.md
Usage: python scripts/stats.py [--phase main] [--labels-dir labels_gpt6luna] [--reps 2000]
"""
import argparse
import json
import math
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
PRICES = json.loads((ROOT / "scripts" / "pricing.json").read_text(encoding="utf-8"))
ARMS = ("A", "B", "C")
PAIRS = (("A", "B"), ("A", "C"), ("B", "C"))
PRIMARY = "grounded_call"


def jsonl(p: Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text(encoding="utf-8").split("\n") if l.strip()]


def mcnemar_exact(b: int, c: int) -> float:
    """Two-sided exact McNemar p-value on discordant pairs (b, c)."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    p = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * p)


def holm(ps: dict) -> dict:
    order = sorted(ps, key=ps.get)
    out, running = {}, 0.0
    for i, k in enumerate(order):
        running = max(running, min(1.0, (len(order) - i) * ps[k]))
        out[k] = running
    return out


def auroc(scores: list[float], ys: list[int]) -> float:
    """Mann-Whitney AUROC with average ranks for ties."""
    pairs = sorted(zip(scores, ys))
    n1 = sum(ys)
    n0 = len(ys) - n1
    if not n1 or not n0:
        return float("nan")
    rank_sum, i = 0.0, 0
    while i < len(pairs):
        j = i
        while j < len(pairs) and pairs[j][0] == pairs[i][0]:
            j += 1
        avg = (i + j + 1) / 2
        rank_sum += avg * sum(y for _, y in pairs[i:j])
        i = j
    return (rank_sum - n1 * (n1 + 1) / 2) / (n1 * n0)


def ece(probs: list[float], ys: list[int], bins: int = 10) -> float:
    b = defaultdict(list)
    for p, y in zip(probs, ys):
        b[min(int(p * bins), bins - 1)].append((p, y))
    return sum(len(v) / len(ys) * abs(sum(p for p, _ in v) / len(v) - sum(y for _, y in v) / len(v)) for v in b.values())


def ci(vals: list[float]) -> tuple[float, float]:
    v = sorted(x for x in vals if not math.isnan(x))
    return v[int(0.025 * len(v))], v[int(0.975 * len(v)) - 1]


def fmt_ci(est: float, lo_hi: tuple[float, float], pct: bool = False) -> str:
    f = (lambda x: f"{100 * x:+.2f} pp") if pct else (lambda x: f"{x:+.3f}")
    return f"{f(est)} [{f(lo_hi[0])}, {f(lo_hi[1])}]"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="main")
    ap.add_argument("--labels-dir", default="labels_gpt6luna")
    ap.add_argument("--reps", type=int, default=2000)
    a = ap.parse_args()
    rng = random.Random(20261007)
    md = [f"# Significance tests: phase `{a.phase}` (judge labels: `{a.labels_dir}`)", "",
          f"Bootstrap: {a.reps} reps, resampling tasks with replacement (task-level clusters; all arms of a task move together). Seed 20261007.", ""]

    # 1. Task success: exact McNemar, Holm-corrected
    tasks = [t for t in jsonl(DATA / "tasks.jsonl") if t["phase"] == a.phase]
    reward = {(t["task"], t["arm"]): 1 if t["reward"] == 1.0 else 0 for t in tasks}
    task_names = sorted({t["task"] for t in tasks})
    md += ["## 1. Task success (secondary)", "", "| arm | passed |", "|---|---|"]
    md += [f"| {arm} | {sum(reward.get((t, arm), 0) for t in task_names)}/{len(task_names)} |" for arm in ARMS]
    raw = {}
    rows = []
    for x, y in PAIRS:
        b = sum(1 for t in task_names if reward.get((t, x), 0) == 1 and reward.get((t, y), 0) == 0)
        c = sum(1 for t in task_names if reward.get((t, x), 0) == 0 and reward.get((t, y), 0) == 1)
        raw[(x, y)] = mcnemar_exact(b, c)
        rows.append((x, y, b, c))
    adj = holm(raw)
    md += ["", "| comparison | only first passed | only second passed | exact McNemar p | Holm p |", "|---|---|---|---|---|"]
    md += [f"| {x} vs {y} | {b} | {c} | {raw[(x, y)]:.4f} | {adj[(x, y)]:.4f} |" for x, y, b, c in rows]

    # 2. Hallucination rates by arm (paired task-cluster bootstrap)
    calls = jsonl(DATA / "analysis" / a.phase / a.labels_dir / "calls_labelled.jsonl")
    agg = defaultdict(lambda: {"n": 0, "strict": 0, "broad": 0})
    for c in calls:
        g = agg[(c["task"], c["arm"])]
        g["n"] += 1
        g["strict"] += c["strict"]
        g["broad"] += c["broad"]
    timed_out = {(t["task"], t["arm"]) for t in tasks if t.get("exception") == "AgentTimeoutError"}

    def rates(sample: list[str], arm: str, metric: str, drop_timeouts: bool = False) -> tuple[float, float]:
        keys = [(t, arm) for t in sample if not (drop_timeouts and any((t, x) in timed_out for x in ARMS))]
        n = sum(agg[k]["n"] for k in keys)
        s = sum(agg[k][metric] for k in keys)
        return (s / n if n else float("nan")), (s / len(keys) if keys else float("nan"))

    for drop in (False, True):
        title = "all tasks" if not drop else "excluding tasks where any arm hit the agent timeout (runaway loops)"
        kept = [t for t in task_names if not (drop and any((t, x) in timed_out for x in ARMS))]
        md += ["", f"## 2{'b' if drop else 'a'}. Hallucination rates: {title} (n tasks = {len(kept)})", "",
               "| arm | calls | strict / call | strict / task | broad / call |", "|---|---|---|---|---|"]
        for arm in ARMS:
            n = sum(agg[(t, arm)]["n"] for t in kept)
            spc, spt = rates(kept, arm, "strict")
            bpc, _ = rates(kept, arm, "broad")
            md.append(f"| {arm} | {n} | {100 * spc:.2f}% | {spt:.2f} | {100 * bpc:.2f}% |")
        boots = defaultdict(list)
        for _ in range(a.reps):
            s = [rng.choice(kept) for _ in kept]
            for x, y in PAIRS:
                for metric in ("strict", "broad"):
                    rx, tx = rates(s, x, metric)
                    ry, ty = rates(s, y, metric)
                    boots[(x, y, metric, "call")].append(ry - rx)
                    boots[(x, y, metric, "task")].append(ty - tx)
        md += ["", "Differences (second minus first), 95% bootstrap CI:", "",
               "| comparison | Δ strict / call | Δ strict / task | Δ broad / call |", "|---|---|---|---|"]
        for x, y in PAIRS:
            ex_c = rates(kept, y, "strict")[0] - rates(kept, x, "strict")[0]
            ex_t = rates(kept, y, "strict")[1] - rates(kept, x, "strict")[1]
            ex_b = rates(kept, y, "broad")[0] - rates(kept, x, "broad")[0]
            md.append(f"| {y} − {x} | {fmt_ci(ex_c, ci(boots[(x, y, 'strict', 'call')]), True)} | "
                      f"{fmt_ci(ex_t, ci(boots[(x, y, 'strict', 'task')]))} | {fmt_ci(ex_b, ci(boots[(x, y, 'broad', 'call')]), True)} |")

    # 3. Critic quality on identical inputs (offline replay), paired
    lab = {(c["run"], c["trial"], c["call_id"]): c for c in calls}
    rep = defaultdict(dict)
    for r in jsonl(DATA / "replay.jsonl"):
        if r.get("phase") == a.phase and r.get("probs") and PRIMARY in r["probs"]:
            rep[r["critic_model"]][(r["run"], r["trial"], r["call_id"])] = r

    def critic_block(critics: list[str], title: str, ref: str) -> None:
        common = [k for k in lab if all(k in rep[c] for c in critics)]
        ys = [lab[k]["strict"] for k in common]
        sc = {c: [1 - rep[c][k]["probs"][PRIMARY] for k in common] for c in critics}
        by_task = defaultdict(list)
        for i, k in enumerate(common):
            by_task[lab[k]["task"]].append(i)
        tnames = list(by_task)
        nonlocal_md = ["", f"## {title} (n = {len(common)} calls, {sum(ys)} strict positives)", "",
                       "| critic | AUROC [95% CI] | ECE | recall@0.5 | precision@0.5 | false-alarm@0.5 | latency p50 / p95 | $ per 1k checks |",
                       "|---|---|---|---|---|---|---|---|"]
        boot = defaultdict(list)
        reps = max(200, a.reps // 4)
        for _ in range(reps):
            idx = [i for t in (rng.choice(tnames) for _ in tnames) for i in by_task[t]]
            yy = [ys[i] for i in idx]
            vals = {c: auroc([sc[c][i] for i in idx], yy) for c in critics}
            for c in critics:
                boot[c].append(vals[c])
                if c != ref:
                    boot[(c, "diff")].append(vals[c] - vals[ref])
        for c in critics:
            p_h = sc[c]
            flag = [p >= 0.5 for p in p_h]
            tp = sum(f and y for f, y in zip(flag, ys))
            fp = sum(f and not y for f, y in zip(flag, ys))
            lat = sorted(rep[c][k]["latency_ms"] for k in common)
            usage = [rep[c][k].get("usage") or {} for k in common]
            tin = sum(u.get("prompt_tokens", u.get("input_tokens", 0)) for u in usage)
            tout = sum(u.get("completion_tokens", u.get("output_tokens", 0)) for u in usage)
            price = PRICES.get(c, {"input": float("nan"), "output": float("nan")})
            cost_1k = (tin * price["input"] + tout * price["output"]) / 1e6 / len(common) * 1000
            lo, hi = ci(boot[c])
            nonlocal_md.append(
                f"| {c} | {auroc(p_h, ys):.3f} [{lo:.3f}, {hi:.3f}] | {ece(p_h, ys):.3f} | {tp / max(1, sum(ys)):.3f} | "
                f"{tp / max(1, tp + fp):.3f} | {fp / max(1, len(ys) - sum(ys)):.3f} | {lat[len(lat) // 2]} / {lat[int(0.95 * len(lat)) - 1]} ms | ${cost_1k:.3f} |")
        nonlocal_md += ["", f"AUROC differences vs `{ref}` (paired, task-cluster bootstrap, {reps} reps):", ""]
        for c in critics:
            if c != ref:
                d = auroc(sc[c], ys) - auroc(sc[ref], ys)
                nonlocal_md.append(f"- {c} − {ref}: {fmt_ci(d, ci(boot[(c, 'diff')]))}")
        md.extend(nonlocal_md)

    critic_block(["clef", "clef-flash", "gpt-5-mini"], "3a. Critic quality, all calls (offline replay)", "gpt-5-mini")
    if rep.get("gpt-4o"):
        critic_block(["clef", "clef-flash", "gpt-5-mini", "gpt-4o"], "3b. Critic quality, seeded gpt-4o sample", "gpt-4o")

    md += ["", "H1c (pre-registered): Clef non-inferior to the LLM critic if the lower CI bound of AUROC(clef) − AUROC(gpt-5-mini) > −0.05.",
           "Score = 1 − P(grounded_call); positive = strict hallucination (judge). ECE computed on that score.",
           f"Judge: {a.labels_dir} (single LLM judge; agreement with Opus on pilot 2: strict κ 0.685)."]
    out = ROOT / "results" / a.phase / "stats.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
