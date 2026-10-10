"""Class/authority/topic selection; lexical context never establishes scientific identity."""

import re


def words(text):
    return set(re.findall(r"[a-z0-9]+", str(text).lower()))


def select_information(intent, query, store, evidence_registry):
    metadata = store.registry.class_metadata
    requested = {
        c
        for c in intent.requested_information
        if metadata.get(c, {}).get("information") and not metadata[c].get("documentary")
    }
    policy = store.registry.selection_policy
    if not requested:
        return [], []
    administrative = set(policy.get("stop_words", []))
    for meta in metadata.values():
        for term in meta.get("query_terms", []):
            administrative.update(words(term))
    topics = words(query) - administrative
    for constraint in intent.entity_constraints:
        topics.update(words(constraint.entity_id))
    for operand in intent.comparison.operands if intent.comparison else []:
        topics.update(words(operand))
    contexts = {}
    candidates = []
    selected = []
    for subject in store.entities():
        classes = store.classes(subject)
        if not classes.intersection(requested):
            continue
        refs = store.evidence(subject)
        source_ok = not intent.source_constraints or bool(
            store.sources(subject).intersection(intent.source_constraints)
        )
        evidence_ok = bool(refs) and all(evidence_registry.resolve(e) is not None for e in refs)
        payload = store.payload(subject)
        text = " ".join(
            str(payload.get(k) or "")
            for k in (
                "text",
                "description",
                "normalized_text",
                "scope_applicability",
                "source_section",
            )
        )
        own = words(text)
        contextual = set()
        # Exact source/page links provide documentary context, not new KG facts.
        for eid in refs:
            p = evidence_registry.resolve(eid)
            if not p:
                continue
            key = (p["document_id"], p.get("page"))
            if key not in contexts:
                rows = evidence_registry.db.execute(
                    "SELECT text,section FROM passages WHERE document_id=? AND page IS ?", key
                ).fetchall()
                contexts[key] = words(
                    " ".join(str(r[0] or "") + " " + str(r[1] or "") for r in rows)
                )
            contextual.update(contexts[key])
        overlap = topics & (own | contextual)
        # Class-only queries have no topic filter. Topic queries need explicit
        # lexical/context overlap; no similarity-based scientific equivalence.
        topic_ok = not topics or bool(overlap)
        excluded = []
        if not source_ok:
            excluded.append("source_constraint")
        if not evidence_ok:
            excluded.append("missing_evidence")
        if not topic_ok:
            excluded.append("no_topic_overlap")
        if intent.clarification_required or intent.unresolved_mentions:
            excluded.append("unresolved_query")
        own_overlap = topics & own
        context_overlap = overlap - own
        score = 3 * len(own_overlap) + len(context_overlap)
        topic_coverage = len(overlap) / len(topics) if topics else 1.0
        candidates.append(
            {
                "subject": subject,
                "classes": sorted(classes),
                "authority": "CANONICAL_REVIEWED",
                "evidence_ids": refs,
                "evidence_sources": [
                    {
                        "evidence_id": eid,
                        "location": {
                            "page": (passage := evidence_registry.resolve(eid)).get("page"),
                            "section": passage.get("section"),
                        },
                        "source": evidence_registry.source_metadata(eid),
                    }
                    for eid in refs
                    if evidence_registry.resolve(eid)
                ],
                "topic_terms": sorted(topics),
                "own_overlap": sorted(own_overlap),
                "context_overlap": sorted(context_overlap),
                "score": score,
                "topic_coverage": topic_coverage,
                "excluded": excluded,
            }
        )
        if not excluded:
            selected.append((score, subject))
    selected.sort(key=lambda x: (-x[0], x[1]))
    selected_rank = {subject: rank for rank, (_, subject) in enumerate(selected, 1)}
    for candidate in candidates:
        candidate["ranking"] = selected_rank.get(candidate["subject"])
        candidate["eligible"] = candidate["ranking"] is not None
        candidate["eligibility_reason"] = (
            "reviewed_class_source_evidence_and_topic_scope_passed"
            if candidate["eligible"]
            else ";".join(candidate["excluded"])
        )
    return [s for _, s in selected], candidates
