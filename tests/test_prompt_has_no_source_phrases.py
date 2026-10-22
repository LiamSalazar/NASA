"""The text sent to the model shares no phrase with a frozen target quote; no source data."""

import glob
import json
import re

from nasa_fire_ai.ingestion.document_extraction import (
    PROTOCOL_SYSTEM,
    STAGE_INSTRUCTIONS,
    Output,
)

STOP = {
    "a",
    "an",
    "the",
    "of",
    "in",
    "on",
    "at",
    "to",
    "for",
    "by",
    "with",
    "and",
    "or",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "as",
    "from",
    "that",
    "this",
    "it",
    "its",
    "not",
    "no",
    "than",
    "then",
    "which",
    "each",
    "all",
    "any",
    "into",
    "per",
    "when",
}


def words(text):
    return re.findall(r"[a-z0-9]+(?:[.'][a-z0-9]+)*", text.lower())


def phrases(text):
    w = words(text)
    return {
        tuple(w[i : i + 3])
        for i in range(len(w) - 2)
        if sum(x not in STOP for x in w[i : i + 3]) >= 2
    }


def descriptions(node):
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "description" and isinstance(value, str):
                yield value
            else:
                yield from descriptions(value)
    elif isinstance(node, list):
        for value in node:
            yield from descriptions(value)


def test_no_prompt_or_schema_text_copies_a_frozen_target_quote():
    sent = [
        PROTOCOL_SYSTEM,
        *STAGE_INSTRUCTIONS.values(),
        *descriptions(Output.model_json_schema()),
    ]
    quotes = []
    for path in glob.glob("artifacts/phase1_generalizable_ingestion/v4/*/source_reference.json"):
        with open(path, encoding="utf-8") as handle:
            quotes += [t["quote"] for t in json.load(handle)["targets"]]
    assert quotes
    target_phrases = set().union(*(phrases(q) for q in quotes))
    shared = sorted({" ".join(p) for text in sent for p in phrases(text) & target_phrases})
    assert shared == []
