"""Blinded LLM judge over packet parts (CallMissed chat model; default gpt-6-luna).

For each packet part without a valid label file: send rubric + packet, parse JSON Lines, check that every
call number shown in the part has exactly one label from the rubric set, retry up to 2 times, then write
data/judge/<phase>/<labels_dir>/<part>.jsonl (same format as the subagent judges) or <part>.error.
Resumable: existing valid label files are skipped. Key: CALLMISSED_JUDGE_API_KEY, else CALLMISSED_API_KEY.

Usage: python3 scripts/judge_llm.py --phase main [--labels-dir labels] [--model gpt-6-luna] [--rpm 40] [--workers 4]
"""
import argparse
import json
import os
import re
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LABELS = {"none", "wrong_tool", "fabricated_tool", "bad_args", "schema_violation", "unnecessary_call", "misread_output", "trajectory_error"}
CALL_RE = re.compile(r"^### Call (\d+) ", re.MULTILINE)
SYSTEM_SUFFIX = "\n\nRespond with JSON Lines only (one JSON object per line), no prose and no code fences."


def load_env() -> None:
    env = ROOT / ".env"
    for line in env.read_text(encoding="utf-8").splitlines() if env.exists() else []:
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"'))


def redact(text: str) -> str:
    """Never write secret values (e.g. echoed in HTTP client errors) to disk."""
    for k, v in os.environ.items():
        if v and len(v) >= 8 and ("KEY" in k or "TOKEN" in k or k == "CF_ACCOUNT_ID"):
            for val in {v, v.strip()}:
                text = text.replace(val, f"<REDACTED:{k}>")
    return text


class Pacer:
    def __init__(self, rpm: float):
        self.gap, self.next, self.lock = 60.0 / rpm, 0.0, threading.Lock()

    def wait(self) -> None:
        with self.lock:
            now = time.time()
            at = max(now, self.next)
            self.next = at + self.gap
        time.sleep(max(0.0, at - now))


def chat(model: str, system: str, user: str, key: str, pacer: Pacer) -> tuple[str, dict]:
    body = json.dumps({"model": model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}).encode()
    for attempt in range(5):
        pacer.wait()
        req = urllib.request.Request("https://api.callmissed.com/v1/chat/completions", body,
                                     {"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                out = json.loads(r.read())
            return out["choices"][0]["message"]["content"] or "", out.get("usage", {})
        except urllib.error.HTTPError as e:
            if e.code != 429 and e.code < 500:
                raise
        except (urllib.error.URLError, TimeoutError, ConnectionError, json.JSONDecodeError):
            pass
        time.sleep(5 * 2 ** attempt)
    raise RuntimeError("judge request failed after retries")


def parse(text: str, pid: str, expected: list[int]) -> tuple[list[dict], str | None]:
    rows = []
    for line in text.splitlines():
        line = line.strip().strip("`")
        if not line.startswith("{"):
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    calls = {}
    for r in rows:
        if "call" in r and "label" in r:
            r["packet"] = pid
            if r["label"] not in LABELS:
                return rows, f"invalid label {r['label']!r} on call {r['call']}"
            calls[int(r["call"])] = r
    missing = [k for k in expected if k not in calls]
    if missing:
        return rows, f"missing labels for calls {missing[:10]} ({len(missing)} total)"
    extra = [r for r in rows if "call" not in r or int(r["call"]) in expected]  # drop labels for calls not in this part
    return extra, None


def judge_part(part: Path, out_dir: Path, rubric: str, model: str, key: str, pacer: Pacer) -> str:
    dest = out_dir / f"{part.stem}.jsonl"
    if dest.exists():
        return "skip"
    text = part.read_text(encoding="utf-8")
    pid = part.stem.split("_p")[0]
    expected = [int(k) for k in CALL_RE.findall(text)]
    err, usage_total = None, {}
    for attempt in range(3):
        try:
            reply, usage = chat(model, rubric + SYSTEM_SUFFIX, text, key, pacer)
        except Exception as e:  # noqa: BLE001 - record and retry
            err = f"request error: {e}"
            continue
        for k, v in usage.items():
            if isinstance(v, (int, float)):
                usage_total[k] = usage_total.get(k, 0) + v
        rows, err = parse(reply, pid, expected)
        missing = sorted(set(expected) - {int(r["call"]) for r in rows if "call" in r and "label" in r})
        if err and err.startswith("missing") and len(missing) <= 5:
            # The model occasionally skips a call in long parts: ask for just those calls, keep only their lines.
            note = (f"\n\n---\nYour previous answer omitted labels for calls {missing}. "
                    f"Output JSON Lines with label objects for ONLY these calls.")
            try:
                fill, usage = chat(model, rubric + SYSTEM_SUFFIX, text + note, key, pacer)
                for k, v in usage.items():
                    if isinstance(v, (int, float)):
                        usage_total[k] = usage_total.get(k, 0) + v
                keep = []
                for line in fill.splitlines():
                    try:
                        r = json.loads(line.strip().strip("`"))
                    except json.JSONDecodeError:
                        continue
                    if isinstance(r, dict) and "label" in r and int(r.get("call", -1)) in missing:
                        keep.append(json.dumps(r))
                rows, err = parse(reply + "\n" + "\n".join(keep), pid, expected)
            except Exception as e:  # noqa: BLE001
                err = f"fill-in request error: {e}"
        if err is None:
            dest.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
            (out_dir / f"{part.stem}.meta.json").write_text(json.dumps(
                {"model": model, "attempts": attempt + 1, "usage": usage_total, "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}))
            return "ok"
    (out_dir / f"{part.stem}.error").write_text(f"{redact(str(err))}\n", encoding="utf-8")
    return "error"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", required=True)
    ap.add_argument("--labels-dir", default="labels")
    ap.add_argument("--model", default="gpt-6-luna")
    ap.add_argument("--rpm", type=float, default=40)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--limit", type=int, help="judge at most N parts (testing)")
    a = ap.parse_args()
    load_env()
    key = (os.environ.get("CALLMISSED_JUDGE_API_KEY") or os.environ["CALLMISSED_API_KEY"]).strip()  # .env may have CRLF
    jdir = ROOT / "data" / "judge" / a.phase
    out_dir = jdir / a.labels_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    for stale in out_dir.glob("*.error"):
        stale.unlink()  # errors are retried on every run
    rubric = (ROOT / "judge" / "rubric.md").read_text(encoding="utf-8")
    parts = sorted((jdir / "packets").glob("*_p*.md"))[: a.limit]
    pacer = Pacer(a.rpm)
    counts: dict[str, int] = {}
    with ThreadPoolExecutor(a.workers) as ex:
        for i, status in enumerate(ex.map(lambda p: judge_part(p, out_dir, rubric, a.model, key, pacer), parts), 1):
            counts[status] = counts.get(status, 0) + 1
            if i % 10 == 0 or i == len(parts):
                print(f"{i}/{len(parts)} {counts}", flush=True)
    print("done", counts)


if __name__ == "__main__":
    main()
