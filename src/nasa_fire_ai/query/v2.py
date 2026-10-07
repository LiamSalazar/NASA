"""Additive, registry-driven query language; v1 retrieval remains the default."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from nasa_fire_ai.models import QueryIntent
from nasa_fire_ai.normalization.units import normalize

Operator = Literal["EQ", "NEQ", "LT", "LTE", "GT", "GTE", "BETWEEN", "APPROX", "IN"]


class GenericValue(BaseModel):
    """Reported and normalized value form, never a property-specific field."""

    reported_value: float | str | None = None
    reported_unit: str | None = None
    canonical_value: float | None = None
    canonical_unit: str | None = None
    lower: float | None = None
    upper: float | None = None
    approximate: bool = False
    raw_expression: str | None = None

    @model_validator(mode="after")
    def valid_shape(self):
        if (self.lower is None) != (self.upper is None):
            raise ValueError("range requires both endpoints")
        if self.lower is not None and self.lower > self.upper:
            raise ValueError("range lower exceeds upper")
        return self


class EntityConstraintV2(BaseModel):
    relation: str
    entity_id: str


class PropertyConstraintV2(BaseModel):
    property_id: str
    operator: Operator
    value: GenericValue


class ComparisonV2(BaseModel):
    operands: list[str] = Field(min_length=2)
    dimensions: list[str] = []


class QueryIntentV2(BaseModel):
    schema_version: str = "query-intent-v2"
    operation: Literal["SEARCH", "COMPARE", "EXPLAIN"] = "SEARCH"
    targets: list[str] = []
    entity_constraints: list[EntityConstraintV2] = []
    property_constraints: list[PropertyConstraintV2] = []
    requested_information: list[str] = []
    comparison: ComparisonV2 | None = None
    source_constraints: list[str] = []
    unresolved_mentions: list[str] = []
    conversation_reference: str | None = None


@dataclass(frozen=True)
class PropertyDefinition:
    property_id: str
    dimension: str
    canonical_unit: str | None
    datatype: Literal["numeric", "categorical"] = "numeric"
    aliases: list[str] = field(default_factory=list)
    status: Literal["CANONICAL", "CANDIDATE_NEW_CONCEPT"] = "CANONICAL"


class SemanticRegistry:
    """Semantic data may grow here without changing the QueryIntentV2 shape."""

    def __init__(self, properties=None, target_classes=None, information_classes=None):
        self.properties = {x.property_id: x for x in properties or []}
        self.target_classes = target_classes or {
            "ExperimentalRun",
            "Investigation",
            "ExperimentFamily",
            "Measurement",
            "Publication",
            "SafetyStatement",
        }
        self.information_classes = information_classes or {
            "ExperimentalRun",
            "Measurement",
            "ReportedObservation",
            "NASAConclusion",
            "SafetyImplication",
            "Requirement",
            "Guidance",
            "Publication",
            "OpenQuestion",
        }

    def register(self, definition: PropertyDefinition) -> None:
        self.properties[definition.property_id] = definition

    def register_target_class(self, class_id: str) -> None:
        self.target_classes.add(class_id)

    def register_information_class(self, class_id: str) -> None:
        self.information_classes.add(class_id)

    def resolve_property(self, raw_label: str, unit: str | None = None) -> tuple[str, str | None]:
        normalized = " ".join(raw_label.lower().replace("_", " ").split())
        matches = [
            p
            for p in self.properties.values()
            if normalized in {p.property_id.lower(), *(a.lower() for a in p.aliases)}
        ]
        if len(matches) != 1:
            return ("AMBIGUOUS" if len(matches) > 1 else "UNKNOWN", None)
        candidate = matches[0]
        if unit and candidate.canonical_unit:
            try:
                _, canonical = normalize(1.0, unit)
            except ValueError:
                return "UNKNOWN", None
            if canonical != candidate.canonical_unit:
                return "UNKNOWN", None
        return "CANONICAL", candidate.property_id

    def validate(self, constraint: PropertyConstraintV2) -> GenericValue:
        definition = self.properties.get(constraint.property_id)
        if definition is None or definition.status != "CANONICAL":
            raise LookupError(constraint.property_id)
        value = constraint.value.model_copy(deep=True)
        if definition.datatype == "categorical":
            if constraint.operator not in {"EQ", "NEQ", "IN"}:
                raise ValueError("operator incompatible with categorical property")
            return value
        if constraint.operator == "BETWEEN" and value.lower is None:
            raise ValueError("BETWEEN requires a range")
        if value.reported_value is not None and not isinstance(value.reported_value, (int, float)):
            raise ValueError("numeric property requires numeric value")
        if value.reported_unit:
            converted, canonical = normalize(
                float(value.reported_value or value.lower or 0), value.reported_unit
            )
            if definition.canonical_unit and canonical != definition.canonical_unit:
                raise ValueError("incompatible unit dimension")
            value.canonical_value, value.canonical_unit = converted, canonical
            if value.lower is not None:
                value.lower = normalize(value.lower, value.reported_unit)[0]
                value.upper = normalize(value.upper, value.reported_unit)[0]
        return value

    def validate_intent(self, intent: QueryIntentV2) -> None:
        if unknown := set(intent.targets) - self.target_classes:
            raise LookupError(f"unknown targets: {sorted(unknown)}")
        if unknown := set(intent.requested_information) - self.information_classes:
            raise LookupError(f"unknown information classes: {sorted(unknown)}")
        for constraint in intent.property_constraints:
            self.validate(constraint)


@dataclass(frozen=True)
class GenericMeasurement:
    property_id: str
    value: GenericValue
    subject_id: str
    evidence_id: str
    qualifiers: dict[str, str] = field(default_factory=dict)
    canonical: bool = True


def _number(value: GenericValue) -> float | None:
    if value.canonical_value is not None:
        return value.canonical_value
    return float(value.reported_value) if isinstance(value.reported_value, (int, float)) else None


def evaluate_constraint(
    constraint: PropertyConstraintV2, candidate: GenericValue, registry: SemanticRegistry
) -> str:
    """Property-independent evaluator: MATCH, DIFFER, UNKNOWN, or INVALID."""
    query = registry.validate(constraint)
    definition = registry.properties[constraint.property_id]
    if definition.datatype == "categorical":
        if candidate.reported_value is None or query.reported_value is None:
            return "UNKNOWN"
        values = (
            query.reported_value
            if isinstance(query.reported_value, list)
            else [query.reported_value]
        )
        same = candidate.reported_value in values
        return "MATCH" if (same if constraint.operator != "NEQ" else not same) else "DIFFER"
    left, right = _number(candidate), _number(query)
    if left is None:
        return "UNKNOWN"
    if constraint.operator == "BETWEEN":
        return "MATCH" if query.lower <= left <= query.upper else "DIFFER"
    if right is None:
        return "UNKNOWN"
    checks = {
        "EQ": left == right,
        "NEQ": left != right,
        "LT": left < right,
        "LTE": left <= right,
        "GT": left > right,
        "GTE": left >= right,
        "APPROX": abs(left - right) <= max(abs(right) * 0.05, 1e-12),
    }
    return "MATCH" if checks.get(constraint.operator, False) else "DIFFER"


@dataclass(frozen=True)
class PlannedQueryV2:
    candidate_entity_ids: list[str]
    eligible_evidence_ids: list[str]
    bm25_terms: list[str]


def plan_v2(
    intent: QueryIntentV2, registry: SemanticRegistry, entity_index=None, evidence_index=None
) -> PlannedQueryV2:
    """Registry-validated planner with no property-identity branches."""
    registry.validate_intent(intent)
    entity_index, evidence_index = entity_index or {}, evidence_index or {}
    candidates = [
        entity_id
        for entity_id, facts in entity_index.items()
        if all(facts.get(c.relation) == c.entity_id for c in intent.entity_constraints)
    ]
    if not entity_index:
        candidates = [c.entity_id for c in intent.entity_constraints]
    evidence = sorted({eid for entity in candidates for eid in evidence_index.get(entity, [])})
    terms = (
        [c.entity_id for c in intent.entity_constraints]
        + [c.property_id for c in intent.property_constraints]
        + intent.targets
        + intent.requested_information
        + intent.source_constraints
    )
    return PlannedQueryV2(candidates, evidence, terms)


def classify_candidate_v2(
    constraints, measurements, registry: SemanticRegistry
) -> tuple[str, dict[str, list[str]]]:
    """Generic DIRECT/RELATED classification; staging cannot establish DIRECT."""
    values = {m.property_id: m for m in measurements if m.canonical}
    matches, differs, unknown = [], [], []
    for constraint in constraints:
        m = values.get(constraint.property_id)
        outcome = "UNKNOWN" if m is None else evaluate_constraint(constraint, m.value, registry)
        (
            matches
            if outcome == "MATCH"
            else differs
            if outcome in {"DIFFER", "INVALID"}
            else unknown
        ).append(constraint.property_id)
    detail = {"matches": matches, "differs": differs, "unknown": unknown}
    if constraints and len(matches) == len(constraints):
        return "DIRECT", detail
    return ("RELATED" if matches else "NO_DIRECT"), detail


def v1_to_v2(intent: QueryIntent) -> QueryIntentV2:
    entities = [EntityConstraintV2(relation="hasMaterial", entity_id=x) for x in intent.materials]
    entities += [
        EntityConstraintV2(relation="hasGravityCondition", entity_id=x)
        for x in intent.gravity_conditions
    ]
    entities += [
        EntityConstraintV2(relation="belongsToInvestigation", entity_id=x)
        for x in intent.investigations
    ]
    props = []
    for name, value in (
        ("OxygenConcentration", intent.oxygen),
        ("Pressure", intent.pressure),
        ("AirflowVelocity", intent.flow_velocity),
    ):
        if value:
            props.append(
                PropertyConstraintV2(
                    property_id=name,
                    operator={"<": "LT", "<=": "LTE", "=": "EQ", ">=": "GTE", ">": "GT"}[
                        value.operator
                    ],
                    value=GenericValue(reported_value=value.value, reported_unit=value.unit),
                )
            )
    requested = {
        "experiments": "ExperimentalRun",
        "observations": "ReportedObservation",
        "measurements": "Measurement",
        "conclusions": "NASAConclusion",
        "publications": "Publication",
        "safety": "SafetyImplication",
    }
    return QueryIntentV2(
        operation="COMPARE" if intent.query_mode == "compare" else "SEARCH",
        targets=["ExperimentalRun"],
        entity_constraints=entities,
        property_constraints=props,
        requested_information=[requested.get(x, x) for x in intent.requested_information],
    )
