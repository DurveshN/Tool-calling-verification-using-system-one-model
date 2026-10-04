#!/usr/bin/env bash
# Progress of the main run: batches/arms done, trials finished, pass counts, critic errors.
# Usage on the host: bash scripts/status.sh   (from this PC: ssh -i ~/.ssh/research_vm researcher@<ip> 'bash ~/prototype/scripts/status.sh')
ROOT="${ROOT:-$HOME/prototype}"  # repo checkout on the host
echo "now: $(date -u +%FT%TZ)  running: $(pgrep -fc 'scripts/run_main.sh') runner(s)"
grep -E "^=== " ~/main.log 2>/dev/null | tail -4
python3 - "$ROOT" <<'EOF'
import json, sys, pathlib
root = pathlib.Path(sys.argv[1])
rows = []
for prov in sorted(root.glob("runs/*/provenance.txt")):
    p = dict(l.split("=", 1) for l in prov.read_text().splitlines() if "=" in l)
    if p.get("phase") != "main":
        continue
    trials = [t for t in prov.parent.glob("jobs/*/*") if (t / "agent").is_dir()]
    done = [t for t in trials if (t / "result.json").exists()]
    passed = sum((t / "verifier/reward.txt").exists() and (t / "verifier/reward.txt").read_text().strip() == "1" for t in done)
    errs = sum(sum(1 for l in (t / "agent/critic.jsonl").open() if '"error"' in l) for t in trials if (t / "agent/critic.jsonl").exists())
    rows.append((p.get("batch"), p.get("arm"), len(done), len(trials), passed, errs, p.get("harbor_exit", "running")))
print("batch arm finished/started passed critic_errors exit")
for r in rows:
    print(*r)
tot = {a: sum(r[2] for r in rows if r[1] == a) for a in "ABC"}
print("trials finished per arm:", tot, "of 89 each")
EOF
