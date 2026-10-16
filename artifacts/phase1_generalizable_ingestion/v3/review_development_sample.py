"""Reproducible developer source checks; never part of scientific ingestion."""

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path


def norm(value):
    return " ".join(value.lower().split())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prepared", type=Path)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    reference = json.loads(Path(__file__).with_name("luci_development_reference.json").read_text())
    package = json.loads(args.prepared.read_text())["package"]
    extraction = package["scientific_extraction"]
    evidence = {e["evidence_id"]: e for e in package["evidence"]}
    for original in package["inputs"]:
        assert (
            hashlib.sha256((args.workspace / original["stored_input"]).read_bytes()).hexdigest()
            == original["sha256"]
        )
    source_checks = []
    labels = defaultdict(set)
    for record in extraction["records"]:
        if record["kind"] == "entities" and record.get("entity_id"):
            labels[record["entity_id"]].add(norm(record["proposal"]["label"]))
        for span in record["support_spans"]:
            original = evidence[span["evidence_id"]]
            source_checks.append(
                original["text"][span["start"] : span["end"]] == span["quote"]
                and original["checksum"] == span["checksum"]
                and original["source_id"] == span["source_id"]
            )
    assert all(source_checks)
    results = []
    for gold in reference["items"]:
        assert any(
            e["page"] == gold["page"] and e["text"] == gold["original_page_text"]
            for e in evidence.values()
        )
        matching = []
        for r in extraction["records"]:
            if r["kind"] != gold["kind"] or not any(
                s["page"] == gold["page"] for s in r["support_spans"]
            ):
                continue
            item = r["proposal"]
            if any(
                norm(str(item.get(k, ""))) != norm(str(gold[k]))
                for k in ("class_id", "label", "expression", "unit", "epistemic", "relation")
                if k in gold
            ):
                continue
            if "text_contains" in gold and norm(gold["text_contains"]) not in norm(
                item.get("text", "")
            ):
                continue
            if "label_contains_any" in gold and not any(
                norm(n) in norm(item["label"]) for n in gold["label_contains_any"]
            ):
                continue
            scopes = r.get("scope", []) or [r.get("subject")]
            if "subject_label" in gold and not any(
                norm(gold["subject_label"]) in labels[s] for s in scopes
            ):
                continue
            if "object_id" in gold and r.get("object") != gold["object_id"]:
                continue
            matching.append(r)
        supported = [r["id"] for r in matching if r["status"] == "SOURCE_SUPPORTED"]
        pending = [
            r["id"]
            for r in matching
            if r["status"] == "UNRESOLVED"
            and set(r["reasons"]) <= {"QUANTITY_SEMANTICS_OR_UNIT_UNRESOLVED"}
        ]
        results.append(
            {
                "reference_id": gold["id"],
                "kind": gold["kind"],
                "source_page": gold["page"],
                "source_supported": supported,
                "grounded_quantity_pending_semantics": pending,
                "other_unresolved": [
                    r["id"]
                    for r in matching
                    if r["status"] == "UNRESOLVED" and r["id"] not in pending
                ],
                "rejected": [r["id"] for r in matching if r["status"] == "REJECTED"],
            }
        )
    metrics = {}
    for kind in sorted({r["kind"] for r in results}):
        rows = [r for r in results if r["kind"] == kind]
        metrics[kind] = {
            "denominator": len(rows),
            "source_supported_recovered": sum(bool(r["source_supported"]) for r in rows),
            "grounded_pending_semantics": sum(
                not r["source_supported"] and bool(r["grounded_quantity_pending_semantics"])
                for r in rows
            ),
            "omitted_or_other_unresolved": sum(
                not r["source_supported"] and not r["grounded_quantity_pending_semantics"]
                for r in rows
            ),
        }
    report = {
        "prepared": str(args.prepared),
        "prepared_sha256": hashlib.sha256(args.prepared.read_bytes()).hexdigest(),
        "adjudication": reference["adjudicator"],
        "boundary": reference["boundary"],
        "original_span_checks": {"correct": sum(source_checks), "denominator": len(source_checks)},
        "limited_sample_recall_counts": metrics,
        "precision": "NOT_COMPREHENSIVELY_ADJUDICATED; do not infer precision from matching gold positives",
        "items": results,
    }
    with args.output.open("x") as f:
        json.dump(report, f, indent=2)
    print(json.dumps(metrics))


if __name__ == "__main__":
    main()
