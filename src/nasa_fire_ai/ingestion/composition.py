"""Material composition read from a document's own wording, staged for review.

A source can say that one material is made of others: "The composition of X is
40% A and 60% B", "X is made up of 90% A, 8% B, and 2% C", "X uses A filler in
B", "A-filled B", "the percentage of A in X is not known". This module reads
those statements generically, from wording and nothing else, and stages each
as a component assertion:

* a candidate ``hasComponent`` relation (Material to Material), which the
  approved ontology does not define (``madeOf`` relates a sample or a run to
  its material, not a material to its constituents);
* the component's documented role (``filler``) as a characteristic of that one
  assertion, never as a global property;
* its documented proportion, with the basis (mass, volume, molar) only when the
  source states it, and a documented unknown kept as unknown.

Nothing here is published to the ontology, the baseline or the graph. Every
assertion carries its literal source sentence and starts as
``SOURCE_SUPPORTED_PENDING_REVIEW``; ``VALIDATED`` and ``APPROVED`` are set only
by a scientist. Explanations are rendered from the structured assertions, so a
sentence can never say more than the record it was built from.
"""

import hashlib
import json
import re

LIFECYCLE = ("PROPOSED", "SOURCE_SUPPORTED_PENDING_REVIEW", "VALIDATED", "APPROVED")
NAME = r"[A-Z][\w®™.+-]*(?:\s+(?:[A-Z][\w®™.+-]*|\d+[\w®™-]*))*|[a-z][a-z-]{2,}"
ITEM = re.compile(rf"(?P<value>\d+(?:\.\d+)?)\s*%\s*(?:of\s+)?(?P<name>{NAME})")
BASIS = (
    (
        re.compile(
            r"\b(?:by\s+(?:weight|mass)|wt\.?\s*%|weight\s+(?:percent|fraction)|mass\s+fraction)",
            re.IGNORECASE,
        ),
        "MASS",
    ),
    (
        re.compile(r"\b(?:by\s+volume|vol\.?\s*%|volume\s+(?:percent|fraction))", re.IGNORECASE),
        "VOLUME",
    ),
    (re.compile(r"\b(?:mol(?:e|ar)?\s*%|mole\s+fraction)", re.IGNORECASE), "MOLAR"),
)
LIST = re.compile(
    r"(?:the\s+)?composition\s+of\s+(?P<subject>.+?)\s+(?:is|was)\s+(?P<items>.+)"
    r"|(?P<subject2>.+?)\s+(?:is|are|was|were)\s+(?:made\s+up|composed|comprised|formed)\s+of\s+(?P<items2>.+)"
    r"|(?P<subject3>.+?)\s+consists?\s+of\s+(?P<items3>.+)",
    re.IGNORECASE,
)
COMPONENT_OF = re.compile(
    rf"^(?:the\s+)?(?P<component>{NAME})\s+component\s+of\s+(?P<parent>.+)$", re.IGNORECASE
)
FILLER_IN = re.compile(
    rf"(?P<subject>{NAME})\s+(?:uses|contains|incorporates)\s+(?:a\s+)?(?P<component>{NAME})\s+fillers?\s+in\s+(?P<host>{NAME})",
)
WITH_FILLER = re.compile(
    rf"(?:formulation|compound|grade|version)\s+of\s+(?P<host>[^.,;]+?)\s+with\s+(?P<component>{NAME})\s+fillers?\b",
    re.IGNORECASE,
)
FILLED_NAME = re.compile(r"(?<![\w-])(?P<component>[A-Z][\w®™]*)-filled\s+(?P<host>[A-Z][\w®™()]*)")
UNKNOWN = re.compile(
    rf"(?:percentage|fraction|proportion|amount)\s+of\s+(?P<component>{NAME})\s+in\s+(?:the\s+)?(?P<subject>[^.,;]+?)\s+is\s+(?:not\s+known|unknown|not\s+reported)",
    re.IGNORECASE,
)
DESCRIPTOR = re.compile(
    r"\b(?:an?\s+)?(?:similar\s+|new\s+)?(?P<descriptor>[\w\s-]{0,40}?\b(?:compound|composite|blend|mixture|formulation|alloy))\s+(?:named|called)\s+(?P<name>[^.,;]+)",
    re.IGNORECASE,
)


def _norm(text):
    return re.sub(r"\s+", " ", (text or "").replace("­", "")).strip()


def _name(text):
    """A printed name without the sentence punctuation that follows it."""
    return re.sub(r"[.,;:]+$", "", _norm(text))


def _key(text):
    return re.sub(r"[^a-z0-9%]+", "", _norm(text).lower())


def _sentences(text):
    joined = re.sub(r"(?<=\w)-\s*\n\s*(?=\w)", "-", text)
    starts = [0] + [m.end() for m in re.finditer(r"(?<!\b[A-Z])[.!?](?=\s)", joined)]
    for begin, end in zip(starts, starts[1:] + [len(joined)]):
        sentence = joined[begin:end].strip()
        if sentence:
            yield sentence


def _basis(sentence):
    for pattern, basis in BASIS:
        if pattern.search(sentence):
            return basis
    return "UNSPECIFIED_IN_SOURCE"


def _entity(name, entities):
    """The supported entity a printed name refers to, if any."""
    key = _key(name)
    if not key:
        return None
    exact = [e for e in entities if _key(e["label"]) == key]
    if exact:
        return exact[0]
    # "Salox-M®." or "the Brass-filled PTFE samples" around a known name.
    contained = sorted(
        (
            e
            for e in entities
            if _key(e["label"]) and _key(e["label"]) in key and e["class_id"] == "Material"
        ),
        key=lambda e: -len(_key(e["label"])),
    )
    return contained[0] if contained else None


def _reference(name, entities):
    name = _name(name)
    entity = _entity(name, entities)
    if entity:
        return {"label": entity["label"], "entity_id": entity["id"], "class_id": entity["class_id"]}
    return {
        "label": _norm(name),
        "entity_id": None,
        "class_id": "Material",
        "entity_status": "STAGED_ENTITY_PROPOSAL",
    }


def _identity(*parts):
    return hashlib.sha256(
        json.dumps(parts, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()[:20]


def composition_assertions(evidence, entities):
    """Component assertions the document itself states, with their evidence.

    ``evidence`` is the package evidence list; ``entities`` are the validated,
    source-supported entities (``id``, ``label``, ``class_id``).
    """
    found = {}

    def add(
        subject,
        component,
        sentence,
        page_evidence,
        role=None,
        host=None,
        value=None,
        basis=None,
        proportion_status=None,
        context=None,
        descriptor=None,
        descriptors=None,
    ):
        subject_ref = _reference(subject, entities)
        component_ref = _reference(component, entities)
        # The subject is a material the document's validated record names, or
        # a component of one ("the Bronze component of X").
        if (
            not context
            and subject_ref["class_id"] != "Material"
            or (not context and subject_ref["entity_id"] is None)
        ):
            return
        if _key(subject_ref["label"]) == _key(component_ref["label"]):
            return
        key = (_key(subject_ref["label"]), _key(component_ref["label"]), _key(context or ""))
        record = found.setdefault(
            key,
            {
                "id": "composition-" + _identity(*key),
                "relation_candidate": "hasComponent",
                "subject": subject_ref,
                "component": component_ref,
                "context": context,
                "role": None,
                "role_host": None,
                "proportion": None,
                "source_descriptor": None,
                "evidence": [],
                "lifecycle": "SOURCE_SUPPORTED_PENDING_REVIEW",
                "activation": "NONE",
            },
        )
        if role and not record["role"]:
            record["role"] = role
            record["role_host"] = _reference(host, entities) if host else None
        if value is not None and not record["proportion"]:
            record["proportion"] = {
                "value": value,
                "unit": "%",
                "basis": basis,
                "status": "REPORTED",
            }
        if proportion_status and not record["proportion"]:
            record["proportion"] = {
                "value": None,
                "unit": None,
                "basis": None,
                "status": proportion_status,
            }
        descriptor = descriptor or next(
            (d for k, d in (descriptors or {}).items() if k.startswith(_key(subject_ref["label"]))),
            None,
        )
        if descriptor and not record["source_descriptor"]:
            record["source_descriptor"] = descriptor
        quote = {
            "evidence_id": page_evidence["evidence_id"],
            "page": page_evidence.get("page"),
            "quote": sentence,
        }
        if quote not in record["evidence"]:
            record["evidence"].append(quote)

    for page in evidence:
        for sentence in _sentences(page.get("text", "")):
            flat = _norm(sentence)
            descriptors = {
                _key(m["name"]): _norm(m["descriptor"]) for m in DESCRIPTOR.finditer(flat)
            }
            listed = LIST.search(flat)
            if listed:
                subject = listed["subject"] or listed["subject2"] or listed["subject3"]
                items = listed["items"] or listed["items2"] or listed["items3"]
                subject = subject.strip()
                context = None
                nested = COMPONENT_OF.match(subject)
                if nested:
                    # "The Bronze component of Salox-M® is made up of ...": the
                    # bronze of that formulation, not the substance in general.
                    context = _reference(nested["parent"], entities)["label"]
                    subject = nested["component"]
                parts = list(ITEM.finditer(items))
                if parts:
                    basis = _basis(flat)
                    for part in parts:
                        add(
                            subject,
                            part["name"],
                            flat,
                            page,
                            value=float(part["value"]),
                            basis=basis,
                            context=context,
                            descriptors=descriptors,
                        )
            for m in FILLER_IN.finditer(flat):
                add(
                    m["subject"],
                    m["component"],
                    flat,
                    page,
                    role="filler",
                    host=m["host"],
                    descriptors=descriptors,
                )
                add(m["subject"], m["host"], flat, page, descriptors=descriptors)
            for m in WITH_FILLER.finditer(flat):
                host = re.sub(r"\s*\([^()]*\)\s*$", "", m["host"]).strip()
                named = [
                    e
                    for e in entities
                    if e["class_id"] == "Material"
                    and re.fullmatch(
                        rf"{re.escape(m['component'])}-filled\s+.+", e["label"], re.IGNORECASE
                    )
                ]
                for subject in named:
                    add(subject["label"], m["component"], flat, page, role="filler", host=host)
            for m in UNKNOWN.finditer(flat):
                add(
                    m["subject"],
                    m["component"],
                    flat,
                    page,
                    proportion_status="NOT_KNOWN_PER_SOURCE",
                )
    # A material whose printed name is "A-filled B" names A as its filler in B.
    for e in entities:
        m = FILLED_NAME.fullmatch(_norm(e["label"])) if e["class_id"] == "Material" else None
        if not m:
            continue
        for page in evidence:
            for sentence in _sentences(page.get("text", "")):
                # A sentence of the text, not a title block or a table run.
                if _key(e["label"]) in _key(sentence) and len(_norm(sentence)) <= 300:
                    add(
                        e["label"],
                        m["component"],
                        _norm(sentence),
                        page,
                        role="filler",
                        host=m["host"],
                    )
                    add(e["label"], m["host"], _norm(sentence), page)
                    break
            else:
                continue
            break
    assertions = sorted(found.values(), key=lambda r: r["id"])
    by_subject = {}
    for record in assertions:
        by_subject.setdefault(
            (_key(record["subject"]["label"]), _key(record["context"] or "")), []
        ).append(record)
    for group in by_subject.values():
        values = [
            r["proportion"]["value"]
            for r in group
            if r["proportion"] and r["proportion"]["value"] is not None
        ]
        for record in group:
            if record["proportion"] and record["proportion"]["value"] is not None:
                # Recorded, never inferred from: the source's own figures.
                record["proportion"]["listed_components_sum"] = round(sum(values), 6)
    return assertions


def ontology_extension_proposals(assertions, semantic_relations):
    """The vocabulary the staged assertions would need, for ontology review."""
    if not assertions or "hasComponent" in semantic_relations:
        return []
    return [
        {
            "id": "relation-proposal-hasComponent",
            "kind": "relation",
            "term": "hasComponent",
            "domain": "Material",
            "range": "Material",
            "definition": "The subject material contains the object material as a constituent, as the source states.",
            "assertion_characteristics": {
                "role": "The component's documented function in this material (e.g. filler); a characteristic of one assertion, not a global property.",
                "proportion": "The documented share of the component, with its documented basis (mass, volume, molar) or UNSPECIFIED_IN_SOURCE.",
                "context": "The material in which a nested component is described (the bronze of one formulation).",
            },
            "approved_relations_examined": sorted(semantic_relations),
            "why_existing_relations_do_not_fit": "madeOf relates a sample, run or experiment family to its material; no approved relation links a material to its constituents.",
            "supporting_assertions": [a["id"] for a in assertions],
            "activation": "NONE",
            "status": "STAGED_FOR_ONTOLOGY_REVIEW",
        }
    ]


def _number(value):
    return f"{value:g}"


def explain(assertion):
    """Natural-language sentences rendered only from one structured assertion."""
    subject = assertion["subject"]["label"]
    component = assertion["component"]["label"]
    where = f" (as used in {assertion['context']})" if assertion.get("context") else ""
    lines = []
    if assertion.get("source_descriptor"):
        lines.append(f"The source describes {subject} as a {assertion['source_descriptor']}.")
    lines.append(f"{subject}{where} contains {component} as a component.")
    if assertion.get("role"):
        host = assertion.get("role_host")
        lines.append(
            f"{component} acts as the {assertion['role']} of {subject}"
            + (f", in {host['label']}" if host and host["label"] != subject else "")
            + "."
        )
    proportion = assertion.get("proportion")
    if proportion and proportion["status"] == "REPORTED":
        basis = {
            "MASS": "by mass",
            "VOLUME": "by volume",
            "MOLAR": "on a molar basis",
        }.get(proportion["basis"], "on a basis the source does not state")
        lines.append(
            f"The reported share of {component} in {subject}{where} is {_number(proportion['value'])}% {basis}."
        )
    elif proportion and proportion["status"] == "NOT_KNOWN_PER_SOURCE":
        lines.append(f"The source states that the share of {component} in {subject} is not known.")
    pages = sorted({e["page"] for e in assertion["evidence"] if e.get("page") is not None})
    lines.append(
        f"Status: {assertion['lifecycle']}; relation hasComponent is a staged proposal, not approved vocabulary"
        + (f"; source page {', '.join(str(p) for p in pages)}." if pages else ".")
    )
    return lines
