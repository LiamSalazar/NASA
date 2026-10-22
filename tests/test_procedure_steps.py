"""A set-up or planned step is what was done, not what was observed; synthetic text."""

import pytest

from nasa_fire_ai.ingestion.statement_integrity import procedure_without_outcome


@pytest.mark.parametrize(
    "text",
    [
        "The valve impacts were performed manually to control the sequence.",
        "Before the series, the valve was set up with a nitrogen supply.",
        "The first series was to perform 40 dry impacts.",
        "The port was injected with 20 uL of oil.",
    ],
)
def test_a_set_up_or_planned_step_is_a_procedure(text):
    assert procedure_without_outcome(text)


@pytest.mark.parametrize(
    "text",
    [
        "The valve performed nominally during the entire series.",
        "The valve was set up with nitrogen and no ignition occurred.",
        "Impacts were performed and the valve passed every functional test.",
    ],
)
def test_a_step_with_its_outcome_is_an_observation(text):
    # Metamorphic: the same steps with a printed outcome report what happened.
    assert not procedure_without_outcome(text)
