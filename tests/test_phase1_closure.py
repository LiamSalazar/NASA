"""Synthetic end-to-end checks for table rows, document scope, lineage and integrity.

Every positive has a critical negative or a metamorphic twin; never NASA data.
"""

import copy

from test_document_extraction import entity, submitted, support
from test_document_extraction import service as _service

from nasa_fire_ai.ingestion.document_extraction import (
    Output,
    section_for_span,
    validate_output,
)
from nasa_fire_ai.ingestion.document_structure import structure
from nasa_fire_ai.ingestion.table_continuity import link_continuation_tables

service = _service

ROWS = [
    ["Material", "Energy (J)", "Condition", "Reactions/Tests"],
    ["aAlpha", "10", "Wet", "0/20"],
    ["", "10", "Dry", "2/20"],
    ["", "10", "Hot", "0/20"],
]
TABLE_TEXT = "\n".join(v for row in ROWS for v in row)
TEXT = (
    "# Synthetic study\nII. Results\nTABLE 1— Synthetic impact data\n"
    + TABLE_TEXT
    + "\na-\nSynthetic standard lab\n"
)


def with_tables(service, package, rows=ROWS):
    document = structure(package, service.root)
    document["detected_tables"] = link_continuation_tables(
        [
            {
                "input_sha256": package["evidence"][0]["checksum"],
                "physical_pdf_page": package["evidence"][0]["page"],
                "bbox": [0, 0, 1, 1],
                "header": rows[0],
                "header_external": False,
                "cells": rows,
            }
        ]
    )
    return document


def run(service, package, output, document):
    return validate_output(copy.deepcopy(output), package, document, service.semantic)["records"]


def proposed(records):
    """The records of the test's own proposals, without printed-structure candidates."""
    return [r for r in records if not r.get("candidate_origin")]


def quantity(expression, label="Reactions/Tests", unit=None):
    return {
        "subject": "alpha",
        "label": label,
        "expression": expression,
        "unit": unit,
        "epistemic": "reported_quantity",
    }


def table_output(package, *quantities):
    o = Output().model_dump()
    o["entities"] = [
        entity(package, "root", "Synthetic study", "Investigation", "# Synthetic study"),
        entity(package, "alpha", "aAlpha", "Sample", "aAlpha"),
    ]
    o["quantities"] = [{**q, "support": support(package, TABLE_TEXT)} for q in quantities]
    return o


def test_value_in_a_continuation_row_binds_to_its_row_group_and_exact_cell(service):
    p = submitted(service, TEXT)
    o = table_output(p, quantity("2/20"))
    record = run(service, p, o, with_tables(service, p))[-1]
    assert record["status"] != "REJECTED", record["reasons"]
    binding = record["table_row_binding"]
    assert binding["status"] == "UNIQUE"
    assert binding["rows"][0]["row_context"]["Condition"] == "Dry"
    [cell] = record["quantity_value_spans"]
    text = p["evidence"][0]["text"]
    assert text[cell["start"] : cell["end"]] == "2/20" and cell["start"] == text.index("2/20")
    assert record["quantity_name_support"]["basis"] == "ORIGINAL_TABLE_COLUMN_HEADER"
    # Without the detected table the same proposal has no subject binding.
    plain = run(service, p, o, structure(p, service.root))[-1]
    assert plain["status"] == "UNRESOLVED" and plain["subject"] is None
    assert "QUANTITY_VALUE_PRESERVED_SUBJECT_UNRESOLVED" in plain["reasons"]


def test_value_in_several_but_not_all_group_rows_stays_unresolved(service):
    p = submitted(service, TEXT)
    record = run(service, p, table_output(p, quantity("0/20")), with_tables(service, p))[-1]
    assert record["table_row_binding"]["status"] == "AMBIGUOUS"
    assert record["status"] == "UNRESOLVED"
    assert "TABLE_VALUE_ROW_WITHIN_GROUP_AMBIGUOUS" in record["reasons"]
    energy = run(
        service, p, table_output(p, quantity("10", "Energy", "J")), with_tables(service, p)
    )[-1]
    assert energy["table_row_binding"]["status"] == "GROUP_CONSTANT"
    assert "TABLE_VALUE_ROW_WITHIN_GROUP_AMBIGUOUS" not in energy["reasons"]


def test_table_value_needs_the_column_header_as_its_name(service):
    p = submitted(service, TEXT)
    record = run(
        service, p, table_output(p, quantity("2/20", label="Outcome")), with_tables(service, p)
    )[-1]
    assert record["status"] == "REJECTED"
    assert record["reasons"] == ["QUANTITY_NAME_IS_NOT_TABLE_COLUMN_HEADER"]


def test_whole_table_rows_are_not_a_prose_statement(service):
    p = submitted(service, TEXT)
    o = Output().model_dump()
    o["entities"] = [entity(p, "root", "Synthetic study", "Investigation", "# Synthetic study")]
    o["statements"] = [
        {
            "text": TABLE_TEXT,
            "class_id": "ReportedObservation",
            "epistemic": "measured_observation",
            "subjects": ["root"],
            "study": "current",
            "support": support(p, TABLE_TEXT),
        }
    ]
    record = run(service, p, o, with_tables(service, p))[-1]
    assert record["status"] == "REJECTED"
    assert record["reasons"] == ["TABLE_REGION_IS_NOT_A_STATEMENT"]


LINEAGE = (
    "# Synthetic study\nII. Results\nTABLE 1— Comparison data\n"
    "Material\nEnergy (J)\nReactions/Tests\naBeta\n10\n0/20\na-\n{legend}\n"
    "Beta seals were compared.\nReferences\n[1] Smith, A. B., “Synthetic paper,” 1999.\n"
)


def lineage_record(service, legend):
    p = submitted(service, LINEAGE.format(legend=legend))
    rows = [["Material", "Energy (J)", "Reactions/Tests"], ["aBeta", "10", "0/20"]]
    o = Output().model_dump()
    o["entities"] = [entity(p, "beta", "Beta", "Material", "Beta seals were compared.")]
    return run(service, p, o, with_tables(service, p, rows))[-1]


def test_comparator_printed_only_in_cited_rows_is_not_established_as_tested_here(service):
    cited = lineage_record(service, "Data of Smith")
    assert cited["status"] == "UNRESOLVED"
    assert "CURRENT_STUDY_LINEAGE_NOT_ESTABLISHED" in cited["reasons"]
    assert cited["lineage_context"]["status"] == "CITED_OR_EXTERNAL_ONLY"
    # Same table, a legend that names no cited author: lineage is not contradicted.
    own = lineage_record(service, "Synthetic standard lab")
    assert "CURRENT_STUDY_LINEAGE_NOT_ESTABLISHED" not in own["reasons"]


def lineage_entity(service, legend, label, study, row_label="aBeta"):
    p = submitted(service, LINEAGE.format(legend=legend).replace("aBeta", row_label))
    rows = [["Material", "Energy (J)", "Reactions/Tests"], [row_label, "10", "0/20"]]
    o = Output().model_dump()
    o["entities"] = [entity(p, "beta", label, "Material", "Beta seals were compared.", study=study)]
    return run(service, p, o, with_tables(service, p, rows))[-1]


def test_material_printed_only_in_this_studys_rows_is_not_only_cited(service):
    own = lineage_entity(service, "Synthetic standard lab", "Beta", "cited")
    assert own["status"] == "UNRESOLVED"
    assert "CITED_STUDY_CONTRADICTED_BY_CURRENT_TABLE_ROWS" in own["reasons"]
    # Rows that do carry a cited lineage leave a cited comparator as it is.
    cited = lineage_entity(service, "Data of Smith", "Beta", "cited")
    assert "CITED_STUDY_CONTRADICTED_BY_CURRENT_TABLE_ROWS" not in cited["reasons"]


def test_row_group_with_a_parenthetical_name_counts_for_the_material(service):
    current = lineage_entity(service, "Data of Smith", "Beta", "current", "aBeta (BT)")
    assert "CURRENT_STUDY_LINEAGE_NOT_ESTABLISHED" in current["reasons"]
    # A different name that merely starts the same way is not the same material.
    other = lineage_entity(service, "Data of Smith", "Bet", "current", "aBeta (BT)")
    assert "CURRENT_STUDY_LINEAGE_NOT_ESTABLISHED" not in other["reasons"]


SCOPE = (
    "# Synthetic study\nII. Results\n{before}"
    "Alpha seals were tested at 10 J and passed with no reactions.\n"
    "References\n[1] Smith, A. B., “Synthetic paper,” 1999.\n"
)
OBSERVED = "Alpha seals were tested at 10 J and passed with no reactions."


def scope_record(service, before, text=OBSERVED):
    p = submitted(service, SCOPE.format(before=before))
    o = Output().model_dump()
    o["entities"] = [
        entity(p, "root", "Synthetic study", "Investigation", "# Synthetic study"),
        entity(p, "alpha", "Alpha", "Material", OBSERVED),
    ]
    o["statements"] = [
        {
            "text": text,
            "class_id": "ReportedObservation",
            "epistemic": "measured_observation",
            "subjects": ["alpha"],
            "study": "current",
            "support": support(p, text),
        }
    ]
    return run(service, p, o, structure(p, service.root))[-1]


def test_own_results_section_scopes_a_material_statement_to_the_one_investigation(service):
    record = scope_record(service, "")
    assert record["scope_context"]["basis"] == (
        "ORIGINAL_RESEARCH_SECTION_AT_DOCUMENT_INVESTIGATION_SCOPE"
    )
    assert record["proposed_subjects"] == ["alpha"]
    assert "STATEMENT_REQUIRES_EXPERIMENTAL_SCOPE" not in record["reasons"]


def test_cited_work_named_just_before_keeps_the_statement_out_of_current_scope(service):
    for before in ("The comparison data come from Smith. ", "The data are in Table 4 [1]. "):
        record = scope_record(service, before)
        assert "STATEMENT_REQUIRES_EXPERIMENTAL_SCOPE" in record["reasons"]
        assert record["status"] == "UNRESOLVED"


def test_material_description_is_not_promoted_to_a_current_observation(service):
    text = "Alpha resin is a virgin granular resin."
    p = submitted(service, "# Synthetic study\nII. Results\n" + text + "\n")
    o = Output().model_dump()
    o["entities"] = [
        entity(p, "root", "Synthetic study", "Investigation", "# Synthetic study"),
        entity(p, "alpha", "Alpha", "Material", text),
    ]
    o["statements"] = [
        {
            "text": text,
            "class_id": "ReportedObservation",
            "epistemic": "measured_observation",
            "subjects": ["alpha"],
            "study": "current",
            "support": support(p, text),
        }
    ]
    record = run(service, p, o, structure(p, service.root))[-1]
    assert record["status"] == "UNRESOLVED"
    assert "STATEMENT_REQUIRES_EXPERIMENTAL_SCOPE" in record["reasons"]


def test_one_sentence_accepted_with_two_incompatible_roles_is_held(service):
    text = "Alpha seals were tested at 10 J and passed with no reactions."
    p = submitted(service, "# Synthetic study\nII. Results\n" + text + "\n")
    o = Output().model_dump()
    o["entities"] = [entity(p, "root", "Synthetic study", "Investigation", "# Synthetic study")]
    base = {"text": text, "subjects": ["root"], "study": "current", "support": support(p, text)}
    o["statements"] = [
        {**base, "class_id": "ReportedObservation", "epistemic": "measured_observation"},
        {**base, "class_id": "Publication", "epistemic": "documentary_context"},
    ]
    records = [
        r for r in run(service, p, o, structure(p, service.root)) if r["kind"] == "statements"
    ]
    assert all(r["status"] == "UNRESOLVED" for r in records)
    assert all("CONFLICTING_ROLE_PROPOSALS_FOR_SAME_SOURCE_SPAN" in r["reasons"] for r in records)


def test_two_values_in_one_expression_are_not_one_quantity(service):
    text = "The regulator offered ~.9 and 4.3 psid set-points."
    p = submitted(service, "# Synthetic study\nII. Results\n" + text + "\n")
    o = Output().model_dump()
    o["entities"] = [entity(p, "root", "Synthetic study", "Investigation", "# Synthetic study")]
    o["quantities"] = [
        {
            "subject": "root",
            "label": "set-point",
            "expression": "~.9 and 4.3",
            "unit": "psid",
            "epistemic": "reported_quantity",
            "support": support(p, text),
        }
    ]
    record = run(service, p, o, structure(p, service.root))[-1]
    assert record["reasons"] == ["QUANTITY_EXPRESSION_LISTS_SEPARATE_VALUES"]


def test_first_word_of_a_section_title_is_not_an_outline_prefix(service):
    text = (
        "# Synthetic study\nIntroduction\nBackground words.\nExperimental\nTest Apparatus\n"
        "The rig was built.\nResults and Discussion\nAlpha passed.\nA. Subsection\nBeta passed.\n"
    )
    p = submitted(service, text)
    d = structure(p, service.root)
    span = {"evidence_id": p["evidence"][0]["evidence_id"]}
    assert section_for_span({**span, "start": text.index("The rig")}, d) == (
        "Experimental\nTest Apparatus"
    )
    assert section_for_span({**span, "start": text.index("Alpha passed")}, d) == (
        "Results and Discussion"
    )
    # A punctuated outline letter is still a subsection, not a new major section.
    assert section_for_span({**span, "start": text.index("Beta passed")}, d) == (
        "Results and Discussion"
    )


def test_a_value_with_its_unit_is_not_a_named_entity(service):
    text = "Each sample was impacted at 72 ft-lbs (98J) in the impact tester."
    p = submitted(service, "# Synthetic study\nII. Results\n" + text + "\n")
    o = Output().model_dump()
    o["entities"] = [entity(p, "energy", "72 ft-lbs (98J)", "Intervention", text)]
    record = run(service, p, o, structure(p, service.root))[-1]
    assert record["status"] == "UNRESOLVED"
    assert "NUMERIC_VALUE_IS_NOT_A_NAMED_ENTITY" in record["reasons"]
    thickness = "Both were tested at 0.062 inches in thickness."
    p = submitted(service, "# Synthetic study\nII. Results\n" + thickness + "\n")
    o = Output().model_dump()
    o["entities"] = [
        entity(p, "t", "0.062 inches", "ExperimentalCondition", thickness),
        entity(p, "run", "Run 3", "ExperimentalRun", thickness.replace("Both were", "Run 3 was")),
    ]
    held, named = run(service, p, o, structure(p, service.root))[-2:]
    assert "NUMERIC_VALUE_IS_NOT_A_NAMED_ENTITY" in held["reasons"]
    assert "NUMERIC_VALUE_IS_NOT_A_NAMED_ENTITY" not in named["reasons"]


def test_an_observation_stating_a_purpose_describes_a_procedure(service):
    text = "A post-test picture of an Alpha sample was taken in order to show the extruded layer."
    p = submitted(service, "# Synthetic study\nII. Results\n" + text + "\n")
    o = Output().model_dump()
    o["entities"] = [entity(p, "root", "Synthetic study", "Investigation", "# Synthetic study")]
    o["statements"] = [
        {
            "text": text,
            "class_id": "ReportedObservation",
            "epistemic": "measured_observation",
            "subjects": ["root"],
            "study": "current",
            "support": support(p, text),
        }
    ]
    record = run(service, p, o, structure(p, service.root))[-1]
    assert record["status"] == "UNRESOLVED"
    assert "OBSERVATION_DESCRIBES_A_PROCEDURE" in record["reasons"]


def test_footnote_marker_printed_with_a_row_group_is_not_part_of_the_entity_name(service):
    p = submitted(service, TEXT)
    document = with_tables(service, p)
    outcomes = {}
    for label in ("aAlpha", "Alpha"):
        o = Output().model_dump()
        o["entities"] = [entity(p, "alpha", label, "ExperimentFamily", "aAlpha")]
        outcomes[label] = proposed(run(service, p, o, document))[-1]
    glued, clean = outcomes["aAlpha"], outcomes["Alpha"]
    assert glued["status"] == clean["status"] == "SOURCE_SUPPORTED"
    # Both runs name the same group; the marker is kept as an annotation.
    assert glued["proposal"]["label"] == clean["proposal"]["label"] == "Alpha"
    assert glued["entity_id"] == clean["entity_id"]
    assert glued["label_normalization"]["footnote_marker"] == "a"
    assert glued["label_normalization"]["footnote_legend"] == ["Synthetic standard lab"]
    assert clean["identity_support"]["basis"] == "LEGEND_BACKED_FOOTNOTE_MARKER_ON_ROW_GROUP_LABEL"
    assert clean["identity_support"]["printed_form"] == "aAlpha"


def test_a_letter_without_a_legend_stays_in_the_name_and_a_clean_label_is_absent(service):
    p = submitted(service, TEXT.replace("a-\nSynthetic standard lab\n", ""))
    document = with_tables(service, p)
    o = Output().model_dump()
    o["entities"] = [entity(p, "alpha", "aAlpha", "ExperimentFamily", "aAlpha")]
    kept = proposed(run(service, p, o, document))[-1]
    assert kept["status"] == "SOURCE_SUPPORTED" and kept["proposal"]["label"] == "aAlpha"
    assert "label_normalization" not in kept
    o["entities"] = [entity(p, "alpha", "Alpha", "ExperimentFamily", "aAlpha")]
    absent = proposed(run(service, p, o, document))[-1]
    assert absent["status"] == "REJECTED"
    assert absent["reasons"] == ["ENTITY_LABEL_ABSENT_FROM_SUPPORT"]


def configuration_record(service, text):
    p = submitted(service, "# Synthetic study\nII. Methods\n" + text + "\n")
    o = Output().model_dump()
    o["entities"] = [entity(p, "root", "Synthetic study", "Investigation", "# Synthetic study")]
    o["statements"] = [
        {
            "text": text,
            "class_id": "ExperimentalCondition",
            "epistemic": "experimental_configuration",
            "subjects": ["root"],
            "study": "current",
            "support": support(p, text),
        }
    ]
    return run(service, p, o, structure(p, service.root))[-1]


def test_a_reagent_or_device_that_was_used_is_a_configuration(service):
    used = configuration_record(service, "A mineral oil spike was used to assure combustion.")
    assert "CONFIGURATION_ROLE_NOT_ESTABLISHED_IN_ORIGINAL_PASSAGE" not in used["reasons"]
    documentary = configuration_record(
        service, "The data used in this comparison were obtained from other papers."
    )
    assert "CONFIGURATION_ROLE_NOT_ESTABLISHED_IN_ORIGINAL_PASSAGE" in documentary["reasons"]


def test_prior_to_a_procedure_step_is_not_prior_research(service):
    from nasa_fire_ai.ingestion.document_extraction import original_research_passage

    procedure = (
        "If the temperature rises above 425 C prior to ignition, the AIT is recorded as >425 C."
    )
    lineage = "Prior to this study, Alpha had not been tested at pressure."
    text = "# Synthetic study\nII. Methods\n" + procedure + "\n" + lineage + "\n"
    p = submitted(service, text)
    d = structure(p, service.root)

    def span(sentence):
        start = text.index(sentence)
        return {
            "evidence_id": p["evidence"][0]["evidence_id"],
            "start": start,
            "end": start + len(sentence),
            "quote": sentence,
        }

    assert original_research_passage([span(procedure)], d)
    assert not original_research_passage([span(lineage)], d)


def test_unresolved_proposals_stay_for_review_but_are_never_included_as_knowledge(service):
    first, second = "Alpha seals were tested at 10 J.", "Beta seals passed every test."
    p = submitted(service, first + " " + second)
    page = p["evidence"][0]

    def record(rid, text, status, reasons):
        start = page["text"].index(text)
        return {
            "id": rid,
            "kind": "statements",
            "status": status,
            "reasons": reasons,
            "support_spans": [
                {
                    "evidence_id": page["evidence_id"],
                    "source_id": page["source_id"],
                    "page": 1,
                    "start": start,
                    "end": start + len(text),
                    "quote": text,
                }
            ],
            "proposal": {
                "text": text,
                "class_id": "ReportedObservation",
                "epistemic": "measured_observation",
                "subjects": [],
                "study": "current",
            },
        }

    p["scientific_extraction"] = {
        "records": [
            record("proposal-ok", first, "SOURCE_SUPPORTED", []),
            record(
                "proposal-held", second, "UNRESOLVED", ["STATEMENT_REQUIRES_EXPERIMENTAL_SCOPE"]
            ),
        ],
        "entities_by_key": {},
    }
    service.attach_scientific_proposals(p)
    by_id = {s["id"]: s for s in p["statements"] if s.get("origin") == "contextual"}
    assert by_id["proposal-ok"]["included"] is True
    assert by_id["proposal-ok"]["review_status"] == "SOURCE_SUPPORTED"
    assert by_id["proposal-held"]["included"] is False
    assert by_id["proposal-held"]["review_status"] == "UNRESOLVED"
    assert by_id["proposal-held"]["review_reasons"] == ["STATEMENT_REQUIRES_EXPERIMENTAL_SCOPE"]


def relation(package, subject, name, obj, quote):
    return {"subject": subject, "relation": name, "object": obj, "support": support(package, quote)}


def test_subject_label_names_material_only_with_a_qualifier():
    from nasa_fire_ai.ingestion.document_extraction import subject_label_names_material as names

    assert names("Brass-filled PTFE (Batch #2)", "Brass-filled PTFE")["qualifier"] == "batch #2"
    assert names("Brass-filled PTFE sample", "Brass-filled PTFE")["qualifier"] == "sample"
    assert names("Alpha\n(Lot 1)", "Alpha")["qualifier"] == "lot 1"
    for subject, material in [
        ("Viton A-500", "Viton A"),
        ("Salox-M", "Brass-filled PTFE"),
        ("Brass-filled PTFE", "PTFE"),
        ("Alpha (cited)", "Alpha"),
        ("Alpha", "Alpha"),
        ("PT", "PT"),
    ]:
        assert names(subject, material) is None


def test_a_group_or_sample_named_after_its_material_is_made_of_it(service):
    from nasa_fire_ai.ingestion.document_extraction import extraction_semantic

    text = (
        "# Synthetic study\nII. Results\nAlpha was tested. Alpha (Lot 1) passed. "
        "Alpha-500 failed. Beta samples burned."
    )
    p = submitted(service, text)
    # The draft-local registry carries the ontology's madeOf once extraction exists.
    p["scientific_extraction"] = {"records": []}
    o = Output().model_dump()
    o["entities"] = [
        entity(p, "alpha", "Alpha", "Material", "Alpha was tested."),
        entity(p, "lot", "Alpha (Lot 1)", "ExperimentFamily", "Alpha (Lot 1) passed."),
        entity(p, "a500", "Alpha-500", "Sample", "Alpha-500 failed."),
        entity(p, "beta", "Beta samples", "Sample", "Beta samples burned."),
    ]
    o["relations"] = [
        relation(p, "lot", "madeOf", "alpha", "Alpha (Lot 1) passed."),
        relation(p, "a500", "madeOf", "alpha", "Alpha-500 failed."),
        relation(p, "beta", "madeOf", "alpha", "Beta samples burned."),
        relation(p, "alpha", "madeOf", "alpha", "Alpha was tested."),
    ]
    records = validate_output(
        copy.deepcopy(o), p, structure(p, service.root), extraction_semantic(service, p)
    )["records"]
    rels = [r for r in records if r["kind"] == "relations"]
    assert rels[0]["status"] == "SOURCE_SUPPORTED", rels[0]["reasons"]
    assert rels[0]["context_resolution"]["basis"] == "SUBJECT_LABEL_NAMES_MATERIAL"
    assert rels[0]["context_resolution"]["qualifier"] == "lot 1"
    assert all(r["status"] != "SOURCE_SUPPORTED" for r in rels[1:])
    assert rels[3]["reasons"] == ["RELATION_ENDPOINT_CLASS_CONTRADICTION"]


def test_a_cut_short_omission_recovery_is_retried_on_the_window_halves(service):
    import json
    from types import SimpleNamespace
    from unittest.mock import Mock

    from test_adaptive_extraction import response

    from nasa_fire_ai.config import Settings
    from nasa_fire_ai.ingestion.document_extraction import ExtractionBudget

    text = (
        "Run A1 was tested at pressure 20 Pa.\n"
        + "Documentary background context. " * 45
        + "\nA1 oxygen concentration was measured at 21%."
    )
    p = submitted(service, text)
    c = Mock()
    focused = []

    def respond(**kwargs):
        request = json.loads(kwargs["messages"][1]["content"])
        result = {k: [] for k in request["schema"]["properties"]}
        subject = request["known_entities"][0]["key"] if request["known_entities"] else "a1"
        if request["stage"] == "identity":
            a = next(a for a in request["source_anchors"] if "Run A1" in a["quote"])
            result["entities"] = [
                {
                    "key": "a1",
                    "label": "A1",
                    "class_id": "ExperimentalRun",
                    "study": "current",
                    "support": [a["id"]],
                }
            ]
        elif request["stage"] == "propositions" and request.get("focus") == "quantities":
            local = [a for a in request["source_anchors"] if a["in_task"]]
            focused.append(len(local))
            whole = any("pressure 20" in a["quote"] for a in local) and any(
                "21%" in a["quote"] for a in local
            )
            if whole:
                # The recovery request over the whole window is cut short.
                return SimpleNamespace(
                    choices=[
                        SimpleNamespace(
                            message=SimpleNamespace(content='{"quantities":['),
                            finish_reason="length",
                        )
                    ],
                    usage=None,
                )
            candidates = request["unstructured_quantity_candidates"]
            if candidates:
                result["quantities"] = [
                    {
                        "quantity_ref": candidates[0]["id"],
                        "subject": subject,
                        "label": "oxygen concentration",
                        "epistemic": "reported_quantity",
                    }
                ]
        elif request["stage"] == "propositions":
            a = next(a for a in request["source_anchors"] if "pressure" in a["quote"])
            result["quantities"] = [
                {
                    "subject": subject,
                    "label": "pressure",
                    "expression": "20",
                    "unit": "Pa",
                    "epistemic": "experimental_configuration",
                    "support": [a["id"]],
                }
            ]
        return response(result)

    c.client.with_options.return_value.chat.completions.create.side_effect = respond
    result = service.prepare_scientific(
        p["id"],
        Settings(root=service.root),
        model_enabled=True,
        client=c,
        budget=ExtractionBudget(max_output_tokens=256),
    )
    records = result["package"]["scientific_extraction"]["records"]
    trace = [
        (o["stage"], o.get("focus"), o["model"], o["attempts"], o.get("recovery"))
        for o in result["processing"]["outcomes"]
    ]
    assert any(
        r["kind"] == "quantities" and r["proposal"]["expression"] == "21" for r in records
    ), (
        trace,
        focused,
    )
    # The halves carry fewer anchors than the whole window that was cut short.
    assert len(focused) >= 2 and min(focused) < max(focused), (trace, focused)


def test_a_normalized_identity_still_travels_with_its_printed_anchor(service):
    from nasa_fire_ai.ingestion.document_extraction import grounded_entities

    p = submitted(service, TEXT)
    document = with_tables(service, p)
    o = Output().model_dump()
    o["entities"] = [entity(p, "alpha", "aAlpha", "ExperimentFamily", "aAlpha")]
    window = {"members": document["segments"]}
    known = grounded_entities(o, p, document, service.semantic, window)
    [alpha] = [e for e in known if e["key"] == "alpha"]
    assert alpha["label"] == "Alpha" and alpha["support"] == o["entities"][0]["support"]


def observation_record(
    service, text, epistemic="measured_observation", class_id="ReportedObservation"
):
    p = submitted(service, "# Synthetic study\nII. Results\n" + text + "\n")
    o = Output().model_dump()
    o["entities"] = [entity(p, "root", "Synthetic study", "Investigation", "# Synthetic study")]
    o["statements"] = [
        {
            "text": text,
            "class_id": class_id,
            "epistemic": epistemic,
            "subjects": ["root"],
            "study": "current",
            "support": support(p, text),
        }
    ]
    return run(service, p, o, structure(p, service.root))[-1]


def test_rules_caveats_and_pointers_typed_as_observations_are_held(service):
    held = {
        "A sample is said to have passed the test if no reactions are recorded out of 20 samples.": "OBSERVATION_STATES_A_CRITERION",
        "The determination of compatibility cannot be made from AIT data alone.": "OBSERVATION_STATES_A_RULE_OR_CAVEAT",
        "The impact results for Alpha are shown in Table 3.": "OBSERVATION_IS_A_DOCUMENTARY_POINTER",
    }
    for text, reason in held.items():
        record = observation_record(service, text)
        assert record["status"] == "UNRESOLVED" and reason in record["reasons"], (
            text,
            record["reasons"],
        )
    observed = observation_record(
        service, "Alpha seals were tested at 10 J and passed with no reactions."
    )
    assert not any(r.startswith("OBSERVATION_") for r in observed["reasons"]), observed["reasons"]


def test_a_test_step_without_an_outcome_is_not_an_observation(service):
    step = observation_record(
        service, "Each Alpha seal was impacted with 98 J at 10,000 psia in LOX."
    )
    assert step["status"] == "UNRESOLVED" and "OBSERVATION_DESCRIBES_A_PROCEDURE" in step["reasons"]
    observed = observation_record(
        service,
        "Each Alpha seal was impacted with 98 J at 10,000 psia and passed with no reactions.",
    )
    assert not any(r.startswith("OBSERVATION_") for r in observed["reasons"]), observed["reasons"]


def test_a_validity_caveat_typed_as_an_interpretation_is_held(service):
    caveat = "These percentages are only valid for an AIT value below the maximum test temperature."
    record = observation_record(
        service, caveat, epistemic="tentative_interpretation", class_id="NASAConclusion"
    )
    assert record["status"] == "UNRESOLVED", record["reasons"]
    assert "INTERPRETATION_STATES_A_VALIDITY_CAVEAT" in record["reasons"]
    reading = observation_record(
        service,
        "Since the filler fraction is not known, it can only be speculated that the filler is zinc.",
        epistemic="tentative_interpretation",
        class_id="NASAConclusion",
    )
    assert "INTERPRETATION_STATES_A_VALIDITY_CAVEAT" not in reading["reasons"]


def test_a_validity_caveat_typed_as_a_configuration_is_held(service):
    caveat = "These percentages are only valid for an AIT value below the maximum test temperature."
    record = observation_record(
        service, caveat, epistemic="experimental_configuration", class_id="ExperimentalCondition"
    )
    assert record["status"] == "UNRESOLVED", record["reasons"]
    assert "CONFIGURATION_STATES_A_VALIDITY_CAVEAT" in record["reasons"]
    setup = observation_record(
        service,
        "The Alpha chamber was purged with oxygen before pressurization.",
        epistemic="experimental_configuration",
        class_id="ExperimentalCondition",
    )
    assert "CONFIGURATION_STATES_A_VALIDITY_CAVEAT" not in setup["reasons"]


def test_a_table_caption_with_a_dash_is_not_an_experiment_family(service):
    caption = "Table 3—Impact data of synthetic compounds"
    series = "Alpha impact series"
    p = submitted(service, "# Synthetic study\nII. Results\n" + caption + "\n" + series + "\n")
    o = Output().model_dump()
    o["entities"] = [entity(p, "fam", caption, "ExperimentFamily", caption)]
    record = run(service, p, o, structure(p, service.root))[-1]
    assert record["status"] == "UNRESOLVED"
    assert "CAPTION_IS_NOT_ESTABLISHED_EXPERIMENT_IDENTITY" in record["reasons"]
    o["entities"] = [entity(p, "fam", series, "ExperimentFamily", series)]
    record = run(service, p, o, structure(p, service.root))[-1]
    assert "CAPTION_IS_NOT_ESTABLISHED_EXPERIMENT_IDENTITY" not in record["reasons"]


TESTED = (
    "# Synthetic study\nII. Results\nTABLE 1— Comparison data\n"
    "Material\nEnergy (J)\nReactions/Tests\naBeta\n10\n0/20\na-\n{legend}\n"
    "Beta seals were compared. The Beta heat of combustion was 1332 cal/g.\n"
    "References\n[1] Smith, A. B., “Synthetic paper,” 1999.\n"
)


def material_quantity_record(service, legend):
    sentence = "The Beta heat of combustion was 1332 cal/g."
    p = submitted(service, TESTED.format(legend=legend))
    rows = [["Material", "Energy (J)", "Reactions/Tests"], ["aBeta", "10", "0/20"]]
    o = Output().model_dump()
    o["entities"] = [entity(p, "beta", "Beta", "Material", "Beta seals were compared.")]
    o["quantities"] = [
        {
            "subject": "beta",
            "label": "heat of combustion",
            "expression": "1332",
            "unit": "cal/g",
            "epistemic": "reported_quantity",
            "support": support(p, sentence),
        }
    ]
    return run(service, p, o, with_tables(service, p, rows))[-1]


def test_prose_value_of_a_material_this_document_tests_is_scoped_to_this_study(service):
    record = material_quantity_record(service, "Synthetic standard lab")
    assert record["status"] == "SOURCE_SUPPORTED", record["reasons"]
    assert record["scope_context"] == {
        "basis": "MATERIAL_ESTABLISHED_AS_TESTED_IN_THIS_STUDY",
        "experimental_scope": "DOCUMENT_INVESTIGATION",
        "general_material_property": False,
    }
    # Never projected as a general material property.
    assert record["native_scope_compatible"] is False
    # A material printed only in cited rows is not established as tested here.
    cited = material_quantity_record(service, "Data of Smith")
    assert cited["status"] == "UNRESOLVED"
    assert "QUANTITY_REQUIRES_EXPERIMENTAL_SCOPE_NOT_MATERIAL_CONCEPT" in cited["reasons"]


def test_recovery_skips_values_already_printed_in_a_table_cell(service):
    from nasa_fire_ai.ingestion.table_continuity import printed_in_table

    p = submitted(service, TEXT)
    document = with_tables(service, p)
    page = p["evidence"][0]["page"]
    assert printed_in_table(document, page, "2/20")
    assert not printed_in_table(document, page, "3/20")
    assert not printed_in_table(document, page + 1, "2/20")


IMPACT = (
    "# Synthetic study\nII. Results\nTABLE 1— Impact data\n"
    "Material\nImpact Energy (J)\nSystem Pressure (psia)\nReactions/Tests\n"
    "aBeta (Lot #1)\n98\n10,000\n0/20\na-\nSynthetic standard lab\n"
    "The data show that Beta is compatible. It was impacted with 98 Joules at 10,000 psia.\n"
    "Gamma was compared. It was impacted with 98 Joules at 10,000 psia.\n"
)
IMPACT_ROWS = [
    ["Material", "Impact Energy (J)", "System Pressure (psia)", "Reactions/Tests"],
    ["aBeta (Lot #1)", "98", "10,000", "0/20"],
]


def impact_output(p, subject_label, sentence, epistemic="experimental_configuration"):
    o = Output().model_dump()
    o["entities"] = [
        entity(p, "beta", "Beta", "Material", "The data show that Beta is compatible."),
        entity(p, "gamma", "Gamma", "Material", "Gamma was compared."),
    ]
    o["quantities"] = [
        {
            "subject": subject_label,
            "label": "impact energy",
            "expression": "98",
            "unit": "Joules",
            "epistemic": epistemic,
            "support": support(p, sentence),
        }
    ]
    return o


def test_prose_value_named_by_its_subjects_own_table_column_and_pronoun(service):
    p = submitted(service, IMPACT)
    document = with_tables(service, p, IMPACT_ROWS)
    beta = "The data show that Beta is compatible. It was impacted with 98 Joules at 10,000 psia."
    record = proposed(run(service, p, impact_output(p, "beta", beta), document))[-1]
    assert record["status"] == "SOURCE_SUPPORTED", record["reasons"]
    assert (
        record["quantity_name_support"]["basis"] == "SAME_SUBJECT_VALUE_UNDER_DOCUMENT_TABLE_COLUMN"
    )
    assert record["subject_antecedent"]["basis"] == "PRONOUN_SUBJECT_OF_PRECEDING_SENTENCE"
    # The same printed value for a material without such a row has no name.
    gamma = "Gamma was compared. It was impacted with 98 Joules at 10,000 psia."
    other = proposed(run(service, p, impact_output(p, "gamma", gamma), document))[-1]
    assert other["status"] != "SOURCE_SUPPORTED"
    # What was applied is not a measured result.
    measured = proposed(
        run(service, p, impact_output(p, "beta", beta, "reported_quantity"), document)
    )[-1]
    assert measured["status"] == "REJECTED"
    assert "APPLIED_TEST_INPUT_IS_NOT_A_MEASUREMENT" in measured["reasons"]


def test_printed_relative_difference_is_kept_as_a_derived_value(service):
    text = "Run A1 was tested. The A1 heat of combustion was 12% lower than the reference."
    p = submitted(service, text)
    o = Output().model_dump()
    o["entities"] = [entity(p, "run", "A1", "ExperimentalRun", text)]
    q = {
        "subject": "run",
        "label": "heat of combustion",
        "expression": "12% lower",
        "unit": None,
        "epistemic": "derived_quantity",
        "support": support(p, text),
    }
    o["quantities"] = [q]
    record = run(service, p, o, structure(p, service.root))[-1]
    assert record["status"] == "SOURCE_SUPPORTED", record["reasons"]
    assert (record["proposal"]["expression"], record["proposal"]["unit"]) == ("12", "%")
    assert record["relative_comparison"]["comparative"] == "lower"
    q["epistemic"] = "reported_quantity"
    reported = run(service, p, o, structure(p, service.root))[-1]
    assert "RELATIVE_DIFFERENCE_IS_A_DERIVED_QUANTITY" in reported["reasons"]


def test_a_row_group_of_a_material_is_preferred_over_the_material(service):
    p = submitted(service, IMPACT)
    document = with_tables(service, p, IMPACT_ROWS)
    o = Output().model_dump()
    o["entities"] = [
        entity(p, "root", "Synthetic study", "Investigation", "# Synthetic study"),
        entity(p, "beta", "Beta", "Material", "The data show that Beta is compatible."),
        entity(p, "lot", "aBeta (Lot #1)", "Sample", "aBeta (Lot #1)"),
    ]
    rows = "\n".join(v for row in IMPACT_ROWS for v in row)
    o["quantities"] = [
        {
            "subject": "root",
            "label": "Reactions/Tests",
            "expression": "0/20",
            "unit": None,
            "epistemic": "reported_quantity",
            "support": support(p, rows.replace("aBeta (Lot #1)", "aBeta (Lot #1)")),
        }
    ]
    result = validate_output(copy.deepcopy(o), p, document, service.semantic)
    record = proposed(result["records"])[-1]
    assert record["subject"] == result["entities_by_key"]["lot"]["id"], record["reasons"]
    assert record["subject_recovery"]["status"] == "RECOVERED"


CONDITIONS = (
    "# Synthetic study\nII. Results\nTABLE 1— Impact data\n"
    "Material\nTest Conditions\nReactions/Tests\n"
    "aBeta (Lot #1)\nLOX/-200°F\n0/20\nGOX/70°F\n0/20\na-\n{legend}\n"
    "Beta was tested in LOX/-200°F and GOX/70°F.\n"
    "References\n[1] Smith, A. B., “Synthetic paper,” 1999.\n"
)
CONDITION_ROWS = [
    ["Material", "Test Conditions", "Reactions/Tests"],
    ["aBeta (Lot #1)", "LOX/-200°F", "0/20"],
    ["", "GOX/70°F", "0/20"],
]


def structural_records(service, legend="Synthetic standard lab", condition_study="current"):
    p = submitted(service, CONDITIONS.format(legend=legend))
    o = Output().model_dump()
    o["entities"] = [
        entity(p, "beta", "Beta", "Material", "Beta was tested in LOX/-200°F and GOX/70°F."),
        entity(p, "lot", "aBeta (Lot #1)", "Sample", "aBeta (Lot #1)"),
        entity(
            p,
            "lox",
            "LOX/-200°F",
            "ExperimentalCondition",
            "tested in LOX/-200°F",
            study=condition_study,
        ),
    ]
    from nasa_fire_ai.ingestion.document_extraction import extraction_semantic

    records = validate_output(
        copy.deepcopy(o),
        p,
        with_tables(service, p, CONDITION_ROWS),
        extraction_semantic(service, p),
    )["records"]
    lox = next(r["entity_id"] for r in records if r["proposal"].get("key") == "lox")
    return {
        r["proposal"]["relation"]: r
        for r in records
        if r["kind"] == "relations"
        and r.get("candidate_origin") == "PRINTED_SOURCE_STRUCTURE"
        and (r["proposal"]["relation"] != "hasCondition" or r.get("object") == lox)
    }


def test_printed_structure_proposes_membership_and_row_conditions_for_validation(service):
    relations = structural_records(service)
    assert relations["madeOf"]["status"] == "SOURCE_SUPPORTED"
    condition = relations["hasCondition"]
    assert condition["status"] == "SOURCE_SUPPORTED", condition["reasons"]
    assert condition["context_resolution"]["basis"] == "SUBJECT_TABLE_ROWS_PRINT_CONDITION"
    # A cited condition entity is never attached to this study's group.
    assert "hasCondition" not in structural_records(service, condition_study="cited")
    # Rows with a cited lineage do not give this group its condition.
    assert "hasCondition" not in structural_records(service, legend="Data of Smith")


def test_values_and_instruments_are_not_named_conditions_or_interventions(service):
    text = (
        "The plummet impacted the Run 3 sample at 98 Joules of energy (72 ft-lbs). "
        "Heating at 9 degrees F/min used an external heater. A water spray was applied."
    )
    p = submitted(service, "# Synthetic study\nII. Results\n" + text + "\n")
    o = Output().model_dump()
    o["entities"] = [
        entity(p, "e", "98 Joules of energy (72 ft-lbs)", "ExperimentalCondition", text),
        entity(p, "r", "9 degrees F/min", "ExperimentalCondition", text),
        entity(p, "h", "external heater", "Intervention", text),
        entity(p, "pl", "plummet", "Intervention", text),
        entity(p, "w", "water spray", "Intervention", text),
    ]
    energy, rate, heater, plummet, spray = run(service, p, o, structure(p, service.root))
    assert "NUMERIC_VALUE_IS_NOT_A_NAMED_ENTITY" in energy["reasons"]
    assert "NUMERIC_VALUE_IS_NOT_A_NAMED_ENTITY" in rate["reasons"]
    assert "APPARATUS_OR_METHOD_IS_NOT_AN_INTERVENTION" in heater["reasons"]
    assert "APPARATUS_OR_METHOD_IS_NOT_AN_INTERVENTION" in plummet["reasons"]
    assert "APPARATUS_OR_METHOD_IS_NOT_AN_INTERVENTION" not in spray["reasons"]
    named = "Run 3 used 100% PBI knit fabric in 37% O2 at 8.2 psia."
    p = submitted(service, "# Synthetic study\nII. Results\n" + named + "\n")
    o = Output().model_dump()
    o["entities"] = [
        entity(p, "m", "100% PBI knit fabric", "Material", named),
        entity(p, "a", "37% O2 at 8.2 psia", "ExperimentalCondition", named),
    ]
    for record in run(service, p, o, structure(p, service.root)):
        assert "NUMERIC_VALUE_IS_NOT_A_NAMED_ENTITY" not in record["reasons"]


SPECIMENS = (
    "# Synthetic study\nII. Results\nThe Beta samples discussed in this paper were tested.\n"
    "TABLE 1— Combustion data\nMaterial\nHeat (cal/g)\nStandard Deviation (cal/g)\n"
    "aBeta\n1332\n13.81\na-\n{legend}\n"
    "References\n[1] Smith, A. B., “Synthetic paper,” 1999.\n"
)
SPECIMEN_ROWS = [
    ["Material", "Heat (cal/g)", "Standard Deviation (cal/g)"],
    ["aBeta", "1332", "13.81"],
]


def specimen_records(service, legend):
    from nasa_fire_ai.ingestion.document_extraction import extraction_semantic

    p = submitted(service, SPECIMENS.format(legend=legend))
    o = Output().model_dump()
    o["entities"] = [
        entity(p, "root", "Synthetic study", "Investigation", "# Synthetic study"),
        entity(p, "beta", "Beta", "Material", "The Beta samples discussed in this paper"),
    ]
    return validate_output(
        copy.deepcopy(o), p, with_tables(service, p, SPECIMEN_ROWS), extraction_semantic(service, p)
    )["records"]


def test_printed_specimens_their_study_and_a_dispersion_column_are_validated_candidates(
    service,
):
    records = [
        r for r in specimen_records(service, "Synthetic standard lab") if r.get("candidate_origin")
    ]
    by = {
        (r["kind"], r["proposal"].get("label") or r["proposal"].get("relation")): r for r in records
    }
    assert by[("entities", "Beta samples")]["status"] == "SOURCE_SUPPORTED"
    member = by[("relations", "belongsToInvestigation")]
    assert member["status"] == "SOURCE_SUPPORTED", member["reasons"]
    assert member["context_resolution"]["basis"] == "SUBJECT_DISCUSSED_IN_THIS_DOCUMENT"
    spread = by[("quantities", "Standard Deviation")]
    assert spread["status"] == "SOURCE_SUPPORTED", spread["reasons"]
    assert spread["proposal"]["epistemic"] == "derived_quantity"
    # Cited rows: the material is not tested here, so no candidate is proposed.
    cited = [r for r in specimen_records(service, "Data of Smith") if r.get("candidate_origin")]
    assert not [r for r in cited if r["status"] == "SOURCE_SUPPORTED"]


def test_a_role_only_hold_is_revalidated_with_the_detected_role(service):
    rule = (
        "If the system temperature rises above 400°C prior to ignition, then the AIT is "
        "recorded as >400°C."
    )
    record = observation_record(
        service, rule, epistemic="experimental_configuration", class_id="ExperimentalCondition"
    )
    assert record["status"] == "SOURCE_SUPPORTED", record["reasons"]
    assert record["proposal"]["epistemic"] == "normative_requirement"
    assert record["role_recovery"]["proposed_epistemic"] == "experimental_configuration"
    assert record["role_recovery"]["method"] == "FULL_REVALIDATION_WITH_THE_DETECTED_ROLE"


def test_a_reading_of_a_cited_table_is_never_this_studys_observation(service):
    text = (
        "TABLE 6— Synthetic impact data [1]\nMaterial\nReactions\naGamma\n2/20\n"
        "The data listed in Table 6 indicate that Gamma reacted. "
        "The reactivity of the same material increases by 20% as the thickness is halved.\n"
        "References\n[1] Smith, A. B., “Synthetic paper,” 1999.\n"
    )
    p = submitted(service, "# Synthetic study\nII. Results\n" + text)
    o = Output().model_dump()
    o["entities"] = [entity(p, "root", "Synthetic study", "Investigation", "# Synthetic study")]
    sentence = "The reactivity of the same material increases by 20% as the thickness is halved."
    o["statements"] = [
        {
            "text": sentence,
            "class_id": "Measurement",
            "epistemic": "derived_quantity",
            "subjects": ["root"],
            "study": "current",
            "support": support(p, sentence),
        }
    ]
    document = with_tables(service, p, [["Material", "Reactions"], ["aGamma", "2/20"]])
    document["detected_tables"][0]["caption"] = "TABLE 6— Synthetic impact data [1]"
    record = proposed(run(service, p, o, document))[-1]
    assert record["status"] != "SOURCE_SUPPORTED", record.get("role_recovery")


def test_a_column_the_document_applies_holds_settings_not_results(service):
    p = submitted(service, IMPACT)
    document = with_tables(service, p, IMPACT_ROWS)
    rows = "\n".join(v for row in IMPACT_ROWS for v in row)
    o = Output().model_dump()
    o["entities"] = [entity(p, "lot", "aBeta (Lot #1)", "Sample", "aBeta (Lot #1)")]
    o["quantities"] = [
        {
            "subject": "lot",
            "label": label,
            "expression": value,
            "unit": unit,
            "epistemic": "reported_quantity",
            "support": support(p, rows),
        }
        for label, value, unit in [
            ("System Pressure", "10,000", "psia"),
            ("Reactions/Tests", "0/20", None),
        ]
    ]
    pressure, reactions = [
        r for r in proposed(run(service, p, o, document)) if r["kind"] == "quantities"
    ]
    # "It was impacted with 98 Joules at 10,000 psia": the pressure is a setting.
    assert pressure["proposal"]["epistemic"] == "experimental_configuration", pressure["reasons"]
    assert pressure["role_recovery"]["basis"] == "COLUMN_VALUE_APPLIED_IN_A_TEST_STEP"
    # A count is never made a setting by a sentence that also counts samples.
    assert reactions["proposal"]["epistemic"] == "reported_quantity"
    assert "role_recovery" not in reactions


def test_a_columns_state_word_settles_a_setting_versus_result_conflict(service):
    text = (
        "# Synthetic study\nII. Results\nTABLE 1— AIT data\nMaterial\nInitial Pressure (psia)\n"
        "Final Pressure (psia)\naBeta\n1500\n2268\na-\nSynthetic standard lab\n"
    )
    rows = [
        ["Material", "Initial Pressure (psia)", "Final Pressure (psia)"],
        ["aBeta", "1500", "2268"],
    ]
    p = submitted(service, text)
    document = with_tables(service, p, rows)
    table = "\n".join(v for row in rows for v in row)
    o = Output().model_dump()
    o["entities"] = [entity(p, "lot", "aBeta", "Sample", "aBeta")]
    o["quantities"] = [
        {
            "subject": "lot",
            "label": name,
            "expression": value,
            "unit": "psia",
            "epistemic": role,
            "support": support(p, table),
        }
        for name, value in [("Initial Pressure", "1500"), ("Final Pressure", "2268")]
        for role in ("experimental_configuration", "reported_quantity")
    ]
    records = {
        (r["proposal"]["label"], r["proposal"]["epistemic"]): r
        for r in proposed(run(service, p, o, document))
        if r["kind"] == "quantities"
    }
    assert records[("Final Pressure", "reported_quantity")]["status"] == "SOURCE_SUPPORTED"
    assert records[("Final Pressure", "experimental_configuration")]["status"] == "UNRESOLVED"
    # "initial" makes the reported reading of the same cell the one that is wrong.
    assert records[("Initial Pressure", "reported_quantity")]["status"] != "SOURCE_SUPPORTED"


def test_a_printed_group_of_a_material_proposed_as_a_material_is_its_specimen_group(service):
    p = submitted(service, IMPACT)
    document = with_tables(service, p, IMPACT_ROWS)
    o = Output().model_dump()
    o["entities"] = [
        entity(p, "beta", "Beta", "Material", "The data show that Beta is compatible."),
        entity(p, "lot", "aBeta (Lot #1)", "Material", "aBeta (Lot #1)"),
        entity(p, "gamma", "Gamma", "Material", "Gamma was compared."),
    ]
    records = {
        r["proposal"]["key"]: r
        for r in proposed(run(service, p, o, document))
        if r["kind"] == "entities"
    }
    assert records["lot"]["proposal"]["class_id"] == "Sample"
    assert (
        records["lot"]["class_recovery"]["basis"]
        == "PRINTED_ROW_GROUP_NAMES_A_GROUP_OF_A_PROPOSED_MATERIAL"
    )
    # A material that is not a printed group of another stays a material.
    assert records["gamma"]["proposal"]["class_id"] == "Material"
    assert "class_recovery" not in records["beta"]


def test_a_detection_criterion_typed_as_an_observation_is_held(service):
    criterion = observation_record(
        service, "The indication of autogenous ignition was the rapid increase of temperature."
    )
    assert criterion["status"] == "UNRESOLVED"
    assert "OBSERVATION_STATES_A_CRITERION" in criterion["reasons"]
    seen = observation_record(service, "An indication of reaction was seen in two Alpha samples.")
    assert "OBSERVATION_STATES_A_CRITERION" not in seen["reasons"]


def test_a_procedure_typed_as_an_interpretation_is_held(service):
    step = observation_record(
        service,
        "After the tests were conducted, the samples were analyzed for signs of combustion.",
        epistemic="tentative_interpretation",
        class_id="NASAConclusion",
    )
    assert step["status"] == "UNRESOLVED"
    assert "INTERPRETATION_DESCRIBES_A_PROCEDURE" in step["reasons"]
    reading = observation_record(
        service,
        "The samples were analyzed for signs of combustion, which suggests none occurred.",
        epistemic="tentative_interpretation",
        class_id="NASAConclusion",
    )
    assert "INTERPRETATION_DESCRIBES_A_PROCEDURE" not in reading["reasons"]


def same_anaphor_record(service, before, epistemic="experimental_configuration"):
    same = "The same compounds were then tested in a high-pressure LOX environment."
    p = submitted(service, "# Synthetic study\nII. Results\n" + before + " " + same + "\n")
    o = Output().model_dump()
    o["entities"] = [entity(p, "root", "Synthetic study", "Investigation", "# Synthetic study")]
    o["statements"] = [
        {
            "text": same,
            "class_id": "Publication"
            if epistemic == "documentary_context"
            else "ExperimentalCondition",
            "epistemic": epistemic,
            "subjects": ["root"],
            "study": "current",
            "support": support(p, same),
        }
    ]
    return run(service, p, o, structure(p, service.root))[-1]


def test_a_same_anaphor_after_cited_work_is_not_this_study(service):
    cited = "The impact data is presented in Table 4 [3]. The compounds were not sensitive."
    record = same_anaphor_record(service, cited)
    assert record["status"] == "UNRESOLVED"
    assert "SAME_ANAPHOR_CONTINUES_CITED_WORK" in record["reasons"]
    narrative = same_anaphor_record(service, cited, epistemic="documentary_context")
    assert "SAME_ANAPHOR_CONTINUES_CITED_WORK" not in narrative["reasons"]
    own = same_anaphor_record(service, "Alpha seals were impacted at 98 J. None reacted.")
    assert "SAME_ANAPHOR_CONTINUES_CITED_WORK" not in own["reasons"]


def test_a_test_medium_is_not_a_tested_material(service):
    text = "The chamber was pressurized with GOX. Alpha seals were tested at 98 J."
    p = submitted(service, "# Synthetic study\nII. Methods\n" + text + "\n")
    o = Output().model_dump()
    o["entities"] = [
        entity(p, "g", "GOX", "Material", "The chamber was pressurized with GOX."),
        entity(p, "a", "Alpha", "Material", "Alpha seals were tested at 98 J."),
    ]
    gox, alpha = run(service, p, o, structure(p, service.root))
    assert gox["status"] == "UNRESOLVED"
    assert "TEST_MEDIUM_IS_NOT_A_TESTED_MATERIAL" in gox["reasons"]
    assert "TEST_MEDIUM_IS_NOT_A_TESTED_MATERIAL" not in alpha["reasons"]
