"""The propositions request defines every statement role and can offer a subject menu; synthetic."""

import typing

from test_document_extraction import client_for, entity, submitted
from test_document_extraction import service as _service
from test_phase1_closure import _requests

import nasa_fire_ai.ingestion.document_extraction as extraction
from nasa_fire_ai.config import Settings
from nasa_fire_ai.ingestion.document_extraction import (
    STAGE_INSTRUCTIONS,
    ExtractionBudget,
    Output,
    Statement,
    admissible_statement_subjects,
)

service = _service

TEXT = "II. Methods\nRun A1 used the Beta igniter coil. Run A1 burned for a short time.\n"


def test_the_role_card_defines_every_statement_role():
    roles = typing.get_args(Statement.model_fields["epistemic"].annotation)
    card = STAGE_INSTRUCTIONS["propositions"]
    assert len(roles) == 10
    assert all(f"- {role}:" in card for role in roles)
    assert "never documentary_context" in card


def propositions_payloads(service, monkeypatch, menu):
    monkeypatch.setenv("SCIENCE_ADMISSIBLE_SUBJECTS", "1" if menu else "0")
    p = submitted(service, TEXT)
    o = Output().model_dump()
    o["entities"] = [entity(p, "a1", "A1", "ExperimentalRun", "Run A1 used")]
    client = client_for(o)
    service.prepare_scientific(
        p["id"],
        Settings(root=service.root),
        model_enabled=True,
        budget=ExtractionBudget(max_model_calls=8),
        client=client,
    )
    return [x for _prompt, x in _requests(client) if x["stage"] == "propositions"]


def test_the_subject_menu_is_off_by_default(service, monkeypatch):
    payloads = propositions_payloads(service, monkeypatch, menu=False)
    assert payloads
    assert not any("admissible_subjects" in a for x in payloads for a in x["source_anchors"])
    assert not any("subject_menu" in x for x in payloads)


def test_the_subject_menu_lists_known_subjects_on_task_statement_anchors(service, monkeypatch):
    payloads = propositions_payloads(service, monkeypatch, menu=True)
    known = {e["key"] for x in payloads for e in x["known_entities"]}
    offered = [a for x in payloads for a in x["source_anchors"] if "admissible_subjects" in a]
    assert offered and all(a["statement_eligible"] and a["in_task"] for a in offered)
    assert all(set(a["admissible_subjects"]) <= known for a in offered)
    assert all("subject_menu" in x for x in payloads)


def test_admissible_subjects_are_supported_and_narrowest_first(monkeypatch):
    monkeypatch.setattr(extraction, "applicable", lambda key, *args: True)
    monkeypatch.setattr(extraction, "document_statement_scope", lambda key, *args: False)
    entities = {
        "study": {
            "class_id": "Investigation",
            "label": "Study",
            "validation_status": "SOURCE_SUPPORTED",
        },
        "group": {
            "class_id": "ExperimentFamily",
            "label": "Group",
            "validation_status": "SOURCE_SUPPORTED",
        },
        "run": {
            "class_id": "ExperimentalRun",
            "label": "Run",
            "validation_status": "SOURCE_SUPPORTED",
        },
        "held": {"class_id": "Sample", "label": "Held", "validation_status": "UNRESOLVED"},
    }
    assert admissible_statement_subjects([], entities, {}) == ["run", "group", "study"]
