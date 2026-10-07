"""Agreement between human labels (data/human/<phase>/labels.csv) and the LLM judge (key.json).

Usage: python scripts/human_agreement.py [--phase main] [--labels other.csv]
(--labels can point to an independent LLM annotator's file; report that as cross-model, not human, agreement.)
Sample is stratified by judge label (equal strict / broad-only / none), so kappa is reported per the sample, not the population.
"""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STRICT = {"fabricated_tool", "bad_args", "misread_output", "wrong_tool", "schema_violation"}
BROAD = STRICT | {"trajectory_error", "unnecessary_call"}
LABELS = BROAD | {"none"}


def kappa(pairs: list[tuple]) -> float:
    n = len(pairs)
    po = sum(x == y for x, y in pairs) / n
    ca, cb = Counter(x for x, _ in pairs), Counter(y for _, y in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n ** 2
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="main")
    ap.add_argument("--labels", help="labels CSV (default: data/human/<phase>/labels.csv, the human sheet)")
    o = ap.parse_args()
    d = ROOT / "data" / "human" / o.phase
    key = json.loads((d / "key.json").read_text(encoding="utf-8"))
    rows = [r for r in csv.DictReader(Path(o.labels or d / "labels.csv").open(encoding="utf-8")) if r["label"].strip()]
    bad = [r["id"] for r in rows if r["label"].strip() not in LABELS]
    if bad:
        raise SystemExit(f"unknown labels in {bad[:10]}; allowed: {sorted(LABELS)}")
    pairs = [(r["label"].strip(), key[r["id"]]["judge_label"]) for r in rows]
    print(f"annotator-labelled items: {len(pairs)} / {len(key)} (labels file: {o.labels or 'labels.csv'})")
    for name, f in (("strict", lambda l: l in STRICT), ("broad", lambda l: l in BROAD), ("full label", lambda l: l)):
        p = [(f(h), f(j)) for h, j in pairs]
        print(f"{name:10} agreement {sum(x == y for x, y in p) / len(p):.3f}  Cohen's kappa {kappa(p):.3f}")
    hs = sum(h in STRICT for h, _ in pairs)
    js = sum(j in STRICT for _, j in pairs)
    both = sum(h in STRICT and j in STRICT for h, j in pairs)
    print(f"strict: annotator {hs}, judge {js}, both {both} -> judge precision vs annotator {both / max(1, js):.3f}, judge recall {both / max(1, hs):.3f}")


if __name__ == "__main__":
    main()
