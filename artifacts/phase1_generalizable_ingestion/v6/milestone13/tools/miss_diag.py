"""Target-by-target miss diagnosis for the milestone 12 runs (and their milestone 13 replays).

    python miss_diag.py REPO NFA_REPLAY_DIR OUT_JSON [MILESTONE TAG RUN,RUN]

MILESTONE (default milestone12), TAG (default 0a5a860) and the runs (default
r1,r2) name the live runs and the evaluation_b.json whose adjudication is used.

Each accessible frozen target that the run's adjudication did not count correct is put in one class:
  WINDOW_LOST            no finished model attempt carried the target's evidence
  NOT_PROPOSED           no record of the target's kind overlaps the target span
  PROPOSED_REJECTED      records of the kind overlap it, none SOURCE_SUPPORTED (first reason codes kept)
  ACCEPTED_MISGRADED     a SOURCE_SUPPORTED record overlaps it, but the adjudication did not count it correct
"""

import collections
import gzip
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
REPO, NFA, OUT = sys.argv[1:4]
MILESTONE, TAG, RUNS = (sys.argv[4:7] + ["milestone12", "0a5a860", "r1,r2"][len(sys.argv[4:7]):])[:3]
A = os.path.join(REPO, "artifacts/phase1_generalizable_ingestion")
M12 = os.path.join(A, "v6", MILESTONE)
evaluation = json.load(open(os.path.join(M12, "evaluation_b.json"), encoding="utf-8"))


def load(path):
    return json.load(gzip.open(path, "rt", encoding="utf-8"))


def overlaps(record, target):
    for s in (record.get("quantity_value_spans") or []) + (record.get("support_spans") or []):
        if (
            s.get("evidence_id") == target["evidence_id"]
            and s.get("start") is not None
            and s["start"] < target["end"]
            and s.get("end", s["start"]) > target["start"]
        ):
            return True
    return False


def reason(record):
    r = (record.get("reasons") or ["?"])[0]
    if isinstance(r, dict):
        r = r.get("code") or str(r)
    return str(r).split(";")[0][:90]


def classify(target, records, carried, correct):
    if target["id"] in correct:
        return None
    if target["id"] not in carried:
        return {"class": "WINDOW_LOST"}
    same = [r for r in records if r["kind"] == target["kind"] and overlaps(r, target)]
    other = sorted({r["kind"] for r in records if r["kind"] != target["kind"] and overlaps(r, target)})
    if not same:
        return {"class": "NOT_PROPOSED", "other_kinds_overlapping": other}
    supported = [r for r in same if r["status"] == "SOURCE_SUPPORTED"]
    if not supported:
        return {
            "class": "PROPOSED_REJECTED",
            "statuses": dict(collections.Counter(r["status"] for r in same)),
            "reasons": dict(collections.Counter(reason(r) for r in same).most_common(4)),
        }
    return {
        "class": "ACCEPTED_MISGRADED",
        "supported": [
            {
                "id": r["id"][-8:],
                "label": " ".join(
                    ((r["proposal"].get("label") or r["proposal"].get("text") or r["proposal"].get("expression") or ""))
                    .split()
                )[:100],
                "type": r["proposal"].get("class_id") or r["proposal"].get("relation") or r["proposal"].get("epistemic"),
            }
            for r in supported[:3]
        ],
    }


result = {"basis": __doc__.strip().splitlines()[0], "runs": {}}
summary = collections.Counter()
for source in ("ignition", "regulator", "textiles"):
    review = json.load(open(os.path.join(A, f"v4/independent_{source}/source_review.json"), encoding="utf-8"))
    targets = [t for t in review["targets"] if t["outcome"] != "inaccessible"]
    for run in RUNS.split(","):
        folder = os.path.join(M12, f"{source}_live_{TAG}_{run}")
        attempts = load(os.path.join(folder, "attempts.json.gz"))["attempts"]
        # Requests carry text in segments of their own ids, so a target's evidence
        # counts as sent when its printed words reach a finished request.
        sent = []

        def strings(x):
            if isinstance(x, str):
                sent.append(x)
            elif isinstance(x, dict):
                for v in x.values():
                    strings(v)
            elif isinstance(x, list):
                for v in x:
                    strings(v)

        for a in attempts:
            if a.get("state") == "FINISHED":
                strings(a.get("request"))
        text = " ".join(" ".join(sent).split()).lower()
        carried = set()
        for t in targets:
            words = " ".join(t["quote"].split()).lower()
            pieces = [words[i : i + 30] for i in range(0, max(1, len(words) - 29), 15)]
            if any(piece in text for piece in pieces):
                carried.add(t["id"])
        correct = set(evaluation["runs"][f"{source}_{run}"]["correct"])
        for label, path in (
            ("live", os.path.join(folder, "prepared.json.gz")),
            ("replay_m13", os.path.join(NFA, f"m12_{source}_{run}", "prepared.json.gz")),
        ):
            if not os.path.exists(path):
                continue
            records = [r for r in load(path)["package"]["scientific_extraction"]["records"] if not r.get("duplicate_of")]
            rows = {}
            for t in targets:
                c = classify(t, records, carried, correct)
                if c:
                    c.update(kind=t["kind"], quote=" ".join(t["quote"].split())[:160])
                    rows[t["id"]] = c
                    if label == "live":
                        summary[(source, c["class"])] += 1
            result["runs"][f"{source}_{run}_{label}"] = {
                "accessible": len(targets),
                "correct": len(correct),
                "missed": len(rows),
                "by_class": dict(collections.Counter(r["class"] for r in rows.values())),
                "targets": rows,
            }
result["summary_live"] = {f"{s}/{c}": n for (s, c), n in sorted(summary.items())}
json.dump(result, open(OUT, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
for k, v in result["runs"].items():
    print(k, v["correct"], "/", v["accessible"], v["by_class"])
print(result["summary_live"])
