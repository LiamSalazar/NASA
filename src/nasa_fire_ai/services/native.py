"""Native scientist-facing boundary with conservative generation and offline fallback."""

from dataclasses import dataclass

from nasa_fire_ai.models import GroundedAnswerDraft
from nasa_fire_ai.query.native import NativeExecutionResult, execute_native
from nasa_fire_ai.services.grounding import GroundingResult, GroundingValidator
from nasa_fire_ai.services.renderer import render


def validate_native_draft(draft, bundle):
    """Metadata grounding plus exact-source quotation gate.

    Existing metadata validation cannot independently establish paraphrase fidelity.
    Until expert gold exists, only verbatim source passages may become visible claims;
    generated summaries and limitations are not rendered as scientific content.
    """
    result = GroundingValidator().validate(draft, bundle)
    errors = list(result.errors)
    texts = {p["evidence_id"]: [p["text"]] for p in bundle.evidence_passages}
    for field in (
        "experimental_observations",
        "interventions",
        "nasa_conclusions",
        "safety_implications",
        "requirements",
        "guidance",
        "design_test_criteria",
        "nasa_identified_open_questions",
    ):
        for item in getattr(bundle, field):
            ids = item.get("evidence_ids", []) + [
                r["evidence_id"] for r in item.get("evidence_refs", [])
            ]
            text = item.get("normalized_text", item.get("text", item.get("description", "")))
            for eid in ids:
                texts.setdefault(eid, []).append(text)
    for claim in draft.claims:
        if not claim.evidence_ids or not all(
            any(claim.text.strip() == text.strip() for text in texts.get(eid, []))
            for eid in claim.evidence_ids
        ):
            errors.append(
                f"{claim.claim_id}: source quotation required; paraphrase fidelity unreviewed"
            )
    return GroundingResult(valid=not errors, errors=errors)


@dataclass(frozen=True)
class NativeResponse:
    execution: NativeExecutionResult
    draft: GroundedAnswerDraft | None
    rendered_answer: str
    fallback: bool
    grounding_errors: list[str]


def answer_native(intent, query, store, evidence_registry, draft=None):
    result = execute_native(intent, query, store, evidence_registry)
    rendered = render(result.bundle)
    accepted = None
    errors = []
    if draft is not None:
        validation = validate_native_draft(draft, result.bundle)
        errors = validation.errors
        if validation.valid:
            accepted = draft
            quoted = "\n".join(f"{c.text} [{', '.join(c.evidence_ids)}]" for c in draft.claims)
            rendered += "\nSource quotations:\n" + quoted
    return NativeResponse(result, accepted, rendered, accepted is None, errors)
