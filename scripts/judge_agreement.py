"""Agreement between two judges on the same packets (e.g. Opus subagents vs gpt-6-luna on pilot 2).

Usage: python scripts/judge_agreement.py --phase pilot2 --a labels --b labels_gpt6luna
Reports Cohen's kappa on the strict-hallucination binary, on the broad-error binary, and on the full label.
"""
import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STRICT = {"fabricated_tool", "bad_args", "misread_output", "wrong_tool", "schema_violation"}
BROAD = STRICT | {"trajectory_error", "unnecessary_call"}


def labels(d: Path) -> dict[tuple[str, int], str]:
    out = {}
    for f in d.glob("*.jsonl"):
        for line in f.read_text(encoding="utf-8").split("\n"):
            r = json.loads(line) if line.strip() else {}
            if "call" in r and "label" in r:
                out[(f.stem.split("_p")[0], int(r["call"]))] = r["label"]
    return out


def kappa(pairs: list[tuple[str, str]]) -> float:
    n = len(pairs)
    po = sum(x == y for x, y in pairs) / n
    ca, cb = Counter(x for x, _ in pairs), Counter(y for _, y in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n ** 2
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", required=True)
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    o = ap.parse_args()
    jdir = ROOT / "data" / "judge" / o.phase
    A, B = labels(jdir / o.a), labels(jdir / o.b)
    common = sorted(set(A) & set(B))
    print(f"calls labelled by both: {len(common)} (a: {len(A)}, b: {len(B)})")
    for name, f in (("strict", lambda l: str(l in STRICT)), ("broad", lambda l: str(l in BROAD)), ("full label", lambda l: l)):
        pairs = [(f(A[k]), f(B[k])) for k in common]
        agree = sum(x == y for x, y in pairs) / len(pairs)
        print(f"{name:10} agreement {agree:.3f}  Cohen's kappa {kappa(pairs):.3f}")
    print("strict positives: a =", sum(A[k] in STRICT for k in common), " b =", sum(B[k] in STRICT for k in common))


if __name__ == "__main__":
    main()
