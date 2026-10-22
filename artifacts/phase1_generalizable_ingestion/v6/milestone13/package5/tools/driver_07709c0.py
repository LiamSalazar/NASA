"""Two fresh Sonnet rounds on the four sources at frozen 07709c0 (new request, Anthropic request size).

Each run gets its own new workspace (own SQLite cache) and receipt directory.
Spending brakes: 500,000 tokens per run (in the run script), stop if a round
passes 6 USD, never start a run that could take the total past 12 USD
(these two rounds together).
"""

import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO = Path(r"C:\Users\legom\Documents\proyects\nasa")
BASE = Path(r"C:\Users\legom\Documents\proyects\nasa-live\pkg5-07709c0")
ORIGINALS = Path(r"C:\Users\legom\Documents\proyects\nasa-live\originals")
COMMIT = "07709c0"
SOURCES = [
    ("ptfe", "20090043050"),
    ("ignition", "20250002114"),
    ("regulator", "20170003941"),
    ("textiles", "20260005493"),
]
ROUND1_LIMIT = 6.0
TOTAL_LIMIT = 6.0  # these two rounds together


def now():
    return datetime.now(UTC).isoformat()


def status(state):
    (BASE / "status.json").write_text(json.dumps(state, indent=2) + "\n", newline="\n")


def head():
    run = lambda *a: subprocess.run(  # noqa: E731
        ["git", *a], cwd=REPO, capture_output=True, text=True
    ).stdout.strip()
    return run("rev-parse", "HEAD"), run("status", "--porcelain", "--", "src", "scripts")


def main():
    env = dict(os.environ, SCIENCE_PROVIDER="anthropic", PYTHONUTF8="1")
    env.pop("ANTHROPIC_SCIENCE_MODEL", None)  # default claude-sonnet-5-5
    state = {"commit_expected": COMMIT, "launched_at": now(), "runs": [], "total_usd": 0.0}
    full, dirty = head()
    state["commit"] = full
    if not full.startswith(COMMIT) or dirty:
        state["stopped"] = f"code not frozen at {COMMIT}: {full} dirty={bool(dirty)}"
        status(state)
        return
    status(state)
    for rnd in (1, 2):
        folder = BASE / f"r{rnd}"
        folder.mkdir(exist_ok=True)
        for name, ntrs in SOURCES:
            full, dirty = head()
            if not full.startswith(COMMIT) or dirty:
                state["stopped"] = f"code changed before r{rnd} {name}: {full}"
                status(state)
                return
            # Worst case for the next run: 1.5 times the dearest so far (the
            # dearest Sonnet run seen cost 0.91 USD).
            worst = max([r.get("usd") or 0 for r in state["runs"]] + [1.0]) * 1.5
            if state["total_usd"] + worst > TOTAL_LIMIT:
                state["stopped"] = f"total cap: {state['total_usd']:.2f} + {worst:.2f} > {TOTAL_LIMIT}"
                status(state)
                return
            entry = {"round": rnd, "source": name, "started_at": now()}
            state["runs"].append(entry)
            status(state)
            out = folder / f"{name}_sonnet_{COMMIT}_r{rnd}"
            with (folder / f"{name}.log").open("w", encoding="utf-8", newline="\n") as log:
                code = subprocess.run(
                    [
                        "uv", "run", "python", "scripts/phase1_exposed_live_run.py",
                        "--pdf", str(ORIGINALS / f"{ntrs}.pdf"),
                        "--provenance-from",
                        f"artifacts/phase1_generalizable_ingestion/v4/independent_{name}/submission.json",
                        "--workspace", str(folder / f"{name}-workspace"),
                        "--directory", str(out),
                        "--timeout-seconds", "3600",
                        "--max-total-tokens", "500000",
                    ],
                    cwd=REPO, env=env, stdout=log, stderr=subprocess.STDOUT,
                ).returncode
            entry["completed_at"] = now()
            entry["exit_code"] = code
            summary = out / "summary.json"
            if summary.exists():
                timing = json.loads(summary.read_text(encoding="utf-8"))["timing"]
                entry["usd"] = timing["estimated_cost_usd"]
                entry["wall_seconds"] = timing["wall_seconds"]
            else:
                entry["usd"] = None
            state["total_usd"] = round(sum(r["usd"] or 0 for r in state["runs"]), 4)
            status(state)
            if sum(r["usd"] or 0 for r in state["runs"] if r["round"] == rnd) > ROUND1_LIMIT:
                state["stopped"] = f"round {rnd} passed {ROUND1_LIMIT} USD"
                status(state)
                return
        state[f"r{rnd}_completed_at"] = now()
        state[f"r{rnd}_usd"] = round(
            sum(r["usd"] or 0 for r in state["runs"] if r["round"] == rnd), 4
        )
        status(state)
    state["finished_at"] = now()
    status(state)


if __name__ == "__main__":
    sys.exit(main())
