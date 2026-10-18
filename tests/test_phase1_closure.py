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
    assert plain["status"] == "REJECTED"


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
