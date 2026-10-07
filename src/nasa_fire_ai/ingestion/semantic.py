"""Generic canonical ingestion and explicit one-time legacy projection.

Only this projection module knows legacy field names. Native ingestion takes generic
records; unknown column semantics enter the persistent review queue.
"""

import json
from pathlib import Path

import yaml

from nasa_fire_ai.ingestion.generic import profile_table, resolve_column
from nasa_fire_ai.query.native import SemanticGraph
from nasa_fire_ai.query.v2 import (
    GenericValue,
    PropertyDefinition,
    RelationDefinition,
    SemanticRegistry,
)


def load_semantic_registry(path: Path) -> SemanticRegistry:
    data = yaml.safe_load(path.read_text())
    registry = SemanticRegistry(
        [PropertyDefinition(**row) for row in data["properties"]],
        target_classes={key for key, meta in data["classes"].items() if meta.get("target")},
        information_classes={
            key for key, meta in data["classes"].items() if meta.get("information")
        },
        relations=[RelationDefinition(**row) for row in data["relations"]],
    )
    registry.class_metadata = data["classes"]
    registry.entities.update(data.get("entities", []))
    return registry


def project_legacy(root: Path, evidence_registry) -> SemanticGraph:
    """Deterministic additive projection. Never writes canonical or raw inputs."""
    registry = load_semantic_registry(root / "domain/semantic_registry.yaml")
    store = SemanticGraph(registry)
    config = yaml.safe_load((root / "domain/legacy_semantic_projection.yaml").read_text())
    records = json.loads((root / "data/canonical/records.json").read_text())
    runs = json.loads((root / "data/canonical/runs.json").read_text())
    run_records = {r["id"]: r for r in records if r["type"] == "ExperimentalRunRecord"}
    for record in records:
        cls = config["record_classes"].get(record["type"])
        if record["type"] == "SafetyStatementRecord":
            cls = config["statement_classes"][record["statement_type"]]
        elif record["type"] in config["statement_classes"]:
            cls = config["statement_classes"][record["type"]]
        if cls is None:
            continue
        refs = record["evidence_refs"]
        store.add_entity(
            record.get("id", record.get("statement_id")),
            cls,
            [r["evidence_id"] for r in refs],
            [r["source_id"] for r in refs],
            record,
        )
    for run in runs:
        eid = run["id"]
        refs = run["evidence_ids"]
        sources = [m["source_id"] for ref in refs if (m := evidence_registry.source_metadata(ref))]
        store.add_entity(eid, "ExperimentalRun", refs, sources, run)
        for field, relation in config["relations"].items():
            if run.get(field):
                # These are existing reviewed canonical labels, not new alias guesses.
                obj = run[field]
                registry.entities.add(obj)
                store.add_relation(eid, relation, obj, refs)
        investigation = run_records.get(eid, {}).get("investigation_id")
        if investigation:
            registry.entities.add(investigation)
            store.add_relation(eid, "belongsToInvestigation", investigation, refs)
        for field, meta in config["properties"].items():
            if run.get(field) is not None:
                definition = registry.properties[meta["property_id"]]
                value = (
                    GenericValue(canonical_value=run[field], canonical_unit=meta["unit"])
                    if definition.datatype == "numeric"
                    else GenericValue(reported_value=run[field])
                )
                store.add_value(
                    f"value:{eid}:{field}",
                    eid,
                    meta["property_id"],
                    value,
                    refs,
                    {"origin": "legacy_projection", "canonical_field": field},
                )
        for field, meta in config["ranges"].items():
            bounds = run.get(field)
            if bounds and all(x is not None for x in bounds):
                store.add_value(
                    f"value:{eid}:{field}",
                    eid,
                    meta["property_id"],
                    GenericValue(
                        lower=bounds[0],
                        upper=bounds[1],
                        canonical_unit=meta["unit"],
                    ),
                    refs,
                    {"origin": "legacy_projection", "canonical_field": field},
                )
    # Every registered document remains queryable as a document independently of runs.
    for row in evidence_registry.db.execute("SELECT document_id,source_id,title FROM documents"):
        refs = [
            r[0]
            for r in evidence_registry.db.execute(
                "SELECT evidence_id FROM passages WHERE document_id=?", (row[0],)
            )
        ]
        if refs:
            store.add_entity(
                row[0],
                "Document",
                refs,
                [row[1]],
                {"id": row[0], "title": row[2], "source_id": row[1]},
            )
            store.add_entity(row[0], "Publication", refs, [row[1]])
    return store


def ingest_generic_table(rows, source_id, evidence_ids, store, evidence_registry):
    """Authority comes only from the frozen registry; source IDs affect provenance only."""
    if len(rows) != len(evidence_ids):
        raise ValueError("one evidence reference is required per row")
    profiles = profile_table(rows)
    resolutions = [resolve_column(p, store.registry) for p in profiles]
    canonical_records = 0
    staging = []
    for profile, resolution in zip(profiles, resolutions, strict=True):
        if resolution.status != "CANONICAL":
            candidate = {
                "candidate_id": f"semantic:{source_id}:{profile.label}",
                "candidate_type": "PROPERTY",
                "raw_label": profile.label,
                "source_id": source_id,
                "evidence_id": evidence_ids[0] if evidence_ids else None,
                "resolution_status": "KNOWN_AMBIGUOUS"
                if resolution.status == "AMBIGUOUS"
                else "UNKNOWN",
                "provenance": {
                    "profiler": "generic-v1",
                    "column": profile.label,
                    "datatype": profile.datatype,
                    "unit": profile.raw_unit,
                },
            }
            evidence_registry.stage_semantic_candidate(candidate)
            staging.append(candidate)
    for i, (row, evidence_id) in enumerate(zip(rows, evidence_ids, strict=True)):
        subject = f"{source_id}:row:{i}"
        store.add_entity(subject, "ExperimentalRun", [evidence_id], [source_id])
        for profile, resolution in zip(profiles, resolutions, strict=True):
            if resolution.status != "CANONICAL" or not str(row.get(profile.label, "")).strip():
                continue
            definition = store.registry.properties[resolution.property_id]
            raw = str(row[profile.label]).strip()
            try:
                value = GenericValue(
                    reported_value=float(raw) if definition.datatype == "numeric" else raw,
                    reported_unit=profile.raw_unit,
                    raw_expression=raw,
                )
                store.add_value(
                    f"{subject}:{profile.label}",
                    subject,
                    resolution.property_id,
                    value,
                    [evidence_id],
                    {"column": profile.label},
                )
                canonical_records += 1
            except ValueError:
                candidate = {
                    "candidate_id": f"value:{subject}:{profile.label}",
                    "candidate_type": "VALUE",
                    "raw_label": raw,
                    "source_id": source_id,
                    "evidence_id": evidence_id,
                    "resolution_status": "UNKNOWN",
                    "provenance": {"column": profile.label, "reason": "incompatible value/unit"},
                }
                evidence_registry.stage_semantic_candidate(candidate)
                staging.append(candidate)
    return {
        "rows": len(rows),
        "columns": len(profiles),
        "canonical_records": canonical_records,
        "canonical_mappings": sum(r.status == "CANONICAL" for r in resolutions),
        "staging_records": len(staging),
        "resolutions": [r.__dict__ for r in resolutions],
    }
