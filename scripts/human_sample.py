"""Build a blinded, stratified human-labelling sample to validate the LLM judge.

Strata (by judge label): strict hallucination / broad error only / none, equal size, split evenly across arms.
The sheet hides arm, judge label and critic verdicts. Writes:
  data/human/<phase>/sample.md   readable items (task, previous 3 calls, call, output)
  data/human/<phase>/labels.csv  id,label,secondary_label,notes  (fill in with rubric labels)
  data/human/<phase>/key.json    id -> run/trial/call_id/arm/judge label (do not open while labelling)
Usage: python scripts/human_sample.py [--phase main] [--labels-dir labels_gpt6luna] [--per-stratum 50] [--seed 20261007]
"""
import argparse
import csv
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
ARMS = ("A", "B", "C")


def clip(s: str, n: int) -> str:
    s = (s or "").replace("\x00", "\\0")  # binary tool output: keep NUL visible but editor-safe
    return s if len(s) <= n else s[: n - 600] + f"\n[...{len(s) - n} chars omitted...]\n" + s[-500:]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="main")
    ap.add_argument("--labels-dir", default="labels_gpt6luna")
    ap.add_argument("--per-stratum", type=int, default=50)
    ap.add_argument("--seed", type=int, default=20261007)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    path = DATA / "analysis" / a.phase / a.labels_dir / "calls_labelled.jsonl"
    calls = [json.loads(l) for l in path.read_text(encoding="utf-8").split("\n") if l.strip()]
    strata = {
        "strict": [c for c in calls if c["strict"]],
        "broad_only": [c for c in calls if c["broad"] and not c["strict"]],
        "none": [c for c in calls if not c["broad"]],
    }
    picked = []
    for name, pool in strata.items():
        per_arm = [a.per_stratum // 3 + (1 if i < a.per_stratum % 3 else 0) for i in range(3)]
        for arm, k in zip(ARMS, per_arm):
            arm_pool = [c for c in pool if c["arm"] == arm]
            picked += [(name, c) for c in rng.sample(arm_pool, min(k, len(arm_pool)))]
    rng.shuffle(picked)

    out = DATA / "human" / a.phase
    out.mkdir(parents=True, exist_ok=True)
    md, key = ["# Human labelling sheet", "",
               "Label each call with the rubric in `judge/rubric.md` (same labels and decision rules as the judge).",
               "Arm, judge label and critic verdicts are hidden. Record answers in `labels.csv`.", ""], {}
    for i, (stratum, c) in enumerate(picked, 1):
        hid = f"H{i:03d}"
        st = c.get("critic_state") or {}
        key[hid] = {"run": c["run"], "trial": c["trial"], "call_id": c["call_id"], "arm": c["arm"], "task": c["task"],
                    "stratum": stratum, "judge_label": c["judge"]["label"], "judge_secondary": c["judge"].get("secondary_label")}
        md += [f"---", f"## {hid}", "", "**Task:**", "", "~~~~", clip(st.get("task", ""), 2500), "~~~~", "",
               "**Previous calls (most recent last, outputs truncated):**", ""]
        for r in st.get("recent", []):
            md += [f"- `{r['tool']}` {json.dumps(r['args'], ensure_ascii=False)[:400]}", "", "  ~~~~", "  " + clip(r.get("output") or "", 500).replace("\n", "\n  "), "  ~~~~", ""]
        md += [f"**Call to label:** `{c['tool']}`", "", "```json", json.dumps(c["args"], indent=1, ensure_ascii=False)[:4000], "```", "",
               "**Output:**", "", "~~~~", clip(str(c.get("output") or ""), 6000), "~~~~", ""]
    (out / "sample.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (out / "key.json").write_text(json.dumps(key, indent=1), encoding="utf-8")
    with (out / "labels.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "label", "secondary_label", "notes"])
        for hid in key:
            w.writerow([hid, "", "", ""])
    print(f"{len(key)} items -> {out} (strata: { {s: sum(1 for v in key.values() if v['stratum'] == s) for s in strata} })")


if __name__ == "__main__":
    main()
