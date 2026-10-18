"""Cited-study attribution printed near a passage, from the document's own references.

A results section can still describe someone else's work ("The data presented by
Chou and Giedorowicz ... Their data indicates ..."). These checks only read the
document: the authors listed in its own reference list, and explicit
third-party wording in the passage or in the sentence right before it.
"""

import re

THIRD_PARTY = re.compile(
    r"\btheir\s+(?:data|results?|work|stud(?:y|ies)|research|tests?|testing|findings|values?|experiments?|measurements?)\b"
    r"|\bthey\s+(?:found|reported|observed|showed|tested|measured|concluded|determined|examined)\b"
    r"|\bet\s+al\b",
    re.IGNORECASE,
)
CITATION = re.compile(r"\[\d+(?:\s*[,–-]\s*\d+)*\]")


def _evidence_text(document, evidence_id):
    return "".join(
        s.get("text", "") for s in document.get("segments", []) if s["evidence_id"] == evidence_id
    )


def reference_authors(document):
    """Surnames printed as authors in the document's own reference list."""
    sections = [
        s
        for s in document.get("sections", [])
        if re.search(r"(?:^|\n)\s*references\s*$", s.get("title", ""), re.IGNORECASE)
    ]
    if not sections:
        return set()
    heading = sections[-1]
    order = list(dict.fromkeys(s["evidence_id"] for s in document.get("segments", [])))
    if heading["evidence_id"] not in order:
        return set()
    text = "".join(
        _evidence_text(document, evidence_id)
        for evidence_id in order[order.index(heading["evidence_id"]) :]
    )[heading["end"] :]
    names = set()
    for entry in re.split(r"(?m)^\s*\[\d+\]", text)[1:]:
        authors = re.split(r"[“\"]", entry, maxsplit=1)[0]
        names.update(re.findall(r"\b([A-Z][a-zA-Z'’-]{2,}),\s*(?:[A-Z]\.\s*)+", authors))
        names.update(re.findall(r"(?:\b[A-Z]\.\s*)+([A-Z][a-zA-Z'’-]{2,})\b", authors))
    return names


def _names(text, authors):
    return sorted(a for a in authors if re.search(rf"\b{re.escape(a)}\b", text))


def cited_attribution_nearby(spans, document):
    """Explicit attribution to cited work in a passage or the sentence before it.

    Returns the attributing text, or None. The sentence before counts only for a
    named reference author or a bracket citation, because a pronoun there may
    refer to anything.
    """
    authors = reference_authors(document)
    for span in spans:
        quote = span.get("quote", "")
        named = _names(quote, authors)
        third_party = THIRD_PARTY.search(quote)
        if named or third_party:
            return {
                "basis": "PASSAGE_ATTRIBUTES_CITED_WORK",
                "quote": quote,
                "reference_authors": named,
                "wording": third_party.group() if third_party else None,
            }
        text = _evidence_text(document, span["evidence_id"])
        start = span.get("start")
        if start is None or start > len(text):
            continue
        prefix = text[:start].rstrip()
        sentences = re.split(r"(?<=[.!?])\s+", prefix) if prefix else []
        # When the passage starts mid-sentence the last piece is that sentence's
        # beginning; the sentence before it is then the one checked.
        nearby = (
            sentences[-2:] if sentences and not re.search(r"[.!?]$", prefix) else sentences[-1:]
        )
        for sentence in nearby:
            named = _names(sentence, authors)
            # "The data is presented in Table 4 [3]. The results show ..."
            if named or CITATION.search(sentence):
                return {
                    "basis": "PRECEDING_SENTENCE_ATTRIBUTES_CITED_WORK",
                    "quote": sentence.strip(),
                    "reference_authors": named,
                }
    return None


def cited_tables(document):
    """Numbers of tables whose own printed caption cites a reference ("[4]")."""
    numbers = set()
    for segment in document.get("segments", []):
        for caption in re.finditer(
            r"(?m)^[ \t]*(?:TABLE|Table)[ \t]+(\d+)[ \t]*[—–:.|-][^\n]*", segment.get("text", "")
        ):
            if CITATION.search(caption.group()):
                numbers.add(caption.group(1))
    return numbers


def cited_table_reference(spans, document):
    """A passage, or the sentence before it, that reads data from a cited table.

    "The data listed in Table 6 indicate ... The reactivity of the same material
    increases ..." reports a cited table, not an observation of the current
    study, even without an author name nearby.
    """
    numbers = cited_tables(document)
    if not numbers:
        return None
    pattern = re.compile(r"\bTables?\s+(\d+)(?:\s*(?:,|and|&)\s*(\d+))?", re.IGNORECASE)
    for span in spans:
        text = _evidence_text(document, span["evidence_id"])
        start = span.get("start")
        prefix = text[:start].rstrip() if start is not None and start <= len(text) else ""
        sentences = re.split(r"(?<=[.!?])\s+", prefix) if prefix else []
        nearby = (
            sentences[-2:] if sentences and not re.search(r"[.!?]$", prefix) else sentences[-1:]
        )
        for passage in [span.get("quote", ""), *nearby]:
            for match in pattern.finditer(passage):
                cited = {n for n in match.groups() if n} & numbers
                if cited:
                    return {
                        "basis": "PASSAGE_READS_A_CITED_TABLE",
                        "quote": passage.strip(),
                        "cited_tables": sorted(cited),
                    }
    return None
