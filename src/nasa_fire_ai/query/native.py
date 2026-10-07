"""Native generic RDF execution. No V1 execution or legacy field mappings.

Scientific identities are supplied exclusively by the registry and graph. Operational
evidence locations remain in EvidenceRegistry; graph references are opaque evidence IDs.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from time import perf_counter
from urllib.parse import quote, unquote

from rdflib import RDF, Graph, Literal, Namespace, URIRef

from nasa_fire_ai.models import EvidenceBundle, ExperimentComparison, QueryIntent
from nasa_fire_ai.query.v2 import (
    GenericValue,
    QueryIntentV2,
    SemanticRegistry,
    evaluate_constraint,
)

NS = Namespace("https://example.org/nasa-fire-safety/semantic/")


def node(identity: str) -> URIRef:
    return NS[quote(identity, safe="")]


def identity(uri: URIRef) -> str:
    return unquote(str(uri).removeprefix(str(NS)))


class SemanticGraph:
    """Additive graph with reified relations and values, independent of source format."""

    def __init__(self, registry: SemanticRegistry, graph: Graph | None = None):
        self.registry = registry
        self.graph = graph if graph is not None else Graph()

    def add_entity(self, entity_id, class_id, evidence_ids, source_ids=(), payload=None):
        if class_id not in self.registry.target_classes | self.registry.information_classes:
            raise LookupError(class_id)
        if not evidence_ids:
            raise ValueError("canonical entities require evidence")
        subject = node(entity_id)
        self.registry.entities.add(entity_id)
        self.graph.add((subject, RDF.type, node(class_id)))
        self.graph.add((subject, NS.canonical, Literal(True)))
        for eid in evidence_ids:
            self.graph.add((subject, NS.evidenceRef, Literal(eid)))
        for sid in source_ids:
            self.graph.add((subject, NS.source, node(sid)))
        if payload is not None:
            self.graph.add((subject, NS.payload, Literal(json.dumps(payload, sort_keys=True))))

    def add_relation(self, subject, relation, obj, evidence_ids):
        definition = self.registry.relations.get(relation)
        if definition is None or definition.status != "CANONICAL":
            raise LookupError(relation)
        if subject not in self.registry.entities or obj not in self.registry.entities:
            raise LookupError("relation endpoints must be reviewed entities")
        if not evidence_ids:
            raise ValueError("canonical relation requires evidence")
        record = node(f"relation:{subject}:{relation}:{obj}")
        for pred, value in (
            (RDF.type, NS.SemanticRelation),
            (NS.subject, node(subject)),
            (NS.relation, node(relation)),
            (NS.object, node(obj)),
        ):
            self.graph.add((record, pred, value))
        for eid in evidence_ids:
            self.graph.add((record, NS.evidenceRef, Literal(eid)))

    def add_value(self, record_id, subject, property_id, value, evidence_ids, qualifiers=None):
        if subject not in self.registry.entities:
            raise LookupError(subject)
        if not evidence_ids:
            raise ValueError("canonical values require evidence")
        from nasa_fire_ai.query.v2 import PropertyConstraintV2

        operator = "BETWEEN" if value.lower is not None else "EQ"
        normalized = self.registry.validate(
            PropertyConstraintV2(property_id=property_id, operator=operator, value=value)
        )
        record = node(record_id)
        for pred, val in (
            (RDF.type, NS.SemanticValue),
            (NS.subject, node(subject)),
            (NS.measuredProperty, node(property_id)),
        ):
            self.graph.add((record, pred, val))
        self.graph.add((record, NS.value, Literal(normalized.model_dump_json())))
        self.graph.add(
            (record, NS.qualifiers, Literal(json.dumps(qualifiers or {}, sort_keys=True)))
        )
        for eid in evidence_ids:
            self.graph.add((record, NS.evidenceRef, Literal(eid)))
        self.add_entity(
            record_id,
            "Measurement",
            evidence_ids,
            self.sources(subject),
            {
                "id": record_id,
                "subject": subject,
                "property_id": property_id,
                "value": normalized.model_dump(mode="json"),
                "qualifiers": qualifiers or {},
                "evidence_ids": list(evidence_ids),
            },
        )

    def entities(self):
        return sorted({identity(s) for s in self.graph.subjects(NS.canonical, Literal(True))})

    def classes(self, subject):
        return {identity(x) for x in self.graph.objects(node(subject), RDF.type)}

    def relations(self, subject, relation):
        return {
            identity(obj)
            for record in self.graph.subjects(NS.subject, node(subject))
            if (record, NS.relation, node(relation)) in self.graph
            for obj in self.graph.objects(record, NS.object)
        }

    def values(self, subject, property_id):
        return [
            GenericValue.model_validate_json(str(value))
            for record in self.graph.subjects(NS.subject, node(subject))
            if (record, NS.measuredProperty, node(property_id)) in self.graph
            for value in self.graph.objects(record, NS.value)
        ]

    def evidence(self, subject):
        return sorted(str(x) for x in self.graph.objects(node(subject), NS.evidenceRef))

    def sources(self, subject):
        return {identity(x) for x in self.graph.objects(node(subject), NS.source)}

    def payload(self, subject):
        value = self.graph.value(node(subject), NS.payload)
        return json.loads(str(value)) if value else {"id": subject}


@dataclass(frozen=True)
class NativeSemanticQueryPlan:
    intent: QueryIntentV2
    candidate_entity_ids: list[str]
    documentary: bool


def compile_native(intent: QueryIntentV2, store: SemanticGraph) -> NativeSemanticQueryPlan:
    store.registry.validate_intent(intent)
    for c in intent.entity_constraints:
        if c.relation not in store.registry.relations:
            raise LookupError(c.relation)
        if c.entity_id not in store.registry.entities:
            raise LookupError(c.entity_id)
    for operand in intent.comparison.operands if intent.comparison else []:
        if operand not in store.registry.entities:
            raise LookupError(operand)
    for dim in intent.comparison.dimensions if intent.comparison else []:
        if dim not in store.registry.properties:
            raise LookupError(dim)
    documentary = any(
        store.registry.class_metadata.get(t, {}).get("documentary") for t in intent.targets
    )
    candidates = []
    for subject in store.entities():
        target_classes = intent.targets or intent.requested_information
        if target_classes and not store.classes(subject).intersection(target_classes):
            continue
        if intent.source_constraints and not store.sources(subject).intersection(
            intent.source_constraints
        ):
            continue
        # Selection scope is declarative registry metadata, not a relation-specific branch.
        if any(
            store.registry.relations[c.relation].selection_scope
            and c.entity_id not in store.relations(subject, c.relation)
            for c in intent.entity_constraints
        ):
            continue
        candidates.append(subject)
    return NativeSemanticQueryPlan(intent, candidates, documentary)


def classify_native(subject, intent, store):
    detail = {
        "matches": [],
        "differs": [],
        "unknown": [],
        "unresolved": list(intent.unresolved_mentions),
    }
    for c in intent.entity_constraints:
        actual = store.relations(subject, c.relation)
        outcome = (
            "matches"
            if c.entity_id in actual
            else "differs"
            if actual or store.registry.relations[c.relation].closed_world
            else "unknown"
        )
        detail[outcome].append(f"{c.relation}={c.entity_id}")
    for c in intent.property_constraints:
        values = store.values(subject, c.property_id)
        outcomes = {evaluate_constraint(c, v, store.registry) for v in values}
        # Conflicting or unavailable observations cannot establish an exact match.
        outcome = (
            "matches"
            if outcomes == {"MATCH"}
            else "differs"
            if outcomes == {"DIFFER"}
            else "unknown"
        )
        detail[outcome].append(c.property_id)
    required = bool(intent.entity_constraints or intent.property_constraints)
    blocked = bool(
        detail["differs"]
        or detail["unknown"]
        or detail["unresolved"]
        or intent.clarification_required
    )
    if required and not blocked:
        return "DIRECT", detail
    return ("RELATED" if detail["matches"] else "NO_DIRECT"), detail


@dataclass(frozen=True)
class NativeExecutionResult:
    bundle: EvidenceBundle
    plan: NativeSemanticQueryPlan
    eligible_evidence_ids: list[str]
    latency_ms: dict[str, float]


def execute_native(intent, query, store, evidence_registry, limit=8):
    started = perf_counter()
    plan = compile_native(intent, store)
    compiled = perf_counter()
    direct, related = [], []
    for subject in plan.candidate_entity_ids:
        status, detail = classify_native(subject, intent, store)
        item = {"id": subject, **detail, "evidence_ids": store.evidence(subject)}
        if status == "DIRECT":
            direct.append(item)
        elif status == "RELATED":
            related.append(item)
    selected = {x["id"] for x in direct + related}
    if plan.documentary:
        # Topic constraints are documentary ranking terms, never canonical run matches.
        selected.update(plan.candidate_entity_ids)
    if not intent.entity_constraints and not intent.property_constraints:
        selected.update(plan.candidate_entity_ids)
    # Documentary semantics retain the document target. Structured overlap may
    # select publications; plain documentary search uses eligible document evidence.
    records = {}
    generic_records = []
    for subject in selected:
        for cls in store.classes(subject):
            if intent.requested_information and cls not in intent.requested_information:
                continue
            field = store.registry.class_metadata.get(cls, {}).get("bundle_field")
            if field:
                records.setdefault(field, []).append(store.payload(subject))
            generic_records.append(
                {"class_id": cls, **store.payload(subject), "evidence_ids": store.evidence(subject)}
            )
    eligible = sorted({eid for subject in selected for eid in store.evidence(subject)})
    executed = perf_counter()
    passages = (
        evidence_registry.search(query, eligible_ids=eligible, limit=limit) if eligible else []
    )
    if eligible and not passages:
        passages = [p for eid in eligible if (p := evidence_registry.resolve(eid))][:limit]
    for passage in passages:
        passage["source_metadata"] = evidence_registry.source_metadata(passage["evidence_id"])
    ranked = perf_counter()
    comparison = None
    if intent.comparison:
        operands = intent.comparison.operands
        dims = intent.comparison.dimensions or list(store.registry.properties)
        shared, different, unknown = {}, {}, []
        for dim in dims:
            values = {
                s: [v.model_dump(mode="json") for v in store.values(s, dim)] for s in operands
            }
            if any(not x for x in values.values()):
                unknown.append(dim)
            elif len({json.dumps(x, sort_keys=True) for x in values.values()}) == 1:
                shared[dim] = next(iter(values.values()))
            else:
                different[dim] = values
        comparison = ExperimentComparison(
            run_ids=operands,
            shared_conditions=shared,
            different_conditions=different,
            unknown_or_unavailable_conditions=unknown,
        )
    bundle = EvidenceBundle(
        query_intent=QueryIntent(),  # Legacy display envelope only; never executed.
        direct_evidence=direct,
        related_evidence=related,
        evidence_passages=passages,
        no_direct_evidence=not bool(direct),
        comparison=comparison,
        **records,
        retrieval_metadata={
            "executor": "native-rdf-v1",
            "query_intent_v2": intent.model_dump(mode="json"),
            "vectors_enabled": False,
        },
        authority_metadata={"canonical_only": True, "staging_can_establish_direct": False},
        semantic_records=generic_records,
        coverage_notes=["Unresolved mentions require review."]
        if intent.unresolved_mentions
        else [],
    )
    ended = perf_counter()
    return NativeExecutionResult(
        bundle,
        plan,
        eligible,
        {
            "planning": (compiled - started) * 1000,
            "kg_execution": (executed - compiled) * 1000,
            "bm25_ranking": (ranked - executed) * 1000,
            "bundle_build": (ended - ranked) * 1000,
            "total": (ended - started) * 1000,
        },
    )
