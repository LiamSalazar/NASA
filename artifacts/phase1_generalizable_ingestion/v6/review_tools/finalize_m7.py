"""Milestone 5 receipts: replays, reviews, metrics, target matrix, regressions.

    python finalize_m5.py REPLAY_ROOT RUNS...
REPLAY_ROOT/runN/{prepared.json.gz,replay.json} and REPLAY_ROOT/scored/runN/source_review.json
must exist; REPLAY_ROOT/cmp holds the exposed comparison and negatives receipts.
"""

import gzip
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

root = Path(sys.argv[1])
runs = sys.argv[2:]
head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
M = Path("artifacts/phase1_generalizable_ingestion/v6/milestone7")
out = M / f"rescored_{head}"
out.mkdir(parents=True, exist_ok=True)


def dump(path, data):
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


matrix, summary = {}, {}
for run in runs:
    target = out / f"ptfe_run{run}"
    (target / "review").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(root / f"run{run}" / "prepared.json.gz", target / "prepared.json.gz")
    replay = json.loads((root / f"run{run}" / "replay.json").read_text(encoding="utf-8"))
    dump(target / "replay.json", replay)
    review = json.loads((root / "scored" / f"run{run}" / "source_review.json").read_text(encoding="utf-8"))
    dump(target / "review" / "source_review.json", review)
    with tempfile.TemporaryDirectory() as tmp:
        plain = Path(tmp) / "prepared.json"
        with gzip.open(target / "prepared.json.gz", "rb") as src, open(plain, "wb") as dst:
            shutil.copyfileobj(src, dst)
        subprocess.run(
            ["uv", "run", "python", "scripts/score_scientific_review.py", str(plain),
             str(target / "review" / "source_review.json"), "--output", str(target / "review" / "scientific_metrics.json")],
            check=True, capture_output=True,
        )
    metrics = json.loads((target / "review" / "scientific_metrics.json").read_text(encoding="utf-8"))
    hashes = list(metrics["input_sha256"].values())
    metrics["input_sha256"] = {
        f"{target.as_posix()}/prepared.json.gz (decompressed)": hashes[0],
        f"{target.as_posix()}/review/source_review.json": hashes[1],
    }
    dump(target / "review" / "scientific_metrics.json", metrics)
    sample = review["proposal_sample"]
    accessible = [t for t in review["targets"] if t["outcome"] != "inaccessible"]
    summary[f"run{run}"] = {
        "input": replay["input"],
        "recall": f"{sum(t['outcome'] == 'correct' for t in accessible)}/{len(accessible)}",
        "precision": f"{sum(p['correct'] for p in sample)}/{len(sample)}",
        "critical": sum(p.get("critical", False) for p in sample),
    }
    for t in review["targets"]:
        matrix.setdefault(t["id"], {})[f"run{run}"] = t["outcome"]
dump(out / "target_matrix.json", {
    "kind": "PHASE1_V6_M7_PER_TARGET_OUTCOMES",
    "code": head,
    "runs": summary,
    "targets": matrix,
    "correct_in_every_run": sorted(k for k, v in matrix.items() if all(o == "correct" for o in v.values())),
    "never_correct": sorted(k for k, v in matrix.items() if not any(o == "correct" for o in v.values())),
})
for name in ("exposed_sources_comparison.json", "historical_negatives_receipt.json"):
    data = json.loads((root / "cmp" / name).read_text(encoding="utf-8"))
    if name.startswith("exposed"):
        data["kind"] = "PHASE1_V6_M7_EXPOSED_SOURCE_REPLAY_COMPARISON"
        data["note"] = (
            "Replays of the v4 application packages at the milestone-7 code; status counts are listed per source "
            "against the v5 closure. The development sources are measured on their new live runs instead "
            "(development_target_outcomes.json)."
        )
    dump(out / name, data)
print(json.dumps(summary, indent=1))
