"""Verify every run directory against its MANIFEST.sha256 (evidence integrity after copying).

Usage: python scripts/verify_manifests.py [runs_dir]
Post-hoc annotation files (INVALID.md, PHASE) are not in manifests by design.
"""
import hashlib
import sys
from pathlib import Path

runs = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "runs"
bad, ok, no_manifest = [], 0, []
for run in sorted(p for p in runs.iterdir() if p.is_dir() and not p.name.startswith("_")):
    m = run / "MANIFEST.sha256"
    if not m.exists():
        no_manifest.append(run.name)
        continue
    for line in m.read_text(encoding="utf-8").splitlines():
        digest, rel = line.split("  ", 1)
        f = run / rel
        if not f.exists():
            bad.append(f"{run.name}/{rel}: missing")
        elif hashlib.sha256(f.read_bytes()).hexdigest() != digest:
            bad.append(f"{run.name}/{rel}: hash mismatch")
        else:
            ok += 1
print(f"files verified: {ok}; problems: {len(bad)}; runs without manifest: {no_manifest or 'none'}")
for b in bad[:20]:
    print("  ", b)
sys.exit(1 if bad else 0)
