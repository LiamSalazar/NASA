"""Review-only original PDF numeric cells; no scientific mapping or execution."""

import re

from nasa_fire_ai.ingestion.document_structure import identity, table_records


def original_table_unit(header, row):
    """Recognize literal unit syntax in either axis, without converting values."""
    prefix = r"(?:da|[yzafpnumµμcdhkMGTPEZY])?"
    base = r"(?:mol|kat|Hz|Pa|Wb|lm|lx|Bq|Gy|Sv|cd|m|g|s|A|K|N|J|W|C|V|F|Ω|S|T|H)"
    atom = rf"{prefix}{base}(?:\^?[-+]?\d+|[²³])?"
    syntax = rf"(?:{atom}(?:[/*· ]{atom})*|%|ppm|fraction|RPM|psia|Wh|Ah|Whr|Ahr|seconds?|minutes?|hours?)"
    label = row[0].get("original_value") if row else None
    candidates = []
    for axis, text in [("column", header), ("row", label or "")]:
        for match in re.finditer(r"\(([^()]+)\)", text):
            literal = match.group(1)
            candidates.append(
                {
                    "axis": axis,
                    "literal": literal,
                    "recognized_unit_syntax": bool(re.fullmatch(syntax, literal.strip())),
                }
            )
    units = {c["literal"] for c in candidates if c["recognized_unit_syntax"]}
    return (next(iter(units)) if len(units) == 1 else None), candidates


def pdf_table_quantities(package, document):
    from nasa_fire_ai.ingestion.document_extraction import quantity_expression_pattern

    result = []
    for row in table_records(document):
        if row["kind"] != "STRUCTURED_TABLE_RECORD":
            continue
        evidence = [
            e
            for e in package["evidence"]
            if e["checksum"] == row["input_sha256"] and e["page"] == row["page"]
        ]
        if len(evidence) != 1:
            continue
        e = evidence[0]
        role_cues = [
            {"quote": m.group(), "start": m.start(), "end": m.end()}
            for m in re.finditer(
                r"(?m)^[^\n]*(?:fits?|derived|derivative|calculated|estimated)[^\n]*$",
                e["text"],
                re.IGNORECASE,
            )
        ]
        for cell in row["cells"]:
            original = cell["original_value"]
            if not original or not re.fullmatch(quantity_expression_pattern(), original.strip()):
                continue
            header = cell.get("header") or ""
            unit, unit_candidates = original_table_unit(header, row["cells"])
            key = identity([row["id"], cell["column_index"], original, header])[:24]
            result.append(
                {
                    "id": "pdf-quantity-" + key,
                    "kind": "quantities",
                    "status": "UNRESOLVED",
                    "proposal": {
                        "expression": original,
                        "unit": unit,
                        "original_unit_candidates": unit_candidates,
                        "original_column_header": header,
                        "original_row": row["cells"],
                        "original_page_heading": document.get("layout_headings", {})
                        .get(e["evidence_id"], {})
                        .get("quote"),
                        "original_role_cues": role_cues,
                        "epistemic": "UNRESOLVED_REVIEW_REQUIRED",
                        "subject": "UNRESOLVED_ORIGINAL_TABLE_ROW_COLUMN_SCOPE",
                    },
                    "reasons": [
                        "ORIGINAL_TABLE_QUANTITY_ROLE_AND_EXPERIMENTAL_SCOPE_REQUIRE_REVIEW"
                    ],
                    "support_spans": [
                        {
                            "evidence_id": e["evidence_id"],
                            "source_id": e["source_id"],
                            "checksum": e["checksum"],
                            "page": e["page"],
                            "start": 0,
                            "end": len(e["text"]),
                            "quote": e["text"],
                            "locator": {
                                "page": e["page"],
                                "table_index": row["table_index"],
                                "table_bbox": row["table_bbox"],
                                "row_index": row["row_index"],
                                "column_index": cell["column_index"],
                            },
                        }
                    ],
                    "source_table_record_id": row["id"],
                    "scientific_execution_asserted": False,
                    "scientific_approval": "NONE",
                    "global_vocabulary_activation": "NONE",
                    "native_quantity_representation": "DEFERRED_PRESERVED_ORIGINAL_TABLE_LITERAL",
                }
            )
    return result
