"""Read-only export of unique real provider attempts; no scientific acceptance scoring."""

import argparse
import gzip
import hashlib
import json
import sqlite3
from collections import Counter
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("directories", nargs="+", type=Path)
    args = parser.parse_args()
    rows = []
    for directory in args.directories:
        db_path = directory / "workspace/data/index/evidence.sqlite"
        with sqlite3.connect(f"file:{db_path}?mode=ro", uri=True) as db:
            assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
            for key, payload, created in db.execute(
                "SELECT cache_key,payload_json,created_at FROM phase3_cache "
                "WHERE cache_kind='scientific_document_attempt' ORDER BY cache_key"
            ):
                rows.append(
                    {
                        "workspace": str(directory),
                        "attempt_key": key,
                        "journal_last_write_at": created,
                        "payload_sha256": hashlib.sha256(payload.encode()).hexdigest(),
                        "attempt": json.loads(payload),
                    }
                )
    assert len({r["attempt_key"] for r in rows}) == len(rows)
    summary = {
        "boundary": "Unique journal keys, not duplicate prepared/export snapshots. Provider probes separate.",
        "attempts": len(rows),
        "states": {},
        "outcomes": {},
        "finish_reasons": {},
        "measured_usage_tokens": 0,
        "attempts_with_measured_usage": 0,
        "attempts_without_measured_usage": 0,
        "recorded_transport_seconds": 0,
        "latency_seconds_range": None,
        "reported_scientific_complete": False,
        "cost_usd": "Account-specific credits/pricing unavailable; no paid plan/route changes.",
    }
    states, outcomes, finishes, workspaces = Counter(), Counter(), Counter(), Counter()
    latencies = []
    for row in rows:
        r = row["attempt"]
        outcome = r.get("outcome", {})
        transport = outcome.get("transport", r.get("transport", {}))
        usage = r.get("usage") or transport.get("usage")
        states[r["state"]] += 1
        outcomes[outcome.get("model", "UNKNOWN_INCOMPLETE_JOURNAL")] += 1
        finishes[outcome.get("finish_reason") or transport.get("finish_reason") or "UNKNOWN"] += 1
        workspaces[row["workspace"]] += 1
        if usage and usage.get("total_tokens") is not None:
            summary["measured_usage_tokens"] += usage["total_tokens"]
            summary["attempts_with_measured_usage"] += 1
        else:
            summary["attempts_without_measured_usage"] += 1
        if transport.get("duration_seconds") is not None:
            latencies.append(transport["duration_seconds"])
    summary.update(
        states=dict(states),
        outcomes=dict(outcomes),
        finish_reasons=dict(finishes),
        workspaces=dict(workspaces),
        recorded_transport_seconds=sum(latencies),
        latency_seconds_range=[min(latencies), max(latencies)] if latencies else None,
    )
    with (
        args.output.with_suffix(".jsonl.gz").open("xb") as raw,
        gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as target,
    ):
        for row in rows:
            target.write((json.dumps(row, ensure_ascii=False) + "\n").encode())
    with args.output.with_suffix(".json").open("x") as target:
        json.dump(summary, target, indent=2)
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
