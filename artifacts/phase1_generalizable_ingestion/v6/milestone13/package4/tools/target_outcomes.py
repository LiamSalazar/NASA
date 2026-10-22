"""Per-target outcomes of one package 4 round, in the point A targets_three_sources.json shape.

    python target_outcomes.py COMMIT ROUND OUT.json   (repo root)

correct = the round's adjudication; for the other targets, the best status of any
record of the same kind overlapping the target span: UNRESOLVED -> unresolved,
REJECTED or a supported record not judged correct -> incorrect_or_rejected,
none -> omitted (the point A rule).
"""
import collections, gzip, json, os, sys
commit, rnd, out = sys.argv[1:4]
B = os.environ.get("PKG_DIR", f"../nasa-live/pkg4-{commit}")
A = "artifacts/phase1_generalizable_ingestion"
results = json.load(open(f"{B}/review/round{rnd}_results.json", encoding="utf-8"))


def overlaps(r, t):
    return any(
        s.get("evidence_id") == t["evidence_id"] and s.get("start") is not None
        and s["start"] < t["end"] and s.get("end", s["start"]) > t["start"]
        for s in (r.get("quantity_value_spans") or []) + (r.get("support_spans") or [])
    )


sources = {}
for source in ("textiles", "regulator", "ignition"):
    pkg = json.load(gzip.open(f"{B}/r{rnd}/{source}_sonnet_{commit}_r{rnd}/prepared.json.gz", "rt", encoding="utf-8"))["package"]
    recs = [r for r in pkg["scientific_extraction"]["records"] if not r.get("duplicate_of")]
    review = json.load(open(f"{A}/v4/independent_{source}/source_review.json", encoding="utf-8"))
    correct = set(results[source]["correct"])
    targets = {}
    for t in review["targets"]:
        if t["outcome"] == "inaccessible":
            targets[t["id"]] = "inaccessible"
            continue
        if t["id"] in correct:
            targets[t["id"]] = "correct"
            continue
        statuses = {r["status"] for r in recs if r["kind"] == t["kind"] and overlaps(r, t)}
        targets[t["id"]] = (
            "unresolved" if "UNRESOLVED" in statuses
            else "incorrect_or_rejected" if statuses else "omitted"
        )
    c = collections.Counter(targets.values())
    sources[source] = {"accessible": len(targets) - c["inaccessible"], "targets": targets, "counts": dict(c)}
json.dump({"basis": __doc__.strip().splitlines()[0] + f" ({commit} round {rnd}).", "sources": sources},
          open(out, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
print({s: v["counts"] for s, v in sources.items()})
