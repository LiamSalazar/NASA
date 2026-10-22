"""The nine directive §11 metrics from saved receipts, with 95 % Wilson intervals.

    python phase1_metrics.py OUT.json
    python phase1_metrics.py OUT.json --round RESULTS.json TARGETS.json PTFE_METRICS.json         [--variability NAME=RESULTS.json ...]

Reads only committed receipts (no replay, no model). By default (evaluation A): the
point A PTFE scorer metrics, the point A per-target outcomes of the other sources,
the round B adjudication with the point A precision judgments, and the milestone 12
live runs for run-to-run variability. With --round (evaluation B, one fresh live
round): that round's results (precision per source), per-target outcomes and PTFE
scorer metrics, and the recall of the named rounds for variability. Nothing here
changes a judgment.
"""

import argparse
import json
import math
from collections import Counter
from pathlib import Path

M13 = Path(__file__).resolve().parents[1]


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def wilson(k, n, z=1.96):
    if not n:
        return None
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return {
        "numerator": k,
        "denominator": n,
        "value": round(p, 3),
        "ci95": [round(centre - half, 3), round(centre + half, 3)],
    }


# Precision after point A: active records and those judged incorrect (point_a.md).
PRECISION = {
    "textiles": (19, 23),
    "regulator": (21, 30),
    "ignition": (86, 114),
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("out")
    parser.add_argument("--round", nargs=3, metavar=("RESULTS", "TARGETS", "PTFE_METRICS"))
    parser.add_argument("--variability", nargs="*", default=[], metavar="NAME=RESULTS")
    args = parser.parse_args()
    precision = PRECISION
    if args.round:
        results = read_json(args.round[0])
        three = read_json(args.round[1])
        ptfe = read_json(args.round[2])
        precision = {
            src: tuple(int(n) for n in results[src]["precision"].split("/"))
            for src in three["sources"]
        }
    else:
        ptfe = read_json(M13 / "point_a/ptfe_r1_metrics.json")
        three = read_json(M13 / "point_a/targets_three_sources.json")
    diagnosis = read_json(M13 / "target_miss_diagnosis.json")
    per_doc = {}
    o = ptfe["outcomes"]
    acc = ptfe["semantic_recall"]["denominator"]
    per_doc["ptfe"] = {
        "recall": wilson(o["correct"], acc),
        "precision": wilson(*ptfe["reviewed_proposal_precision"].values()),
        "evidence_retention": wilson(*ptfe["evidence_retention"].values()),
        "correctly_unresolved": wilson(ptfe["correctly_held_targets"]["count"], acc),
        "unresolved": wilson(o["unresolved"], acc),
        "omissions": wilson(o["omitted"], acc),
        "critical": ptfe["incorrect_critical_assignments_in_sample"],
        "by_kind": ptfe["by_kind"],
    }
    for src, data in three["sources"].items():
        c = Counter(data["targets"].values())
        acc = data["accessible"]
        by_kind = {}
        for target, outcome in data["targets"].items():
            if outcome != "inaccessible":
                kind = target.rsplit("-", 1)[0]
                by_kind.setdefault(kind, Counter())[outcome] += 1
        per_doc[src] = {
            "recall": wilson(c["correct"], acc),
            "precision": wilson(*precision[src]),
            "evidence_retention": wilson(c["correct"] + c["unresolved"], acc),
            "correctly_unresolved": None,  # no hold assessment in these adjudications
            "unresolved": wilson(c["unresolved"], acc),
            "omissions": wilson(c["omitted"], acc),
            "critical": 0,
            "by_kind": {k: dict(v) for k, v in by_kind.items()},
        }
    pooled = {}
    for metric in ("recall", "precision", "evidence_retention", "omissions"):
        k = sum(d[metric]["numerator"] for d in per_doc.values())
        n = sum(d[metric]["denominator"] for d in per_doc.values())
        pooled[metric] = wilson(k, n)
    categories = {}
    for d in per_doc.values():
        for kind, counts in d["by_kind"].items():
            cat = categories.setdefault(kind, Counter())
            for outcome, n in counts.items():
                cat[outcome] += n
    per_category = {
        kind: wilson(c.get("correct", 0), sum(n for o, n in c.items() if o != "inaccessible"))
        for kind, c in categories.items()
        if sum(n for o, n in c.items() if o != "inaccessible")
    }
    variability = {}
    for item in args.variability:
        name, path = item.split("=", 1)
        for src, data in read_json(path).items():
            variability.setdefault(src, {})[name] = data["recall"]
    for run, data in [] if args.round else diagnosis["runs"].items():
        if run.endswith("_live_m12"):
            src = run.split("_")[0]
            variability.setdefault(src, {})[run.split("_")[1]] = (
                f"{data['correct']}/{data['accessible']}"
            )
    for name in () if args.round else ("r1", "r2"):
        m = read_json(M13 / f"point_a/ptfe_{name}_m12_metrics.json")
        r = m["semantic_recall"]
        variability.setdefault("ptfe", {})[name] = f"{r['numerator']}/{r['denominator']}"
    basis = (
        "Evaluation B, one fresh live round: " + three["basis"]
        if args.round
        else "Evaluation A only (saved outputs revalidated at point A, 0 model calls)."
    )
    result = {
        "basis": basis + " Development sources, so these are regression measurements, not "
        "evidence of generalization (directive §12, §19). UNRESOLVED never counts as recovered.",
        "targets": {"precision": 0.95, "recall": 0.80, "critical": 0},
        "per_document": per_doc,
        "pooled": pooled,
        "critical_errors_total": sum(d["critical"] for d in per_doc.values()),
        "per_category_recall": per_category,
        ("run_to_run_recall_package4_live" if args.round else "run_to_run_recall_m12_live"): (
            variability
        ),
    }
    # LF on every platform, whatever the local default.
    Path(args.out).write_text(
        json.dumps(result, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
    )
    for src, d in per_doc.items():
        print(
            src,
            "recall",
            d["recall"]["value"],
            d["recall"]["ci95"],
            "precision",
            d["precision"]["value"],
            d["precision"]["ci95"],
        )
    print("pooled", {k: (v["value"], v["ci95"]) for k, v in pooled.items()})
    print(
        "category",
        {k: (v["value"], v["numerator"], v["denominator"]) for k, v in per_category.items()},
    )
    print("variability", variability)


if __name__ == "__main__":
    main()
