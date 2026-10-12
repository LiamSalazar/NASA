"""Conservative claim support states; similarity and model scores prove no science."""

from nasa_fire_ai.services.scientific_synthesis import validate_selected_claim


def verify_claim(claim, bundle, registry, *, store=None):
    missing = [eid for eid in claim.evidence_ids if registry.resolve(eid) is None]
    if missing:
        return {
            "claim_id": claim.claim_id,
            "status": "INSUFFICIENT_EVIDENCE",
            "errors": ["Unresolvable evidence references"],
            "missing_evidence_ids": missing,
        }
    errors = validate_selected_claim(claim, bundle)
    if any(d.get("status") == "CONFLICTED" for d in claim.experimental_context):
        errors.append("Conflicted scientific scope cannot be emitted as supported")
    from nasa_fire_ai.services.scientific_synthesis import normalize

    for span in claim.support_spans:
        if span.get("reference_kind") == "supplied_structured_value" and store is not None:
            supplied = span.get("structured_record", {})
            trusted = store.payload(supplied.get("id", ""))
            if not trusted or any(
                supplied.get(key) != trusted.get(key)
                for key in ("id", "subject", "property_id", "value", "qualifiers")
            ):
                errors.append("Structured quantity differs from validated graph source projection")
        if span.get("reference_kind") == "exact_source_span":
            original = registry.resolve(span["evidence_id"])
            if not original or normalize(span.get("text", "")) not in normalize(
                original.get("text", "")
            ):
                errors.append("Supplied span differs from immutable registry source")
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
