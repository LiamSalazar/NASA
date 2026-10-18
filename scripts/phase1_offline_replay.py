"""Offline replay of a saved Phase 1 package through the current validation code.

Every proposal kind is replayed: the saved raw Nemotron proposals go through the
current explicit-scope resolution and source validation, against the saved
original evidence and the saved document structure with today's deterministic
table linking. No model is called, no API key is needed, and the input receipt
is never modified. The result is a new prepared package that the existing
review scorer can read; a retained proposal still requires scientific review.

    uv run python scripts/phase1_offline_replay.py PREPARED.json.gz --output DIR
"""

import argparse
import gzip
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def replay(prepared, service):
    from nasa_fire_ai.ingestion.document_extraction import (
        Output,
        extraction_semantic,
        merge_output,
        resolve_explicit_scopes,
        validate_output,
    )
    from nasa_fire_ai.ingestion.document_structure import table_records
    from nasa_fire_ai.ingestion.pdf_quantities import pdf_table_quantities
    from nasa_fire_ai.ingestion.table_continuity import link_continuation_tables

    package = prepared["package"]
    extraction = package["scientific_extraction"]
    document = extraction["document"]
    document["detected_tables"] = link_continuation_tables(document["detected_tables"])
    output = extraction["raw_proposals"]
    resolve_explicit_scopes(output, document)
    consolidated = Output().model_dump()
    merge_output(consolidated, output)
    validation = validate_output(
        consolidated, package, document, extraction_semantic(service, package)
    )
    previous = {r["id"]: r["status"] for r in extraction["records"]}
    extraction.update(
        raw_proposals=consolidated,
        pdf_table_quantity_proposals=pdf_table_quantities(package, document),
        structured_table_records=table_records(document),
        **validation,
    )
    changes = Counter(
        (previous.get(r["id"], "NEW"), r["status"])
        for r in validation["records"]
        if previous.get(r["id"]) != r["status"]
    )
    return prepared, {
        "records": dict(Counter(r["status"] for r in validation["records"])),
        "by_kind": {
            kind: dict(Counter(r["status"] for r in validation["records"] if r["kind"] == kind))
            for kind in ("entities", "quantities", "statements", "relations", "concepts")
        },
        "status_changes": {f"{a}->{b}": n for (a, b), n in sorted(changes.items())},
        "records_no_longer_present": len(set(previous) - {r["id"] for r in validation["records"]}),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("prepared", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)  # exclusive: never overwrite receipts

    from nasa_fire_ai.evidence import EvidenceRegistry
    from nasa_fire_ai.services.curation import CurationService

    data = args.prepared.read_bytes()
    with gzip.open(args.prepared, "rt", encoding="utf-8") as handle:
        prepared = json.load(handle)
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False
    ).stdout.strip()
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", "src"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for name in ("domain", "ontology", "data/canonical"):
            shutil.copytree(ROOT / name, tmp / name)
        registry = EvidenceRegistry(tmp / "data/index/evidence.sqlite")
        try:
            prepared, summary = replay(prepared, CurationService(tmp, registry))
        finally:
            registry.db.close()
    with gzip.open(
        args.output / "prepared.json.gz", "wt", encoding="utf-8", newline="\n"
    ) as handle:
        json.dump(prepared, handle, ensure_ascii=False, sort_keys=True)
    receipt = {
        "kind": "PHASE1_FULL_OFFLINE_REPLAY",
        "input": args.prepared.as_posix(),
        "input_sha256": hashlib.sha256(data).hexdigest(),
        "git_head": head,
        "uncommitted_src_changes": bool(dirty),
        "model_calls": 0,
        "scientific_acceptance": "REQUIRES_SOURCE_REVIEW",
        **summary,
    }
    (args.output / "replay.json").write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
