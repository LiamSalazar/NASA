"""Proposal states and the vocabulary extensions a source needs; nothing here is activated.

A validated record is in exactly one of these states. The last two are reached only
through curation (review, then authorized publication), never by extraction:

- REJECTED: unsupported by the source; kept for audit.
- STRUCTURALLY_WELL_FORMED: parsed and anchored, but a source or scientific check is
  still open.
- SOURCE_SUPPORTED: supported by the source with the approved vocabulary.
- PROPOSED_ONTOLOGY_EXTENSION: supported by the source except that a class, statement
  class or relation it uses is not in the approved vocabulary; the term is staged as
  an extension proposal beside it.
- SCIENTIFICALLY_REVIEWED, AUTHORIZED_PUBLISHED: set by curation.
"""

PROPOSAL_STATES = (
    "REJECTED",
    "STRUCTURALLY_WELL_FORMED",
    "SOURCE_SUPPORTED",
    "PROPOSED_ONTOLOGY_EXTENSION",
    "SCIENTIFICALLY_REVIEWED",
    "AUTHORIZED_PUBLISHED",
)

# A reason that only says the approved vocabulary lacks a term, by kind of term.
VOCABULARY_REASONS = {
    "UNREGISTERED_CLASS_NEEDS_SEMANTIC_REVIEW": "class",
    "UNREGISTERED_INFORMATION_CLASS": "information_class",
    "UNREGISTERED_RELATION": "relation",
}


# Entailment is checked against the printed wording of approved relations only, so
# an unregistered relation always needs it reviewed; that review is the proposal's.
FOLLOWS_FROM_UNREGISTERED = {"UNREGISTERED_RELATION": {"RELATION_ENTAILMENT_REQUIRES_REVIEW"}}


def proposal_state(record):
    if record["status"] == "REJECTED":
        return "REJECTED"
    if record["status"] == "SOURCE_SUPPORTED":
        return "SOURCE_SUPPORTED"
    reasons = set(record.get("reasons") or [])
    for reason, follows in FOLLOWS_FROM_UNREGISTERED.items():
        if reason in reasons:
            reasons -= follows
    if reasons and reasons <= set(VOCABULARY_REASONS):
        return "PROPOSED_ONTOLOGY_EXTENSION"
    return "STRUCTURALLY_WELL_FORMED"


IDENTIFIER = r"[A-Za-z][A-Za-z0-9]*"


def structural_validation(proposal, approved):
    """Whether a staged vocabulary proposal is well formed, checked apart from the baseline.

    ``approved`` maps each kind to the approved terms of that kind. Placement in the
    hierarchy is a scientific decision, so a class without an established parent is
    well formed but marked as needing placement.
    """
    import re

    errors = []
    term = proposal.get("term") or ""
    if not re.fullmatch(IDENTIFIER, term):
        errors.append("TERM_IS_NOT_AN_IDENTIFIER")
    known = {t.lower(): t for t in approved.get(proposal.get("kind"), ())}
    if term.lower() in known:
        errors.append(
            "TERM_ALREADY_APPROVED"
            if known[term.lower()] == term
            else "TERM_DIFFERS_FROM_AN_APPROVED_TERM_ONLY_BY_CASE"
        )
    evidence = proposal.get("evidence") or []
    if not evidence or not all(e.get("evidence_id") and e.get("quote") for e in evidence):
        errors.append("EVIDENCE_ANCHORS_MISSING")
    if proposal.get("kind") == "relation" and not (
        proposal.get("domain") and proposal.get("range")
    ):
        errors.append("RELATION_DOMAIN_OR_RANGE_UNKNOWN")
    if proposal.get("activation") != "NONE":
        errors.append("EXTENSION_ACTIVATED_OUTSIDE_REVIEW")
    if proposal.get("definition") not in {None, "NOT_ESTABLISHED_BY_SOURCE"} and not proposal.get(
        "definition_evidence"
    ):
        errors.append("DEFINITION_WITHOUT_SOURCE_EVIDENCE")
    return {
        "well_formed": not errors,
        "errors": errors,
        "placement": "PARENT_NOT_ESTABLISHED_REQUIRES_REVIEW"
        if proposal.get("kind") != "relation" and not proposal.get("parent")
        else "PARENT_PROPOSED",
    }


def vocabulary_extension_proposals(records, entity_classes, approved=None):
    """One staged proposal per missing term, with the evidence of every record that uses it.

    The proposal names the term, its documentary instances and, for a relation, the
    classes it was used between. It never supplies a definition the source does not
    print; scientific review decides placement and meaning.
    """
    proposals = {}
    for record in records:
        if record.get("proposal_state") != "PROPOSED_ONTOLOGY_EXTENSION" or record.get(
            "duplicate_of"
        ):
            continue
        item = record["proposal"]
        for reason in record["reasons"]:
            kind = VOCABULARY_REASONS.get(reason)
            if kind is None:
                continue
            term = item["relation"] if kind == "relation" else item["class_id"]
            proposal = proposals.setdefault(
                (kind, term),
                {
                    "id": f"{kind}-proposal-{term}",
                    "kind": kind,
                    "term": term,
                    "definition": "NOT_ESTABLISHED_BY_SOURCE",
                    "instances": [],
                    "supporting_records": [],
                    "evidence": [],
                    "activation": "NONE",
                    "status": "STAGED_FOR_ONTOLOGY_REVIEW",
                    "proposal_state": "PROPOSED_ONTOLOGY_EXTENSION",
                    **({"domain": [], "range": []} if kind == "relation" else {}),
                },
            )
            proposal["supporting_records"].append(record["id"])
            label = item.get("label") or item.get("text") or ""
            if label and kind != "relation" and label not in proposal["instances"]:
                proposal["instances"].append(" ".join(label.split())[:160])
            if kind == "relation":
                for side, key in (("domain", "subject"), ("range", "object")):
                    cls = entity_classes.get(record.get(key))
                    if cls and cls not in proposal[side]:
                        proposal[side].append(cls)
            for span in record.get("support_spans") or []:
                anchor = {k: span[k] for k in ("evidence_id", "start", "end", "quote") if k in span}
                if anchor not in proposal["evidence"]:
                    proposal["evidence"].append(anchor)
    for proposal in proposals.values():
        for key in ("instances", "domain", "range"):
            if key in proposal:
                proposal[key].sort()
        proposal["structural_validation"] = structural_validation(proposal, approved or {})
    return [proposals[k] for k in sorted(proposals)]
