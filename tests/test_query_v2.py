import pytest

from nasa_fire_ai.models import NumericFilter, QueryIntent
from nasa_fire_ai.query.v2 import (
    GenericValue,
    PropertyConstraintV2,
    PropertyDefinition,
    SemanticRegistry,
    v1_to_v2,
)


def test_v1_maps_to_generic_constraints():
    q = v1_to_v2(
        QueryIntent(
            materials=["PMMA"], flow_velocity=NumericFilter(operator="<=", value=10, unit="cm/s")
        )
    )
    assert q.entity_constraints[0].relation == "hasMaterial"
    assert q.property_constraints[0].property_id == "AirflowVelocity"


def test_dynamic_property_needs_no_query_schema_change():
    registry = SemanticRegistry([PropertyDefinition("TestPropertyX", "temperature", "K")])
    assert (
        registry.validate(
            PropertyConstraintV2(
                property_id="TestPropertyX",
                operator="EQ",
                value=GenericValue(reported_value=300, reported_unit="K"),
            )
        ).reported_value
        == 300
    )
    with pytest.raises(ValueError):
        registry.validate(
            PropertyConstraintV2(
                property_id="TestPropertyX",
                operator="EQ",
                value=GenericValue(reported_value=2, reported_unit="m/s"),
            )
        )
