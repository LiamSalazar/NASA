"""Original logical sections and documentary scope certificates, never global aliases."""

import re

from nasa_fire_ai.ingestion.source_spans import normalized_with_offsets, recover_span


def norm(text):
    return normalized_with_offsets(text)[0].lower().strip()


def contains(label, text):
    return bool(re.search(r"(?<![\w-])" + re.escape(norm(label)) + r"(?![\w-])", norm(text)))


STANDARD_SECTION = re.compile(
    r"^(?:abstract|introduction|background|nomenclature|experimental(?:\s+(?:description|setup|methods|procedure))?|methods?|test\s+(?:configuration|objectives|results|methods?|procedure)|testing|results(?:\s+and\s+discussion)?|discussion|conclusions?|summary(?:\s+and\s+conclusions)?|references|acknowledg\w*)$",
    re.IGNORECASE,
)
ROMAN = re.compile(r"^[IVX]+[.)]\s+", re.IGNORECASE)


def logical_section(span, document):
    """A prominent title or numbered list does not override its parent section."""
    order = {
        key: i
        for i, key in enumerate(dict.fromkeys(s["evidence_id"] for s in document["segments"]))
    }
    segments = [s for s in document["segments"] if s["evidence_id"] == span["evidence_id"]]
    if not segments:
        return "UNSPECIFIED"
    sid = segments[0]["source_id"]
    headings = [h for h in document["sections"] if h.get("source_id") == sid]
    roman_mode = any(
        re.match(
            r"^(?:I[.)]\s+(?:Introduction|Background|Methods)|[IVX]{2,}[.)]\s+)",
            h["title"],
            re.IGNORECASE,
        )
        for h in headings
    )
    candidates = []
    for h in headings:
        # Strip only an outline number ("3", "2.1.") or a punctuated letter/roman
        # numeral ("A.", "IV)"); an unpunctuated first word ("Results") is the title.
        body = re.sub(
            r"^(?:#+\s*|\d+(?:\.\d+)*[.)]?\s+|[A-Z][.)]\s+|[IVXLCDM]+[.)]\s+)",
            "",
            h["title"],
            flags=re.IGNORECASE,
        ).strip()
        if norm(body) == norm(document.get("package_title", "")):
            continue
        # A major heading printed alone on its line may be followed directly by
        # its first subsection title ("Experimental" then "Test Apparatus").
        first_line = body.split("\n", 1)[0].strip()
        major = (
            bool(ROMAN.match(h["title"]))
            if roman_mode
            else bool(STANDARD_SECTION.fullmatch(body) or STANDARD_SECTION.fullmatch(first_line))
        )
        if re.fullmatch(r"references|acknowledg\w*|abstract|nomenclature", body, re.IGNORECASE):
            major = True
        if major and (order[h["evidence_id"]], h["start"]) <= (
            order[span["evidence_id"]],
            span["start"],
        ):
            candidates.append(h)
    if candidates:
        return max(candidates, key=lambda h: (order[h["evidence_id"]], h["start"]))["title"]
    return "UNSPECIFIED"


def figure_group_support(subject, spans, entities, document):
    entity = entities.get(subject, {})
    if (
        entity.get("class_id") != "ExperimentFamily"
        or entity.get("validation_status") != "SOURCE_SUPPORTED"
    ):
        return []
    if not re.search(
        r"\b(?:tests?|series|results?|comparison|experiments?|groups?)\b",
        entity["label"],
        re.IGNORECASE,
    ):
        return []
    proof = []
    for span in spans:
        if span["source_id"] != entity["source_id"]:
            return []
        if any(
            e.get("class_id") in {"ExperimentFamily", "ExperimentalRun"}
            and e.get("validation_status") == "SOURCE_SUPPORTED"
            and e.get("id") != entity.get("id")
            and contains(e["label"], span["quote"])
            for e in entities.values()
        ):
            return []
        refs = re.findall(r"\b(?:Figures?|Figs?\.?)\s+(\d+)\b", span["quote"], re.IGNORECASE)
        if not refs:
            return []
        for ref in refs:
            captions = [
                f
                for f in document.get("figures", [])
                if f["source_id"] == span["source_id"] and f["number"] == ref
            ]
            if len(captions) != 1:
                return []
            f = captions[0]
            # The name must start in the actual caption's first line, not in
            # neighboring prose accidentally included by layout extraction.
            first = f["quote"][: f["first_line_end"] - f["start"]]
            first_word = entity["label"].split()[0]
            if not contains(entity["label"], f["quote"]) or not contains(first_word, first):
                return []
            if re.search(
                r"\[\d|\b(?:reproduced|adapted|prior|previous)\b", f["quote"], re.IGNORECASE
            ):
                return []
            if any(
                e.get("class_id") == "ExperimentFamily"
                and e.get("validation_status") == "SOURCE_SUPPORTED"
                and e.get("id") != entity.get("id")
                and contains(e["label"], f["quote"])
                for e in entities.values()
            ):
                return []
            proof.append(
                {"evidence_id": f["evidence_id"], "quote": f["quote"], "start": f["start"]}
            )
    return list({(p["evidence_id"], p["start"]): p for p in proof}.values())


def test_article_alias_review(subject, spans, entities, document):
    """Preserve a unique source-defined test-article acronym for REVIEW only."""
    entity = entities.get(subject, {})
    if (
        entity.get("class_id") != "Sample"
        or entity.get("study") != "current"
        or entity.get("validation_status") != "SOURCE_SUPPORTED"
    ):
        return None
    literal = norm(entity["label"])
    identity = [
        s
        for s in entity.get("support", [])
        if re.search(
            r"(?:tested\s+(?:was|were)|test\s+article\s+(?:was|is))\s+(?:the\s+)?"
            + re.escape(literal),
            norm(s["quote"]),
        )
    ]
    if not identity:
        return None
    for alias in re.findall(r"\(([A-Z][A-Z0-9-]{1,9})\)", entity["label"]):
        if any(
            e.get("id") != entity.get("id")
            and e.get("class_id") == "Sample"
            and e.get("validation_status") == "SOURCE_SUPPORTED"
            and e.get("source_id") == entity["source_id"]
            and contains(alias, e["label"])
            for e in entities.values()
        ):
            continue
        versions = set(re.findall(r"\b\d+\.\d+\b", entity["label"]))
        valid = True
        for span in spans:
            section = logical_section(span, document)
            if span["source_id"] != entity["source_id"] or not contains(alias, span["quote"]):
                valid = False
                break
            if not re.search(
                r"\b(?:test|testing|experimental|configuration|methods?|disassembly|inspection|functional|conclusions?|results?)\b",
                section,
                re.IGNORECASE,
            ) or re.search(
                r"analysis|model|background|introduction|references", section, re.IGNORECASE
            ):
                valid = False
                break
            if any(
                v not in versions
                for v in re.findall(re.escape(alias) + r"\s*(\d+\.\d+)", span["quote"])
            ):
                valid = False
                break
            if any(
                e.get("class_id") == "Sample"
                and e.get("validation_status") == "SOURCE_SUPPORTED"
                and e.get("id") != entity.get("id")
                and contains(e["label"], span["quote"])
                for e in entities.values()
            ):
                valid = False
                break
        if valid:
            return {
                "basis": "UNIQUE_ORIGINAL_TEST_ARTICLE_ACRONYM_REQUIRES_SCOPE_REVIEW",
                "original_acronym": alias,
                "support": identity,
                "global_alias_activation": "NONE",
                "scientific_approval": "NONE",
            }
    return None


def page_continuation_context(spans, evidence):
    """A lower-case continuation after a page break is not a whole proposition."""
    pages = list(evidence.values())
    counts = {}
    for page in pages:
        for line in set(page["text"].splitlines()):
            if line.strip():
                counts[line.strip()] = counts.get(line.strip(), 0) + 1

    def body(page):
        lines = page["text"].splitlines(keepends=True)
        left = 0
        right = len(page["text"])
        while lines and (
            not lines[0].strip()
            or lines[0].strip() == str(page.get("page"))
            or counts.get(lines[0].strip(), 0) > 1
        ):
            left += len(lines.pop(0))
        while lines and (
            not lines[-1].strip()
            or lines[-1].strip() == str(page.get("page"))
            or counts.get(lines[-1].strip(), 0) > 1
        ):
            right -= len(lines.pop())
        return left, right, page["text"][left:right].strip()

    for span in spans:
        current = evidence[span["evidence_id"]]
        if current.get("page") is None:
            continue
        previous = [
            p
            for p in pages
            if p["source_id"] == current["source_id"] and p.get("page") == current["page"] - 1
        ]
        if len(previous) != 1:
            continue
        begin, _, text = body(current)
        prev = previous[0]
        _, end, tail = body(prev)
        if (
            text
            and text[0].islower()
            and tail
            and tail[-1] not in ".!?:"
            and span["start"] <= begin < span["end"]
        ):
            start = prev["text"].rfind("\n\n", 0, end) + 2
            if start == 1:
                start = 0
            return {
                "basis": "ORIGINAL_SENTENCE_CONTINUES_FROM_PREVIOUS_PDF_PAGE",
                "evidence_id": prev["evidence_id"],
                "start": start,
                "end": end,
                "quote": prev["text"][start:end],
            }
    return None


def consolidate_validated_variants(records, entities, evidence, document):
    """One active exact assertion; original inference variants remain auditable."""
    primary = {}
    for record in sorted(records, key=lambda r: r["id"]):
        if record["status"] == "REJECTED":
            continue
        item = record["proposal"]
        kind = record["kind"]
        key = None
        if kind == "statements":
            body = item["text"]
            for span in record["support_spans"]:
                heading = document.get("layout_headings", {}).get(span["evidence_id"])
                if (
                    heading
                    and body.startswith(heading["quote"])
                    and any(
                        norm(e["label"]) == norm(heading["quote"])
                        and e["id"] in record.get("scope", [])
                        for e in entities.values()
                    )
                ):
                    body = body[len(heading["quote"]) :].lstrip()
            positions = []
            for span in record["support_spans"]:
                try:
                    located = recover_span(evidence[span["evidence_id"]]["text"], body)
                except ValueError:
                    continue
                if span["start"] <= located["start"] and located["end"] <= span["end"]:
                    positions.append((span["evidence_id"], located["start"], located["end"]))
            if positions:
                key = (
                    kind,
                    record["status"],
                    norm(body),
                    item["epistemic"],
                    item["study"],
                    tuple(sorted(record.get("scope", []))),
                    tuple(sorted(set(positions))),
                    tuple(sorted(record["reasons"])),
                )
        elif (
            kind == "quantities"
            and item["epistemic"] == "experimental_configuration"
            and record.get("source_role") == "SPECIMEN_CHARACTERISTIC"
        ):
            subject = entities.get(item["subject"], {})
            if contains(item["expression"], subject.get("label", "")) and contains(
                item["unit"] or "", subject.get("label", "")
            ):
                key = (
                    kind,
                    record["status"],
                    record.get("subject"),
                    record.get("mapping", {}).get("source_accessor"),
                    item["expression"],
                    item["unit"],
                    tuple(sorted(record["reasons"])),
                )
        if (
            kind == "relations"
            and record["status"] == "SOURCE_SUPPORTED"
            and record.get("subject")
            and record.get("object")
        ):
            # One relation between the same two entities, proposed by the model
            # and by the printed structure, is one assertion.
            key = (kind, record["status"], record["subject"], item["relation"], record["object"])
        binding = record.get("table_row_binding") or {}
        if key is None and kind == "quantities" and binding.get("rows"):
            # One table cell bound through the same printed row(s), proposed by
            # the model and by the printed structure, is one assertion.
            key = (
                kind,
                record["status"],
                record.get("subject"),
                norm(item["label"]),
                item["expression"],
                item["unit"],
                item["epistemic"],
                tuple(
                    sorted(
                        (r.get("page"), r.get("row_index"), r.get("column_index"))
                        for r in binding["rows"]
                    )
                ),
                tuple(sorted(record["reasons"])),
            )
        if key is None and kind == "quantities" and record.get("quantity_value_spans"):
            # The same printed value, subject, name, unit and role proposed twice.
            key = (
                kind,
                record["status"],
                record.get("subject"),
                norm(item["label"]),
                item["expression"],
                item["unit"],
                item["epistemic"],
                tuple(
                    (v["evidence_id"], v["start"], v["end"]) for v in record["quantity_value_spans"]
                ),
                tuple(sorted(record["reasons"])),
            )
        if key is None:
            continue
        if key not in primary:
            primary[key] = record
            continue
        owner = primary[key]
        record["duplicate_of"] = owner["id"]
        record["active_proposal"] = False
        owner.setdefault("validated_variant_ids", []).append(record["id"])
        existing = {(s["evidence_id"], s["start"], s["end"]) for s in owner["support_spans"]}
        for span in record["support_spans"]:
            k = (span["evidence_id"], span["start"], span["end"])
            if k not in existing:
                owner["support_spans"].append(span)
                existing.add(k)
        owner["support_spans"].sort(key=lambda s: (s["evidence_id"], s["start"], s["end"]))
