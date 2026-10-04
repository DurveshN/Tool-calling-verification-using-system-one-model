"""Redact secret values from a run directory, then write MANIFEST.sha256 (evidence freeze).

Usage: python3 scripts/redact_and_manifest.py runs/<run_dir>
Secrets are read from the environment (CALLMISSED_API_KEY, CF_API_TOKEN, CF_ACCOUNT_ID).
"""
import hashlib
import os
import sys
from pathlib import Path

SECRET_VARS = ("CALLMISSED_API_KEY", "CALLMISSED_CRITIC_API_KEY", "CALLMISSED_REPLAY_API_KEY", "CF_API_TOKEN", "CF_ACCOUNT_ID")


def main(run_dir: Path) -> None:
    secrets = {v: os.environ[v].encode() for v in SECRET_VARS if os.environ.get(v)}
    redacted = 0
    for f in sorted(p for p in run_dir.rglob("*") if p.is_file() and p.name != "MANIFEST.sha256"):
        data = f.read_bytes()
        new = data
        for name, val in secrets.items():
            new = new.replace(val, f"<REDACTED:{name}>".encode())
        if new != data:
            f.write_bytes(new)
            redacted += 1
    lines = []
    for f in sorted(p for p in run_dir.rglob("*") if p.is_file() and p.name != "MANIFEST.sha256"):
        lines.append(f"{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.relative_to(run_dir).as_posix()}")
    (run_dir / "MANIFEST.sha256").write_text("\n".join(lines) + "\n")
    print(f"redacted files: {redacted}; manifest entries: {len(lines)}")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
