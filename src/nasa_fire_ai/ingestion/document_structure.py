"""Deterministic, reversible document windows over immutable curation evidence."""

import hashlib
import re
from pathlib import Path

from nasa_fire_ai.ingestion.pdf import extract_pdf_tables

VERSION = "scientific-document-structure-v1"
HEADING = re.compile(
    r"(?m)^(?:#{1,6}\s+[^\n]+|(?:\d+(?:\.\d+)*[.)]?\s+)?"
    r"(?:abstract|introduction|background|experimental(?:\s+\w+){0,3}|"
    r"methods|outcomes?|findings|results(?:\s+and\s+discussion)?|discussion|conclusions?|"
    r"summary(?:\s+and\s+conclusions)?|references|acknowledg\w*|appendix[^\n]*))\s*$",
    re.IGNORECASE,
)


def identity(value):
    import json

    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()


def layout_headings(package, root):
    """Candidate scope labels from original PDF typography, never scientific claims.

    Prominent top-of-page lines are retained at their original text offsets. The
    physical location matters when a PDF writes a slide title after its body text.
    """
    import pymupdf

    result = {}
    for manifest in package["inputs"]:
        path = Path(root) / manifest["stored_input"]
        if path.suffix != ".pdf" or not path.is_file():
            continue
        with pymupdf.open(path) as pdf:
            for index, page in enumerate(pdf):
                evidence = next(
                    (
                        e
                        for e in package["evidence"]
                        if e["checksum"] == manifest["sha256"] and e["page"] == index + 1
                    ),
                    None,
                )
                if not evidence:
                    continue
                lines = [
                    line
                    for block in page.get_text("dict")["blocks"]
                    for line in block.get("lines", [])
                ]
                sizes = [
                    span["size"]
                    for line in lines
                    for span in line["spans"]
                    for _ in range(max(1, len(span["text"].strip())))
                ]
                if not sizes:
                    continue
                body = sorted(sizes)[len(sizes) // 5]
                for line in lines:
                    text = "".join(span["text"] for span in line["spans"]).strip()
                    font = max(span["size"] for span in line["spans"])
                    start = evidence["text"].find(text)
                    if (
                        line["bbox"][1] > page.rect.height * 0.25
                        or font < body * 1.2
                        or not 3 <= len(text) <= 160
                        or not re.search(r"[A-Za-z]", text)
                        or text.endswith((".", ";", ","))
                        or start < 0
                    ):
                        continue
                    candidate = {
                        "evidence_id": evidence["evidence_id"],
                        "source_id": evidence["source_id"],
                        "start": start,
                        "end": start + len(text),
                        "quote": text,
                        "font_size": font,
                        "bbox": list(line["bbox"]),
                        "basis": "PROMINENT_ORIGINAL_PDF_LAYOUT_NOT_SCIENTIFIC_ENTAILMENT",
                    }
                    if (
                        evidence["evidence_id"] not in result
                        or font > result[evidence["evidence_id"]]["font_size"]
                    ):
                        result[evidence["evidence_id"]] = candidate
    return result


def structure(package, root, max_chars=6500):
    """Partition every character; headings carry across pages of the same document.

    Context anchors remain literal spans, never asserted experimental conditions.
    PDF image contents are deliberately unread; detected cells retain coordinates.
    """
    if max_chars < 1000:
        raise ValueError("Document window must retain at least 1000 characters of context")
    sections, segments, anchors, tables, limitations = [], [], [], [], []
    current = {}
    layout = layout_headings(package, root)
    for evidence in package["evidence"]:
        eid, sid, text = evidence["evidence_id"], evidence["source_id"], evidence["text"]
        transitions = list(HEADING.finditer(text))
        sections.extend(
            {"evidence_id": eid, "start": m.start(), "end": m.end(), "title": m.group().strip()}
            for m in transitions
        )
        start = 0
        while start < len(text):
            end = min(start + max_chars, len(text))
            upcoming = [m.start() for m in transitions if start < m.start() < end]
            if upcoming:
                end = upcoming[0]
            if end < len(text):
                breaks = [m.end() for m in re.finditer(r"\n\s*\n|[.!?]\s+", text[start:end])]
                if breaks and breaks[-1] > max_chars // 2:
                    end = start + breaks[-1]
            relevant = [m for m in transitions if m.start() <= start]
            if relevant:
                current[sid] = relevant[-1].group().strip()
            section = layout[eid]["quote"] if eid in layout else current.get(sid, "UNSPECIFIED")
            segment = {
                "id": "segment-" + identity([eid, start, end, VERSION])[:24],
                "evidence_id": eid,
                "source_id": sid,
                "page": evidence["page"],
                "start": start,
                "end": end,
                "section": section,
                "layout_heading": layout.get(eid),
                "text": text[start:end],
                "section_transitions": [
                    s for s in sections if s["evidence_id"] == eid and start <= s["start"] < end
                ],
            }
            segments.append(segment)
            # Bounded source retrieval for distributed methods and definitions.
            for m in re.finditer(r"[^\n]+(?:\n(?!\n)[^\n]+)*", segment["text"]):
                quote = m.group()
                if len(quote) <= 2400 and re.search(
                    r"\b(?:tests?\s+(?:were|was)|experiments?\s+(?:were|was)|"
                    r"performed\s+(?:in|on|at)|conducted\s+(?:in|on|at)|"
                    r"all\s+(?:tests|experiments)|sample\s+(?:was|is)|"
                    r"except|denoted|designated|referred\s+to\s+as)\b",
                    quote,
                    re.IGNORECASE,
                ):
                    # Do not truncate into an invented sentence.
                    anchors.append(
                        {
                            "evidence_id": eid,
                            "source_id": sid,
                            "start": start + m.start(),
                            "end": start + m.end(),
                            "quote": quote,
                            "section": section,
                        }
                    )
            if transitions:
                before_end = [m for m in transitions if m.start() < end]
                if before_end:
                    current[sid] = before_end[-1].group().strip()
            start = end
    for manifest in package["inputs"]:
        path = Path(root) / manifest["stored_input"]
        if path.suffix == ".pdf":
            try:
                import pymupdf

                tables.extend(
                    {"input_sha256": manifest["sha256"], **t} for t in extract_pdf_tables(path)
                )
                with pymupdf.open(path) as doc:
                    for i, page in enumerate(doc):
                        if page.get_images() or not page.get_text().strip():
                            limitations.append(
                                {
                                    "input_sha256": manifest["sha256"],
                                    "page": i + 1,
                                    "kind": "IMAGE_CONTENT_NOT_INTERPRETED",
                                    "reason": "Text and detected table cells only; no OCR or figure interpretation",
                                }
                            )
            except (RuntimeError, ValueError) as error:
                limitations.append(
                    {
                        "input_sha256": manifest["sha256"],
                        "kind": "TABLE_LAYOUT_FAILURE",
                        "error_type": type(error).__name__,
                    }
                )
        elif path.suffix in {".md", ".txt", ".json"}:
            for evidence in package["evidence"]:
                if evidence["checksum"] != manifest["sha256"]:
                    continue
                for m in re.finditer(
                    r"(?m)^\|[^\n]+\|\s*\n\|[ :|\-]+\|\s*\n(?:\|[^\n]+\|\s*\n?)+", evidence["text"]
                ):
                    tables.append(
                        {
                            "evidence_id": evidence["evidence_id"],
                            "start": m.start(),
                            "end": m.end(),
                            "text": m.group(),
                            "publication_status": "REVIEW_REQUIRED",
                        }
                    )
    return {
        "version": VERSION,
        "sections": sections,
        "layout_headings": layout,
        "segments": segments,
        "context_anchors": anchors,
        "detected_tables": tables,
        "limitations": limitations,
        "coverage": {
            "source_characters": sum(len(e["text"]) for e in package["evidence"]),
            "segmented_characters": sum(s["end"] - s["start"] for s in segments),
            "units": len(package["evidence"]),
            "segments": len(segments),
        },
    }


def context_for(segment, document, max_chars=3500):
    """Retrieve same-document context; local exceptions are passed separately.

    Source locations and selected/unselected counts make bounded retrieval visible.
    No keyword occurrence grants universal applicability.
    """
    anchors = [a for a in document["context_anchors"] if a["source_id"] == segment["source_id"]]
    terms = set(re.findall(r"\w{4,}", segment["text"].lower()))
    anchors.sort(
        key=lambda a: (
            -len(terms & set(re.findall(r"\w{4,}", a["quote"].lower()))),
            a["evidence_id"],
            a["start"],
        )
    )
    selected, size = [], 0
    for anchor in anchors:
        if (
            anchor["evidence_id"] == segment["evidence_id"]
            and segment["start"] <= anchor["start"] < segment["end"]
        ):
            continue
        if size + len(anchor["quote"]) <= max_chars:
            selected.append(anchor)
            size += len(anchor["quote"])
    return {"anchors": selected, "available": len(anchors), "selected_characters": size}


def table_records(document):
    """Retain heterogeneous detected cells as reviewable records with physical identity.

    Empty/merged columns keep their original positions. A header, caption or row
    does not establish that an experiment ran. Multilevel headers stay explicit.
    """
    records = []
    for index, table in enumerate(document["detected_tables"]):
        if "cells" not in table:
            records.append(
                {
                    "id": "table-" + identity(table)[:20],
                    "kind": "TEXT_TABLE",
                    "source": table,
                    "status": "SEMANTIC_REVIEW_REQUIRED",
                }
            )
            continue
        cells = table["cells"]
        headers = table["header"]
        rows = cells if table["header_external"] else cells[1:]
        for row_index, row in enumerate(rows):
            records.append(
                {
                    "id": "table-record-"
                    + identity(
                        [table["input_sha256"], table["physical_pdf_page"], index, row_index]
                    )[:20],
                    "kind": "STRUCTURED_TABLE_RECORD",
                    "input_sha256": table["input_sha256"],
                    "page": table["physical_pdf_page"],
                    "table_index": index,
                    "row_index": row_index + 1,
                    "table_bbox": table["bbox"],
                    "original_headers": headers,
                    "cells": [
                        {
                            "column_index": i,
                            "header": headers[i] if i < len(headers) else None,
                            "original_value": value,
                        }
                        for i, value in enumerate(row)
                    ],
                    "status": "SEMANTIC_REVIEW_REQUIRED",
                    "limitation": "Merged cells and multirow headers are retained; header roles and row experiment identity require source-supported interpretation",
                    "scientific_execution_asserted": False,
                }
            )
    return records


def model_windows(document, max_chars):
    """Pack consecutive structural units; every member keeps its original locator.

    Small PDF pages can share a bounded call. Documents never share a window.
    Structural segments remain the independent deterministic coverage/checkpoint units.
    """
    windows = []
    members = []
    size = 0
    for segment in document["segments"]:
        if re.search(r"references|acknowledg", segment["section"], re.IGNORECASE):
            continue
        if members and (
            members[0]["source_id"] != segment["source_id"]
            or size + len(segment["text"]) > max_chars
            or (segment.get("layout_heading") and members[-1]["section"] != segment["section"])
        ):
            windows.append(
                {
                    "id": "window-" + identity([s["id"] for s in members])[:24],
                    "source_id": members[0]["source_id"],
                    "members": members,
                }
            )
            members = []
            size = 0
        members.append(segment)
        size += len(segment["text"])
    if members:
        windows.append(
            {
                "id": "window-" + identity([s["id"] for s in members])[:24],
                "source_id": members[0]["source_id"],
                "members": members,
            }
        )
    return windows
