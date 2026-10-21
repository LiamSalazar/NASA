"""A condition never carries another value, a printed difference is not an absolute value,
and one entity proposed twice is one entity; synthetic text, never NASA data."""

import pytest
from test_document_extraction import entity, submitted, support, validate
from test_document_extraction import service as _service

from nasa_fire_ai.ingestion.document_extraction import Output

service = _service


def quantities(service, text, entities, items):
    p = submitted(service, "II. Methods\n" + text)
    o = Output().model_dump()
    o["entities"] = [entity(p, *e) for e in entities]
    o["quantities"] = [
        {
            "subject": subject,
            "label": label,
            "expression": expression,
            "unit": unit,
            "epistemic": epistemic,
            "support": support(p, sentence),
        }
        for subject, label, expression, unit, epistemic, sentence in items
    ]
    result = validate(service, p, o)
    return [r for r in result["records"] if r["kind"] == "quantities"], result["entities_by_key"]


@pytest.mark.parametrize(
    "sentence,condition,expression",
    [
        (
            "The 3750 psia supply pressure had a nominal operating pressure of ~200 psia.",
            "3750 psia supply pressure",
            "~200",
        ),
        (
            "For the 4000 psia supply pressure, the nominal operating pressure was ~150 psia.",
            "4000 psia supply pressure",
            "~150",
        ),
    ],
)
def test_a_condition_never_carries_another_value(service, sentence, condition, expression):
    # Metamorphic: other numbers and wording, same reading. The value is kept,
    # never given to the condition.
    records, entities = quantities(
        service,
        sentence,
        [("cond", condition, "PressureCondition", condition)],
        [
            (
                "cond",
                "nominal operating pressure",
                expression,
                "psia",
                "experimental_configuration",
                sentence,
            )
        ],
    )
    (record,) = records
    assert record["status"] != "REJECTED"
    assert record.get("subject") != entities["cond"]["id"]
    assert record["subject_recovery"]["proposed_subject_rejection"] == (
        "QUANTITY_SUBJECT_IS_A_CONDITION"
    )


def test_a_condition_may_carry_its_own_printed_magnitude(service):
    sentence = "The sample was exposed to a 10 cm/s primer flow."
    records, _ = quantities(
        service,
        sentence,
        [("flow", "10 cm/s primer flow", "FlowCondition", "10 cm/s primer flow")],
        [("flow", "primer flow", "10", "cm/s", "experimental_configuration", sentence)],
    )
    (record,) = records
    assert "QUANTITY_SUBJECT_IS_A_CONDITION" not in record["reasons"]
