"""Seeded, difficulty-stratified task sample from the local Terminal-Bench 2.0 copy.

Usage (in WSL): python3 scripts/select_tasks.py <n> <seed> [--exclude a,b] > configs/<name>_tasks.txt
Allocation is proportional to difficulty counts (largest remainder), so the sample mirrors the benchmark mix.
"""
import argparse
import random
import tomllib
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("n", type=int)
ap.add_argument("seed", type=int)
ap.add_argument("--dataset", default=str(Path.home() / "datasets/terminal-bench"))
ap.add_argument("--exclude", default="")
a = ap.parse_args()

excluded = set(filter(None, a.exclude.split(",")))
by_diff: dict[str, list[str]] = {}
for f in sorted(Path(a.dataset).glob("*/task.toml")):
    if f.parent.name not in excluded:
        d = tomllib.loads(f.read_text())["metadata"]["difficulty"]
        by_diff.setdefault(d, []).append(f.parent.name)

total = sum(len(v) for v in by_diff.values())
quota = {d: a.n * len(v) / total for d, v in by_diff.items()}
alloc = {d: int(q) for d, q in quota.items()}
for d in sorted(quota, key=lambda d: quota[d] - alloc[d], reverse=True)[: a.n - sum(alloc.values())]:
    alloc[d] += 1

rng = random.Random(a.seed)
for d in sorted(by_diff):
    for t in sorted(rng.sample(by_diff[d], alloc[d])):
        print(t)
