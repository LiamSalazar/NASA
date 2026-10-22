"""Draft target finders for ignition, regulator and textiles, written only from the frozen targets.

    python make_finder_draft.py        (repo root) -> finders_draft.json

Each finder is derived from the target's own frozen quote, page and kind, never
from any run's records, so it cannot be tuned to an extraction. It is a draft for
Liam to review, correct and freeze; the scorer and the targets are not touched.
A target whose quote alone cannot pick one record (two values in one quote, a
relation whose endpoints the quote does not print) is marked for his decision.
"""
import json
import re

A = "artifacts/phase1_generalizable_ingestion/v4"
OUT = "artifacts/phase1_generalizable_ingestion/v6/milestone13/package4/liam/finders_draft.json"
NUMBER = re.compile(r"[~≈<>]?\s*\d[\d,.]*(?:\s*[-–]\s*\d[\d,.]*)?")


def finder(target):
    quote = " ".join(target["quote"].split())
    base = {"kind": target["kind"], "page": target.get("page"), "quote": quote}
    if target["kind"] == "entities":
        return {**base, "match": "entity label equals the quote, case and spacing normalized"}
    if target["kind"] == "statements":
        words = quote.split()
        return {
            **base,
            "match": "statement text contains this fragment",
            "fragment": " ".join(words[: min(len(words), 10)]),
        }
    if target["kind"] == "quantities":
        values = [v.strip() for v in NUMBER.findall(quote)]
        spec = {
            **base,
            "match": "quantity expression equals one printed value on this page",
            "values_in_quote": values,
        }
        if len(values) != 1:
            spec["needs_decision"] = "the quote prints several values; the expectation must name which"
            spec["expectation"] = target["expectation"]
        return spec
    return {
        **base,
        "match": "relation whose endpoints the expectation names",
        "needs_decision": "the quote does not print both endpoints; Liam to name subject, relation and object",
        "expectation": target["expectation"],
    }


def main():
    out = {}
    for source in ("ignition", "regulator", "textiles"):
        with open(f"{A}/independent_{source}/source_review.json", encoding="utf-8") as handle:
            review = json.load(handle)
        out[source] = {
            t["id"]: finder(t) for t in review["targets"] if t["outcome"] != "inaccessible"
        }
    with open(OUT, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(out, handle, indent=1, ensure_ascii=False)
        handle.write("\n")
    for source, finders in out.items():
        print(source, len(finders), "finders,", sum("needs_decision" in f for f in finders.values()), "need a decision")


main()
