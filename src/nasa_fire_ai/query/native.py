"""Native generic RDF execution. No V1 execution or legacy field mappings.

Scientific identities are supplied exclusively by the registry and graph. Operational
evidence locations remain in EvidenceRegistry; graph references are opaque evidence IDs.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from time import perf_counter
from urllib.parse import quote, unquote

from rdflib import RDF, Graph, Literal, Namespace, URIRef

from nasa_fire_ai.models import EvidenceBundle, ExperimentComparison, QueryIntent
from nasa_fire_ai.query.evidence_selection import select_information
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

    def explore_route(self, start, steps, evidence_registry, **budgets):
        """Explore validated associations without changing QueryIntentV2 or eligibility."""
        from nasa_fire_ai.query.ontology_navigation import navigate

        return navigate(self, start, steps, evidence_registry, **budgets)

    def add_entity(self, entity_id, class_id, evidence_ids, source_ids=(), payload=None):
        if class_id not in self.registry.target_classes | self.registry.information_classes:
            raise LookupError(class_id)
        if not evidence_ids:
            raise ValueError("canonical entities require evidence")
        subject = node(entity_id)
        self.registry.entities.add(entity_id)
        self.registry.source_ids.update(source_ids)
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

    def add_value(
        self,
        record_id,
        subject,
        property_id,
        value,
        evidence_ids,
        qualifiers=None,
        class_id="Measurement",
    ):
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
            class_id,
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

    def classes(self, subject, include_ancestors=False):
        classes = set(self.graph.objects(node(subject), RDF.type))
        if include_ancestors:
            from rdflib import RDFS

            from nasa_fire_ai.query.ontology_navigation import schema_closure

            classes = {
                parent
                for cls in classes
                for parent in schema_closure(self.graph, cls, RDFS.subClassOf)
            }
        return {identity(x) for x in classes}

    def relations(self, subject, relation):
        return {
            identity(obj)
            for record in self.graph.subjects(NS.subject, node(subject))
            if (record, NS.relation, node(relation)) in self.graph
            for obj in self.graph.objects(record, NS.object)
        }

    def values(self, subject, property_id):
        if (node(subject), NS.measuredProperty, node(property_id)) in self.graph:
            return [
                GenericValue.model_validate_json(str(x))
                for x in self.graph.objects(node(subject), NS.value)
            ]
        return [
            GenericValue.model_validate_json(str(value))
            for record in self.graph.subjects(NS.subject, node(subject))
            if (record, NS.measuredProperty, node(property_id)) in self.graph
            for value in self.graph.objects(record, NS.value)
        ]

    def value_records(self, subject, property_id):
        """Return values with source qualifiers intact for context-aware matching."""
        records = []
        if (node(subject), NS.measuredProperty, node(property_id)) in self.graph:
            candidates = [node(subject)]
        else:
            candidates = [
                record
                for record in self.graph.subjects(NS.subject, node(subject))
                if (record, NS.measuredProperty, node(property_id)) in self.graph
            ]
        for record in candidates:
            values = self.graph.objects(record, NS.value)
            qualifiers = self.graph.value(record, NS.qualifiers)
            parsed = json.loads(str(qualifiers)) if qualifiers else {}
            for value in values:
                records.append(
                    {
                        "value": GenericValue.model_validate_json(str(value)),
                        "qualifiers": parsed,
                        "evidence_ids": sorted(
                            str(e) for e in self.graph.objects(record, NS.evidenceRef)
                        ),
                    }
                )
        return records

    def evidence(self, subject):
        records = {node(subject), *self.graph.subjects(NS.subject, node(subject))}
        return sorted(
            {str(x) for record in records for x in self.graph.objects(record, NS.evidenceRef)}
        )

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


def compile_native(
    intent: QueryIntentV2, store: SemanticGraph, schema_hierarchical=False
) -> NativeSemanticQueryPlan:
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
        if intent.comparison and subject not in intent.comparison.operands:
            continue
        target_classes = intent.targets or intent.requested_information
        if target_classes and not store.classes(
            subject, include_ancestors=schema_hierarchical
        ).intersection(target_classes):
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


def classify_native(subject, intent, store, taxonomy_paths=None, related_policy=False):
    taxonomy_paths = taxonomy_paths or {}
    detail = {
        "matches": [],
        "differs": [],
        "unknown": [],
        "invalid": [],
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
        verified_paths = [taxonomy_paths.get((c.relation, c.entity_id), {}).get(a) for a in actual]
        if any(path and path["category_match"] for path in verified_paths):
            outcome = "matches"
        detail[outcome].append(f"{c.relation}={c.entity_id}")
    for c in intent.property_constraints:
        records = store.value_records(subject, c.property_id)
        if c.qualifiers:
            records = [
                row
                for row in records
                if all(row["qualifiers"].get(k) == v for k, v in c.qualifiers.items())
            ]
        values = [row["value"] for row in records]
        outcomes = {evaluate_constraint(c, v, store.registry) for v in values}
        # Conflicting or unavailable observations cannot establish an exact match.
        outcome = (
            "matches"
            if outcomes == {"MATCH"}
            else "differs"
            if outcomes == {"DIFFER"}
            else "invalid"
            if "INVALID" in outcomes
            else "unknown"
        )
        detail[outcome].append(c.property_id)
    required = bool(intent.entity_constraints or intent.property_constraints)
    blocked = bool(
        detail["differs"]
        or detail["invalid"]
        or detail["unknown"]
        or detail["unresolved"]
        or intent.clarification_required
    )
    if required and not blocked:
        return "DIRECT", detail
    path_overlap = any(
        taxonomy_paths.get((c.relation, c.entity_id), {}).get(actual)
        for c in intent.entity_constraints
        for actual in store.relations(subject, c.relation)
    )
    if taxonomy_paths or related_policy:
        anchors = set(
            store.registry.selection_policy.get("related", {}).get("anchor_relations", [])
        )
        requested_anchors = [c for c in intent.entity_constraints if c.relation in anchors]
        if requested_anchors and not any(
            c.entity_id in store.relations(subject, c.relation)
            or any(
                taxonomy_paths.get((c.relation, c.entity_id), {}).get(actual)
                for actual in store.relations(subject, c.relation)
            )
            for c in requested_anchors
        ):
            return "NO_DIRECT", detail
    # For a numeric-only request, the same validated physical quantity with an
    # explicit different value is an interpretable relationship. Previously a
    # bound with no exact match lost all source-backed alternatives. Anchor
    # checks above still protect required material/phenomenon scope.
    numeric_difference = related_policy and any(
        c.property_id in detail["differs"] for c in intent.property_constraints
    )
    return (
        "RELATED" if detail["matches"] or path_overlap or numeric_difference else "NO_DIRECT"
    ), detail


@dataclass(frozen=True)
class NativeExecutionResult:
    bundle: EvidenceBundle
    plan: NativeSemanticQueryPlan
    eligible_evidence_ids: list[str]
    latency_ms: dict[str, float]


def execute_native(
    intent,
    query,
    store,
    evidence_registry,
    limit=8,
    hierarchical=None,
    relational=None,
):
    started = perf_counter()
    from nasa_fire_ai.query.conceptual import is_conceptual_question

    conceptual = is_conceptual_question(query)
    conceptual_support = {}
    if conceptual:
        from nasa_fire_ai.query.conceptual import approved_conceptual_support

        conceptual_support = approved_conceptual_support(query, store, evidence_registry)
        # Also protects lossy historical conversion when the original question
        # is available. Experiment matches cannot answer terminology questions.
        intent = QueryIntentV2(
            operation="EXPLAIN",
            targets=["Publication"],
            source_constraints=intent.source_constraints,
        )
    if not conceptual:
        grouped = execute_investigation_groups(
            intent, query, store, evidence_registry, limit, hierarchical, relational
        )
        if grouped is not None:
            return grouped
    plan = compile_native(
        intent,
        store,
        schema_hierarchical=os.getenv("ONTOLOGY_GRAPH_ENRICHMENT_ENABLED", "false").lower()
        == "true",
    )
    hierarchical = (
        hierarchical
        if hierarchical is not None
        else os.getenv("HIERARCHICAL_SEMANTIC_RETRIEVAL_ENABLED", "false").lower()
        in {"true", "1", "yes"}
    )
    relational = (
        relational
        if relational is not None
        else os.getenv("RELATIONAL_RELATED_RETRIEVAL_ENABLED", "false").lower()
        in {"true", "1", "yes"}
    )
    taxonomy_paths, traversal_receipts = {}, []
    expansion_error = None
    if hierarchical:
        from nasa_fire_ai.query.hierarchy import traverse

        try:
            for constraint in intent.entity_constraints:
                # Selection-scoped identity restrictions remain exact.
                if store.registry.relations[constraint.relation].selection_scope:
                    continue
                receipt = traverse(
                    store, constraint.entity_id, constraint.relation, evidence_registry
                )
                taxonomy_paths[(constraint.relation, constraint.entity_id)] = receipt["paths"]
                traversal_receipts.append({"dimension": constraint.relation, **receipt})
        except (ValueError, LookupError, KeyError, TypeError) as exc:
            taxonomy_paths = {}
            expansion_error = type(exc).__name__
    compiled = perf_counter()
    direct, related = [], []
    provenance_exclusions = []
    for subject in plan.candidate_entity_ids:
        if hierarchical or relational:
            refs = store.evidence(subject)
            if not refs or any(evidence_registry.resolve(eid) is None for eid in refs):
                provenance_exclusions.append(
                    {"subject": subject, "reason": "unresolvable_experimental_evidence"}
                )
                continue
            if intent.source_constraints and any(
                (evidence_registry.source_metadata(eid) or {}).get("source_id")
                not in intent.source_constraints
                for eid in refs
            ):
                provenance_exclusions.append(
                    {"subject": subject, "reason": "cross_source_evidence"}
                )
                continue
        status, detail = classify_native(
            subject, intent, store, taxonomy_paths, hierarchical or relational
        )
        item = {"id": subject, **detail, "evidence_ids": store.evidence(subject)}
        if status == "DIRECT":
            direct.append(item)
        elif status == "RELATED":
            related.append(item)
    if hierarchical or relational:
        from nasa_fire_ai.query.hierarchy import constraint_explanation

        for item in direct + related:
            item["relationship_explanation"] = constraint_explanation(
                item["id"], intent, store, taxonomy_paths, item, query=query
            )
        related.sort(
            key=lambda item: (-item["relationship_explanation"]["ranking_score"], item["id"])
        )
    selected = {x["id"] for x in direct + related}
    if conceptual:
        direct, related = [], []
    if plan.documentary:
        # Topic constraints are documentary ranking terms, never canonical run matches.
        selected.update(plan.candidate_entity_ids)
    if not intent.entity_constraints and not intent.property_constraints:
        selected.update(plan.candidate_entity_ids)
    if intent.clarification_required or (
        intent.unresolved_mentions
        and not (intent.entity_constraints or intent.property_constraints)
    ):
        selected.clear()
        direct, related = [], []
    # Documentary evidence is complementary to KG matches, not constrained by
    # the existence of a matching run. Scientific epistemic records are selected
    # by registry class and lexical evidence relevance; never appended globally.
    scientific_classes = {
        c
        for c, meta in store.registry.class_metadata.items()
        if meta.get("bundle_field") and not meta.get("documentary")
    }
    requested_science = scientific_classes.intersection(intent.requested_information)
    measurement_only = (
        bool(intent.requested_information) and not requested_science and not plan.documentary
    )
    all_documentary = sorted(
        {
            eid
            for subject in store.entities()
            if (
                not intent.source_constraints
                or store.sources(subject).intersection(intent.source_constraints)
            )
            and any(
                store.registry.class_metadata.get(c, {}).get("documentary")
                for c in store.classes(subject)
            )
            for eid in store.evidence(subject)
        }
    )
    documentary_passages = []
    if (
        not measurement_only
        and not requested_science
        and not intent.clarification_required
        and not (
            intent.unresolved_mentions
            and not intent.entity_constraints
            and not intent.property_constraints
        )
    ):
        documentary_passages = evidence_registry.search(
            query, eligible_ids=all_documentary, limit=limit
        )
    info_selected, info_trace = select_information(intent, query, store, evidence_registry)
    if conceptual:
        for relation in conceptual_support.get("approved_relations", []):
            documentary_passages.extend(
                evidence_registry.resolve(eid) for eid in relation["evidence_ids"]
            )
    if os.getenv("SOURCE_KNOWLEDGE_ENRICHMENT_ENABLED", "false").lower() == "true":
        from nasa_fire_ai.query.evidence_selection import antecedent_context

        documentary_passages.extend(antecedent_context(info_trace, evidence_registry))
    if requested_science:
        # Run matches remain diagnostic, not a substitute for the requested class.
        selected = set(info_selected)
        direct, related = [], []
        for s in info_selected:
            status, detail = classify_native(
                s, intent, store, taxonomy_paths, hierarchical or relational
            )
            detail["matches"].append("reviewed requested information class")
            if not intent.entity_constraints and not intent.property_constraints:
                status = "DIRECT"
            elif status == "NO_DIRECT":
                if hierarchical or relational:
                    continue  # Topical class alone cannot establish scientific relatedness.
                status = "RELATED"
            item = {"id": s, **detail, "evidence_ids": store.evidence(s)}
            (direct if status == "DIRECT" else related).append(item)
    if (hierarchical or relational) and requested_science:
        from nasa_fire_ai.query.hierarchy import constraint_explanation

        for item in direct + related:
            item["relationship_explanation"] = constraint_explanation(
                item["id"], intent, store, taxonomy_paths, item, query=query
            )
    # Documentary semantics retain the document target. Structured overlap may
    # select publications; plain documentary search uses eligible document evidence.
    records = {}
    generic_records = []
    # Conditions preserve subject linkage, original units and context at the
    # bundle boundary, without converting them to observations.
    for subject in sorted(selected):
        for record in store.graph.subjects(NS.subject, node(subject)):
            if (record, RDF.type, NS.SemanticValue) in store.graph:
                generic_records.append(store.payload(identity(record)))
    for subject in sorted(selected):
        for cls in store.classes(subject):
            if intent.requested_information and cls not in intent.requested_information:
                continue
            field = store.registry.class_metadata.get(cls, {}).get("bundle_field")
            if field:
                payload = store.payload(subject)
                if subject in info_selected and (
                    intent.entity_constraints or intent.property_constraints
                ):
                    from nasa_fire_ai.query.hierarchy import constraint_explanation

                    _, scope_detail = classify_native(
                        subject, intent, store, taxonomy_paths, hierarchical or relational
                    )
                    payload = {
                        **payload,
                        "scientific_applicability": constraint_explanation(
                            subject, intent, store, taxonomy_paths, scope_detail, query=query
                        ),
                        "applicability_limit": "Topical statement selection does not establish every requested experimental condition",
                    }
                records.setdefault(field, []).append(payload)
            generic_records.append(
                {"class_id": cls, **store.payload(subject), "evidence_ids": store.evidence(subject)}
            )
    eligible = sorted({eid for subject in selected for eid in store.evidence(subject)})
    executed = perf_counter()
    ranked_passages = (
        evidence_registry.search(query, eligible_ids=eligible, limit=limit) if eligible else []
    )
    passages = list(ranked_passages)
    if requested_science:
        # FTS text need not repeat the query topic (which may be in its section).
        # Keep one resolvable reference per reviewed selected statement before BM25.
        structured = [
            passage
            for subject in info_selected
            if (
                passage := next(
                    (
                        evidence_registry.resolve(eid)
                        for eid in store.evidence(subject)
                        if evidence_registry.resolve(eid)
                    ),
                    None,
                )
            )
            is not None
        ]
        passage_map = {p["evidence_id"]: p for p in structured + passages}
        passages = list(passage_map.values())[:limit]
    if eligible and not passages:
        passages = [p for eid in eligible if (p := evidence_registry.resolve(eid))][:limit]
    # Preserve structured evidence and documentary discoveries; do not turn
    # lexical passages into canonical DIRECT or RELATED scientific facts.
    merged = {p["evidence_id"]: p for p in passages}
    merged.update({p["evidence_id"]: p for p in documentary_passages})
    passages = list(merged.values())
    eligible = sorted(set(eligible) | {p["evidence_id"] for p in documentary_passages})
    for passage in passages:
        resolved = evidence_registry.resolve(passage["evidence_id"])
        if resolved:
            passage.update(resolved)
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
            "conceptual_query": {
                "active": conceptual,
                "original_question": query,
                "equivalence_asserted": False,
                "authority": "approved relations and source terminology only",
                **conceptual_support,
            },
            "executor": "native-rdf-v1",
            "query_intent_v2": intent.model_dump(mode="json"),
            "vectors_enabled": False,
            "hierarchical_retrieval": {
                "enabled": hierarchical,
                "load_errors": getattr(store, "taxonomy_load_errors", []),
                "receipts": traversal_receipts,
                "error": expansion_error,
            },
            "relational_related": {"enabled": relational},
            "provenance_exclusions": provenance_exclusions,
            "selection_trace": {
                "requested_information": intent.requested_information,
                "initial_kg_candidates": plan.candidate_entity_ids,
                "information_candidates": info_trace,
                "selected_information": info_selected,
                "documentary_candidates": [p["evidence_id"] for p in documentary_passages],
                "documentary_candidate_trace": [
                    {
                        "evidence_id": p["evidence_id"],
                        "rank": rank,
                        "bm25_score": p.get("score"),
                        "eligible": p["evidence_id"] in all_documentary,
                        "source_metadata": evidence_registry.source_metadata(p["evidence_id"]),
                    }
                    for rank, p in enumerate(documentary_passages, 1)
                ],
                "ranked_passage_candidates": [
                    {
                        "evidence_id": p["evidence_id"],
                        "rank": rank,
                        "bm25_score": p.get("score"),
                        "eligible": p["evidence_id"] in eligible,
                        "source_metadata": evidence_registry.source_metadata(p["evidence_id"]),
                    }
                    for rank, p in enumerate(ranked_passages, 1)
                ],
                "final_evidence_ids": [p["evidence_id"] for p in passages],
                "no_direct_reason": (
                    "clarification_required"
                    if intent.clarification_required
                    else "unresolved_mentions"
                    if intent.unresolved_mentions
                    else "no_class_topic_source_eligible_evidence"
                    if requested_science and not info_selected
                    else "required_canonical_constraint_not_fully_matched"
                    if intent.entity_constraints or intent.property_constraints
                    else "no_canonical_direct_record"
                )
                if not direct
                else None,
            },
        },
        authority_metadata={"canonical_only": True, "staging_can_establish_direct": False},
        semantic_records=generic_records,
        coverage_notes=["Unresolved mentions require review."]
        if intent.unresolved_mentions
        else [],
    )
    from nasa_fire_ai.query.related_presentation import group_related

    bundle.retrieval_metadata["related_presentation"] = group_related(related, store)
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


def execute_investigation_groups(
    intent, query, store, evidence_registry, limit, hierarchical, relational
):
    """Bounded union for distinct investigation identities, preserving branch provenance."""
    from dataclasses import replace

    slots = {}
    for constraint in intent.entity_constraints:
        slots.setdefault(constraint.relation, []).append(constraint)
    group_slots = [
        relation
        for relation, values in slots.items()
        if len(values) > 1
        and store.registry.relations.get(relation)
        and store.registry.relations[relation].selection_scope
    ]
    if not (
        len(group_slots) == 1
        and len(slots[group_slots[0]]) <= 8
        and not intent.comparison
        and not intent.unresolved_mentions
        and not any(
            term in query.lower()
            for term in (
                "same experiment",
                "single experiment",
                "simultaneously",
                "belongs to both",
            )
        )
        and all(a.startswith("multiple_values_for_relation:") for a in intent.ambiguities)
    ):
        return None
    relation = group_slots[0]
    branches = []
    for value in slots[relation]:
        branch = intent.model_copy(
            update={
                "entity_constraints": [
                    c for c in intent.entity_constraints if c.relation != relation
                ]
                + [value],
                "ambiguities": [],
                "clarification_required": False,
            }
        )
        branches.append(
            (
                value.entity_id,
                execute_native(
                    branch, query, store, evidence_registry, limit, hierarchical, relational
                ),
            )
        )
    first = branches[0][1]
    bundle = first.bundle.model_copy(deep=True)
    for field in ("direct_evidence", "related_evidence"):
        setattr(
            bundle,
            field,
            [
                {**item, "requested_group": group}
                for group, result in branches
                for item in getattr(result.bundle, field)
            ],
        )
    for field in (
        "semantic_records",
        "experimental_observations",
        "measurements",
        "conditions",
        "nasa_conclusions",
        "safety_implications",
        "requirements",
        "guidance",
        "design_test_criteria",
        "nasa_identified_open_questions",
        "interventions",
        "publications",
    ):
        setattr(
            bundle,
            field,
            [
                {**item, "requested_group": group}
                for group, result in branches
                for item in getattr(result.bundle, field)
            ],
        )
    passages = {
        p["evidence_id"]: p for _, result in branches for p in result.bundle.evidence_passages
    }
    bundle.evidence_passages = list(passages.values())
    bundle.no_direct_evidence = not bool(bundle.direct_evidence)
    bundle.retrieval_metadata["query_intent_v2"] = intent.model_dump(mode="json")
    bundle.retrieval_metadata["grouped_search"] = [
        {"group": group, "no_direct": result.bundle.no_direct_evidence}
        for group, result in branches
    ]
    from nasa_fire_ai.query.related_presentation import group_related

    bundle.retrieval_metadata["related_presentation"] = group_related(
        bundle.related_evidence, store
    )
    return replace(
        first,
        bundle=bundle,
        eligible_evidence_ids=sorted(
            {eid for _, result in branches for eid in result.eligible_evidence_ids}
        ),
    )
