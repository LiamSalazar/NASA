"""Best state of every frozen target over all graded live runs (0 model calls).

    python feasibility_runs.py OUT.json        (repo root)

Graded runs: NVIDIA evaluation B of milestones 10-13, the Anthropic pilot, and the
package 4 rounds. A target is correct in a run when that run's adjudication
counted it; otherwise its class comes from miss_diag (value spans, table cells,
lost windows). Replay recoveries (point A, block 3b) are listed apart: they are
not live runs.
"""
import glob, json, os, sys

V6 = "artifacts/phase1_generalizable_ingestion/v6"
sys.path.insert(0, os.path.join(V6, "milestone13/tools"))
from miss_diag import carried_by_stage, diagnose_records  # noqa: E402

RANK = ["CORRECT", "ACCEPTED_MISGRADED", "PROPOSED_REJECTED", "NOT_PROPOSED", "WINDOW_LOST"]
REPLAY_GAINS = {  # replay recoveries of saved outputs, adjudicated in point_a.md and fixes.md
    "ignition": {"quantities-14": "point A (3.1) and block 3b fix 3"},
    "regulator": {"statements-22": "point A (3.2b)", "statements-24": "point A (3.2b)"},
    "textiles": {"statements-22": "point A (3.2) and block 3b fix 2", "statements-24": "block 3b fix 2"},
}


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def graded_runs(source):
    runs = []
    for milestone, tag, evaluation in (
        ("milestone10", "96a2fa2", "evaluation_b_round1.json"),
        ("milestone11", "8e3f4e7", "evaluation_b.json"),
        ("milestone12", "0a5a860", "evaluation_b.json"),
        ("milestone13", "b4be17d", "evaluation_b.json"),
    ):
        for name, run in load(f"{V6}/{milestone}/{evaluation}")["runs"].items():
            if name.startswith(source + "_") and "x30b" not in name and run.get("correct") is not None:
                folder = f"{V6}/{milestone}/{source}_live_{tag}_{name.split('_')[1]}"
                runs.append((f"nvidia {milestone} {name}", folder, set(run["correct"])))
    pilot = load(f"{V6}/milestone13/pilot_anthropic/pilot_results.json")["runs"]
    for name, run in pilot.items():
        if name.startswith(source + "_"):
            (folder,) = glob.glob(f"{V6}/milestone13/pilot_anthropic/{name}_*")
            runs.append((f"pilot {name}", folder, set(run["correct"])))
    for commit, n in (("dc6f342", 1), ("a6d967b", 1), ("a6d967b", 2)):
        results = load(f"{V6}/milestone13/package4/review/{commit}_round{n}_results.json")
        folder = f"{V6}/milestone13/package4/{source}_sonnet_{commit}_r{n}"
        runs.append((f"sonnet package4 {commit} r{n}", folder, set(results[source]["correct"])))
    return runs


def main():
    out = {}
    for source in ("ignition", "regulator", "textiles"):
        review = load(f"artifacts/phase1_generalizable_ingestion/v4/independent_{source}/source_review.json")
        targets = [t for t in review["targets"] if t["outcome"] != "inaccessible"]
        best = {t["id"]: {"state": "WINDOW_LOST", "runs": []} for t in targets}
        detail = {t["id"]: {} for t in targets}
        runs = graded_runs(source)
        for label, folder, correct in runs:
            carried, outcomes = carried_by_stage(folder, targets)
            rows = diagnose_records(os.path.join(folder, "prepared.json.gz"), targets, carried, correct, outcomes)
            for t in targets:
                state = "CORRECT" if t["id"] in correct else rows[t["id"]]["class"]
                detail[t["id"]][label] = rows.get(t["id"], {"class": "CORRECT"})
                b = best[t["id"]]
                if RANK.index(state) < RANK.index(b["state"]):
                    best[t["id"]] = {"state": state, "runs": [label]}
                elif state == b["state"]:
                    b["runs"].append(label)
        out[source] = {
            "accessible": len(targets),
            "runs": [r[0] for r in runs],
            "targets": {
                t["id"]: {
                    "kind": t["kind"],
                    "expectation": t["expectation"],
                    "best_live": best[t["id"]],
                    "replay_gain": REPLAY_GAINS.get(source, {}).get(t["id"]),
                    "per_run": detail[t["id"]],
                }
                for t in targets
            },
        }
        live = sum(v["best_live"]["state"] == "CORRECT" for v in out[source]["targets"].values())
        replay = sum(
            v["best_live"]["state"] == "CORRECT" or bool(v["replay_gain"])
            for v in out[source]["targets"].values()
        )
        print(source, "runs", len(runs), "correct in some live run", live, "with replay", replay, "of", len(targets))
    with open(sys.argv[1], "w", encoding="utf-8", newline="\n") as handle:
        json.dump(out, handle, indent=1, ensure_ascii=False)


main()
