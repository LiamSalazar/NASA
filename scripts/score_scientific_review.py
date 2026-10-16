"""Score an explicit source review without treating model output as scientific gold.

References and judgments are supplied by a reviewer. Unresolved quantities count
as retained evidence, separately from correct semantic recovery. Precision uses
an explicitly reviewed proposal sample, never the source-target denominator.
"""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


def score(prepared, review):
    package = prepared["package"]
    records = {r["id"]: r for r in package["scientific_extraction"]["records"]}
    records.update(
        {
            r["id"]: r
            for r in package["scientific_extraction"].get("pdf_table_quantity_proposals", [])
        }
    )
    seen = set()
    allowed = {"correct", "incorrect", "unresolved", "omitted", "inaccessible"}
    counts = Counter()
    by_kind = {}
    for target in review["targets"]:
        if target["id"] in seen or target["outcome"] not in allowed:
            raise ValueError("Duplicate target or invalid outcome")
        seen.add(target["id"])
        original = next(e for e in package["evidence"] if e["evidence_id"] == target["evidence_id"])
        if target["quote"] not in original["text"]:
            raise ValueError("Reference is not an exact original source span: " + target["id"])
        refs = target.get("proposal_ids", [])
        if target["outcome"] in {"correct", "unresolved", "incorrect"} and not refs:
            raise ValueError("Recovered target must identify reviewed proposals")
        for proposal in refs:
            r = records[proposal]
            if target["outcome"] == "correct" and r["status"] != "SOURCE_SUPPORTED":
                raise ValueError("Unresolved or rejected content cannot count as correct recovery")
            if target["outcome"] == "unresolved" and r["status"] != "UNRESOLVED":
                raise ValueError("Unresolved accounting requires an unresolved proposal")
        counts[target["outcome"]] += 1
        by_kind.setdefault(target["kind"], Counter())[target["outcome"]] += 1
    proposals = review["proposal_sample"]
    if len({p["proposal_id"] for p in proposals}) != len(proposals):
        raise ValueError("Duplicate precision judgment")
    for p in proposals:
        if records[p["proposal_id"]]["status"] != "SOURCE_SUPPORTED":
            raise ValueError("Accepted-proposal precision requires SOURCE_SUPPORTED records")
        if not isinstance(p["correct"], bool) or not p.get("reason"):
            raise ValueError("Each precision judgment requires a boolean and source rationale")
    correct = sum(p["correct"] for p in proposals)
    accessible = len(seen) - counts["inaccessible"]
    return {
        "basis": review["basis"],
        "target_count": len(seen),
        "outcomes": {k: counts[k] for k in sorted(allowed)},
        "by_kind": {k: dict(v) for k, v in by_kind.items()},
        "semantic_recall": {"numerator": counts["correct"], "denominator": accessible},
        "evidence_retention": {
            "numerator": counts["correct"] + counts["unresolved"],
            "denominator": accessible,
        },
        "reviewed_proposal_precision": {"numerator": correct, "denominator": len(proposals)},
        "incorrect_critical_assignments_in_sample": sum(
            not p["correct"] and p.get("critical", False) for p in proposals
        ),
        "unreviewed_supported_proposals": sum(
            r["status"] == "SOURCE_SUPPORTED" for r in records.values()
        )
        - len(proposals),
        "unresolved_is_confirmed_science": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prepared", type=Path)
    parser.add_argument("review", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = score(json.loads(args.prepared.read_text()), json.loads(args.review.read_text()))
    result["input_sha256"] = {
        str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in (args.prepared, args.review)
    }
    with args.output.open("x") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
