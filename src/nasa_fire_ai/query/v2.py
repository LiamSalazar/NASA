"""Additive generic query language; v1 retrieval remains the default."""

from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel

from nasa_fire_ai.models import QueryIntent
from nasa_fire_ai.normalization.units import normalize


class GenericValue(BaseModel):
    reported_value: float | str | None = None
    reported_unit: str | None = None
    lower: float | None = None
    upper: float | None = None
    approximate: bool = False


class EntityConstraintV2(BaseModel):
    relation: str
    entity_id: str


class PropertyConstraintV2(BaseModel):
    property_id: str
    operator: Literal["EQ", "NEQ", "LT", "LTE", "GT", "GTE", "BETWEEN", "APPROX", "IN"]
    value: GenericValue


class ComparisonV2(BaseModel):
    operands: list[str]
    dimensions: list[str] = []


class QueryIntentV2(BaseModel):
    schema_version: str = "query-intent-v2"
    operation: Literal["SEARCH", "COMPARE", "EXPLAIN"] = "SEARCH"
    targets: list[str] = []
    entity_constraints: list[EntityConstraintV2] = []
    property_constraints: list[PropertyConstraintV2] = []
    requested_information: list[str] = []
    comparison: ComparisonV2 | None = None
    unresolved_mentions: list[str] = []


@dataclass
class PropertyDefinition:
    property_id: str
    dimension: str
    canonical_unit: str | None
    aliases: list[str] = field(default_factory=list)
    status: Literal["CANONICAL", "CANDIDATE_NEW_CONCEPT"] = "CANONICAL"


class SemanticRegistry:
    def __init__(self, properties: list[PropertyDefinition] | None = None):
        self.properties = {x.property_id: x for x in properties or []}

    def register(self, definition: PropertyDefinition) -> None:
        self.properties[definition.property_id] = definition

    def validate(self, constraint: PropertyConstraintV2) -> GenericValue:
        definition = self.properties.get(constraint.property_id)
        if definition is None:
            raise LookupError(constraint.property_id)
        if constraint.value.reported_value is not None and constraint.value.reported_unit:
            _, unit = normalize(
                float(constraint.value.reported_value), constraint.value.reported_unit
            )
            if definition.canonical_unit and unit != definition.canonical_unit:
                raise ValueError("incompatible unit dimension")
        return constraint.value


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
    return QueryIntentV2(
        operation="COMPARE" if intent.query_mode == "compare" else "SEARCH",
        targets=["ExperimentalRun"],
        entity_constraints=entities,
        property_constraints=props,
        requested_information=intent.requested_information,
    )
