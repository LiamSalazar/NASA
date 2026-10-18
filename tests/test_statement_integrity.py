"""Synthetic statement integrity and cited-attribution checks; never NASA data."""

from nasa_fire_ai.ingestion.statement_integrity import (
    conflicting_roles,
    count_conflict,
    fragment_context,
    observation_cue,
    stated_criterion,
)
from nasa_fire_ai.ingestion.study_attribution import cited_attribution_nearby, reference_authors

REFERENCES = "References\n[1] Smith, A. B. and Jones, C., “Synthetic paper,” 1999.\n[2] Lee, D., “Other,” 2001.\n"


def doc(text):
    return {
        "segments": [
            {"evidence_id": "E1", "source_id": "S", "page": 1, "text": text},
            {"evidence_id": "R", "source_id": "S", "page": 2, "text": REFERENCES},
        ],
        "sections": [
            {"evidence_id": "R", "source_id": "S", "start": 0, "end": 10, "title": "References"}
        ],
    }


def span(text, quote):
    start = text.index(quote)
    return {"evidence_id": "E1", "start": start, "end": start + len(quote), "quote": quote}


def test_reference_list_authors_are_read_from_the_document_itself():
    assert reference_authors(doc("x")) == {"Smith", "Jones", "Lee"}


def test_named_cited_work_or_its_pronoun_is_not_the_current_study():
    text = (
        "The data presented by Smith and Jones is only a pass indication. "
        "Their data indicates that only one polymer passed. "
        "Our seal passed every test."
    )
    d = doc(text)
    assert cited_attribution_nearby(
        [span(text, "Their data indicates that only one polymer passed.")], d
    )
    assert cited_attribution_nearby([span(text, "The data presented by Smith and Jones")], d)
    assert cited_attribution_nearby([span(text, "Our seal passed every test.")], d) is None


def test_preceding_bracket_citation_marks_the_next_sentence():
    text = "The impact data is presented in Table 4 [3]. The results show the compounds were not sensitive."
    d = doc(text)
    assert cited_attribution_nearby(
        [span(text, "The results show the compounds were not sensitive.")], d
    )
    clean = "The impact data is presented in Table 3. The results show the compounds were not sensitive."
    assert (
        cited_attribution_nearby(
            [span(clean, "The results show the compounds were not sensitive.")], doc(clean)
        )
        is None
    )


def test_a_pronoun_in_the_previous_sentence_does_not_attribute_by_itself():
    text = "Both seals were compared and their performance was similar. The new seal passed."
    assert cited_attribution_nearby([span(text, "The new seal passed.")], doc(text)) is None


def pages(*texts):
    return {
        f"E{i}": {"evidence_id": f"E{i}", "source_id": "S", "page": i, "text": t}
        for i, t in enumerate(texts, 1)
    }


def located(evidence, key, quote):
    start = evidence[key]["text"].index(quote)
    return {"evidence_id": key, "start": start, "end": start + len(quote)}


def test_statement_cut_at_an_abbreviation_is_a_fragment():
    ev = pages("1\nUnder the same conditions, i.e. thickness and energy, it passed.\n")
    quote = "Under the same conditions, i.e."
    assert (
        fragment_context(quote, located(ev, "E1", quote), ev)["basis"]
        == "STATEMENT_ENDS_AT_ABBREVIATION"
    )


def test_sentence_cut_at_a_page_break_is_a_fragment_both_ways():
    ev = pages(
        "1\nThe sensitivity was attributed to the high percentage of\n",
        "2\nBronze filler in the compound.\nA separate sentence follows.\n",
    )
    tail = "The sensitivity was attributed to the high percentage of"
    assert fragment_context(tail, located(ev, "E1", tail), ev)["basis"] == (
        "SENTENCE_CONTINUES_ON_NEXT_PDF_PAGE"
    )
    head = "Bronze filler in the compound."
    assert fragment_context(head, located(ev, "E2", head), ev)["basis"] == (
        "SENTENCE_STARTS_ON_PREVIOUS_PDF_PAGE"
    )
    whole = "A separate sentence follows."
    assert fragment_context(whole, located(ev, "E2", whole), ev) is None


def test_a_slide_bullet_ending_a_page_without_punctuation_is_whole():
    ev = pages(
        "1\n• 1-g extinction happens 45 seconds sooner than partial-g extinction\n", "2\nNext.\n"
    )
    quote = "1-g extinction happens 45 seconds sooner than partial-g extinction"
    assert fragment_context(quote, located(ev, "E1", quote), ev) is None


def test_a_page_ending_with_a_full_sentence_does_not_mark_the_next_page():
    ev = pages("1\nThe first page ends here.\n", "2\nBronze filler was used.\n")
    quote = "Bronze filler was used."
    assert fragment_context(quote, located(ev, "E2", quote), ev) is None


def test_conflicting_counts_printed_together_are_held_for_review():
    text = (
        "Neither the wet nor dry tests showed any reactions out of the 80 impacts. "
        "Four of the additional 80 wet samples reacted with no remaining sample."
    )
    ev = pages(text)
    zero = "Neither the wet nor dry tests showed any reactions out of the 80 impacts."
    four = "Four of the additional 80 wet samples reacted with no remaining sample."
    assert count_conflict(located(ev, "E1", zero), ev)
    assert count_conflict(located(ev, "E1", four), ev)
    other = pages(zero + " Four of the additional 40 wet samples reacted.")
    assert count_conflict(located(other, "E1", zero), other) is None


def test_observation_requires_testing_or_result_wording():
    assert observation_cue("No reactions were recorded out of 20 samples.")
    assert observation_cue("The post-test picture shows the extruded material.")
    assert not observation_cue(
        "Alpha resin is a virgin granular resin which has been pre-sintered."
    )
    assert not observation_cue("The composition of Beta is 40% bronze and 60% polymer.")


def test_a_procedure_with_a_purpose_clause_is_not_an_observation():
    assert not observation_cue("A post-test picture was taken in order to show the extruded layer.")
    assert observation_cue("The post-test picture shows the extruded layer.")


def test_acceptance_and_recording_rules_are_criteria_not_configuration():
    assert stated_criterion("A sample is said to have passed if no reactions are recorded.")
    assert stated_criterion(
        "If the temperature rises above 425 C, then the AIT is recorded as >425 C."
    )
    assert stated_criterion("The pass/fail criterion is the number of reactions.")
    assert not stated_criterion("The chamber was pressurized with GOX and lowered into the bath.")


def record(rid, epistemic, start=0, status="SOURCE_SUPPORTED"):
    return {
        "id": rid,
        "kind": "statements",
        "status": status,
        "proposal": {"epistemic": epistemic},
        "statement_location": {"evidence_id": "E1", "start": start, "end": 40},
    }


def test_one_span_accepted_with_incompatible_roles_is_held():
    records = [
        record("a", "experimental_configuration"),
        record("b", "tentative_interpretation"),
        record("c", "tentative_interpretation", start=50),
        record("d", "hypothesis", start=50),
        record("e", "measured_observation", start=90),
        record("f", "documentary_context", start=90, status="UNRESOLVED"),
    ]
    assert conflicting_roles(records) == {"a", "b"}
