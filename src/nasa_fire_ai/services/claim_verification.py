"""Conservative claim support states; similarity and model scores prove no science."""

from nasa_fire_ai.services.scientific_synthesis import validate_selected_claim


def verify_claim(claim, bundle, registry):
    missing = [eid for eid in claim.evidence_ids if registry.resolve(eid) is None]
    if missing:
        return {
            "claim_id": claim.claim_id,
            "status": "INSUFFICIENT_EVIDENCE",
            "errors": ["Unresolvable evidence references"],
            "missing_evidence_ids": missing,
        }
    errors = validate_selected_claim(claim, bundle)
    if errors:
        return {
            "claim_id": claim.claim_id,
            "status": "UNSUPPORTED",
            "errors": errors,
            "fallback": "Remove proposed wording; use verified supplied statements",
        }
    limitations = list(claim.scope_limits)
    if claim.relationship_status != "DIRECT":
        limitations.append("Experimental applicability is not established as DIRECT")
    return {
        "claim_id": claim.claim_id,
        "status": "SUPPORTED_WITH_LIMITATIONS" if limitations else "SUPPORTED",
        "evidence_ids": claim.evidence_ids,
        "epistemic_type": claim.epistemic_type,
        "scientific_entities": claim.scientific_entities,
        "support_spans": claim.support_spans,
        "graph_paths": claim.graph_paths,
        "experimental_context": claim.experimental_context,
        "limitations": limitations,
        "boundary": "Exact supplied source statement; independent scientific correctness remains unmeasured",
    }
