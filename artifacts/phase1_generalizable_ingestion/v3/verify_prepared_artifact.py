"""Verify source fidelity, isolated RDF and publication isolation of service outputs."""

import argparse
import hashlib
import io
import json
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

from pyshacl import validate
from rdflib import Graph, Literal

from nasa_fire_ai.evidence import EvidenceRegistry
from nasa_fire_ai.query.native import NS, SemanticGraph
from nasa_fire_ai.services.curation import CurationService, project_package


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prepared", type=Path)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--previous", type=Path)
    args = parser.parse_args()
    prepared = json.loads(args.prepared.read_text())
    package = prepared["package"]
    registry = EvidenceRegistry(args.workspace / "data/index/evidence.sqlite")
    service = CurationService(args.workspace, registry)
    evidence = {e["evidence_id"]: e for e in package["evidence"]}
    extraction = package["scientific_extraction"]
    spans = [s for r in extraction["records"] for s in r["support_spans"]]
    span_checks = [
        evidence[s["evidence_id"]]["text"][s["start"] : s["end"]] == s["quote"]
        and evidence[s["evidence_id"]]["checksum"] == s["checksum"]
        and evidence[s["evidence_id"]]["source_id"] == s["source_id"]
        for s in spans
    ]
    originals = [
        {
            "name": item["name"],
            "sha256": item["sha256"],
            "exact": hashlib.sha256(
                (args.workspace / item["stored_input"]).read_bytes()
            ).hexdigest()
            == item["sha256"],
        }
        for item in package["inputs"]
    ]
    payload = service.export_package(package["id"])
    args.output.with_suffix(".zip").write_bytes(payload)
    with ZipFile(io.BytesIO(payload)) as archive:
        zip_hashes = {hashlib.sha256(archive.read(n)).hexdigest() for n in archive.namelist()}
    graph = SemanticGraph(service.property_registry(package))
    project_package(graph, package)
    for node in list(graph.graph.subjects(NS.canonical, None)):
        graph.graph.set((node, NS.canonical, Literal(False)))
    for node in list(graph.graph.subjects(NS.evidenceRef, None)):
        graph.graph.set((node, NS.reviewState, Literal("STAGED_CANDIDATE")))
    graph.graph.serialize(args.output.with_suffix(".ttl"), format="turtle")
    conforms, _, shacl = validate(
        graph.graph, shacl_graph=Graph().parse(args.workspace / "ontology/semantic_shapes.ttl")
    )
    args.output.with_suffix(".shacl.txt").write_text(str(shacl))
    source_errors = service.validate_originals(package)
    validation = service.validate(package)
    result = {
        "prepared": str(args.prepared),
        "prepared_sha256": hashlib.sha256(args.prepared.read_bytes()).hexdigest(),
        "digest": prepared["digest"],
        "previous_digest_equal": prepared["digest"]
        == json.loads(args.previous.read_text())["digest"]
        if args.previous
        else None,
        "new_model_calls_in_preparation": prepared["processing"]["new_model_calls"],
        "verification_model_calls": 0,
        "originals": originals,
        "original_source_integrity_errors": source_errors,
        "source_spans": {"denominator": len(spans), "correct": sum(span_checks)},
        "export_contains_original_bytes": all(o["sha256"] in zip_hashes for o in originals),
        "export_sha256": hashlib.sha256(payload).hexdigest(),
        "isolated_rdf_triples": len(graph.graph),
        "isolated_semantic_shacl": bool(conforms),
        "full_curation_ready": validation["ready"],
        "full_validation_errors": validation["errors"],
        "record_counts": dict(
            Counter(r["kind"] + ":" + r["status"] for r in extraction["records"])
        ),
        "review_requirement_counts": dict(
            Counter(r["kind"] for r in extraction["review_requirements"])
        ),
        "scientific_coverage": extraction["scientific_coverage"],
        "approvals": registry.db.execute("SELECT count(*) FROM research_approvals").fetchone()[0],
        "publications": registry.db.execute("SELECT count(*) FROM research_active").fetchone()[0],
        "sqlite_integrity": registry.db.execute("PRAGMA integrity_check").fetchone()[0],
        "scientific_acceptance": "NOT_INFERRED_FROM_RDF_SCHEMA_OR_SOURCE_SPAN_MATCHES",
    }
    with args.output.with_suffix(".json").open("x") as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False)
    assert all(span_checks) and all(o["exact"] for o in originals)
    assert not source_errors and result["export_contains_original_bytes"]
    assert result["approvals"] == result["publications"] == 0
    print(
        json.dumps(
            {
                k: v
                for k, v in result.items()
                if k not in ["scientific_coverage", "full_validation_errors"]
            }
        )
    )


if __name__ == "__main__":
    main()
