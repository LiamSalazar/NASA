"""Build a review for any PTFE run from frozen targets, record finders and judgments.

    python build_review_generic.py PREPARED.json.gz BASIS OUT.json [NEW_JUDGMENTS.json]

Each frozen target has a finder over the run's records (labels, texts, values,
pages). A target is correct when an active SOURCE_SUPPORTED record it finds is
judged correct, incorrect when it is judged incorrect, unresolved when only
UNRESOLVED records are found, omitted otherwise. Judgments are reused for
identical proposal ids from every earlier v5/v6 review; any other active record
must be in NEW_JUDGMENTS ({suffix: [correct, reason]}) or the build stops.
"""

import copy
import glob
import gzip
import json
import sys
from collections import Counter

prepared_path, basis, out = sys.argv[1:4]
new_judgments = json.load(open(sys.argv[4], encoding="utf-8")) if len(sys.argv) > 4 else {}
package = json.load(gzip.open(prepared_path, "rt", encoding="utf-8"))["package"]
x = package["scientific_extraction"]
records = {r["id"]: r for r in x["records"]}
pdf = {r["id"]: r for r in x["pdf_table_quantity_proposals"]}
evidence = {e["evidence_id"]: e for e in package["evidence"]}
label = {r["proposal"]["key"]: r["proposal"]["label"] for r in x["records"] if r["kind"] == "entities"}
template = json.load(
    open("artifacts/phase1_generalizable_ingestion/v6/milestone1/ptfe_run1_replay/review/source_review.json", encoding="utf-8")
)
prior = {}
for path in sorted(glob.glob("artifacts/phase1_generalizable_ingestion/v[56]/**/source_review.json", recursive=True)):
    for p in json.load(open(path, encoding="utf-8")).get("proposal_sample", []):
        prior.setdefault(p["proposal_id"], (p, path))


def page(r):
    spans = r.get("quantity_value_spans") or r.get("support_spans") or []
    return evidence[spans[0]["evidence_id"]]["page"] if spans else None


def ent(text, cls=None, study=None):
    return lambda r: r["kind"] == "entities" and " ".join(r["proposal"]["label"].split()).lower() == " ".join(text.split()).lower() and (
        cls is None or r["proposal"]["class_id"] == cls) and (study is None or r["proposal"]["study"] == study)


def qty(expression, pg, label_part=None, epistemic=None):
    return lambda r: r["kind"] == "quantities" and r["proposal"]["expression"] == expression and page(r) == pg and (
        label_part is None or label_part in r["proposal"]["label"].lower()) and (
        epistemic is None or r["proposal"]["epistemic"] == epistemic)


def stmt(fragment):
    return lambda r: r["kind"] == "statements" and fragment in " ".join(r["proposal"]["text"].split())


def rel(relation, subject_part, obj=None):
    return lambda r: r["kind"] == "relations" and r["proposal"]["relation"] == relation and subject_part in label.get(
        r["proposal"]["subject"], "") and (obj is None or label.get(r["proposal"]["object"]) == obj)


FINDERS = {
    "entities-01": ent("Oxygen Compatibility of Brass-Filled PTFE Compared to Commonly Used Fluorinated Polymers for Oxygen Systems", "Investigation"),
    "entities-02": ent("Brass-filled PTFE samples", "Sample"),
    "entities-03": ent("Brass-filled PTFE", "Material", "current"),
    "entities-04": ent("Salox-M®", None, "current"),
    "entities-05": ent("Algoflon® E2", None, "current"),
    "entities-06": ent("Algoflon® F7", None, "current"),
    "entities-07": lambda r: r["kind"] == "entities" and "(batch #1)" in r["proposal"]["label"].lower(),
    "entities-08": lambda r: r["kind"] == "entities" and "(batch #2)" in r["proposal"]["label"].lower(),
    "quantities-09": qty("1332", 8),
    "quantities-10": qty("13.81", 8, None, "derived_quantity"),
    "quantities-11": qty(">425", 8, "ait"),
    "quantities-12": qty("1500", 8, "initial"),
    "quantities-13": qty("2268", 8),
    "quantities-14": lambda r: r["kind"] == "quantities" and r["proposal"]["expression"] == "12" and r["proposal"]["epistemic"] == "derived_quantity",
    "quantities-15": qty("98", 9),
    "quantities-16": qty("10,000", 9),
    "quantities-17": lambda r: r["kind"] == "quantities" and r["proposal"]["expression"] == "5" and (r["proposal"].get("unit") or "").strip() == "%" and page(r) == 10,
    "quantities-18": lambda r: r["kind"] == "quantities" and r["proposal"]["expression"] == "40" and (r["proposal"].get("unit") or "").strip() == "%" and page(r) == 10 and "salox" in label.get(r["proposal"]["subject"], "").lower(),
    "statements-19": stmt("The data used to compare Brass-filled PTFE to other polymers"),
    "statements-20": stmt("samples discussed in this paper were evaluated using a Parr 6200"),
    "statements-21": stmt("a mineral oil spike was used"),
    "statements-22": stmt("If the system temperature rises above 425"),
    "statements-23": stmt("If one sample out of 20 reacts"),
    "statements-24": stmt("Their data indicates that only TFE-Teflon"),
    "statements-25": lambda r: stmt("Neither the LOX nor GOX tests showed any reactions")(r) or stmt("Four of the additional 80 LOX")(r),
    "statements-26": stmt("second batch of Brass-filled PTFE performed the same"),
    "statements-27": stmt("Since the exact chemical make up of the Brass component"),
    "statements-28": stmt("pre-sintered E2 Algoflon® produced no reactions"),
    "statements-29": stmt("choice of the filler material and the percentage of filler"),
    "statements-30": stmt("Even though the Brass-filled PTFE performs similarly to TFE-Teflon"),
    "relations-31": rel("belongsToInvestigation", "samples"),
    "relations-32": rel("hasCondition", "(Batch #1)", "LOX/-297°F"),
    "relations-33": lambda r: r["kind"] == "relations" and "salox" in label.get(r["proposal"]["subject"], "").lower() and "bronze" in label.get(r["proposal"]["object"], "").lower(),
    "relations-34": rel("madeOf", "(Batch #1)"),
}
PDF_FALLBACK = {"quantities-10": "528308fb", "quantities-11": "7b2a73de", "quantities-12": "1a915cc1", "quantities-13": "beb821ff", "quantities-09": "6a385d9b"}
active = [r for r in x["records"] if r["status"] == "SOURCE_SUPPORTED" and not r.get("duplicate_of")]
sample = []
judgment = {}
for r in active:
    if r["id"] in prior:
        p = copy.deepcopy(prior[r["id"]][0])
        p["judgment_source"] = "REUSED_IDENTICAL_PROPOSAL_ID: " + prior[r["id"]][1]
    elif r["id"][-8:] in new_judgments:
        correct, reason = new_judgments[r["id"][-8:]]
        p = {"proposal_id": r["id"], "correct": correct, "critical": False, "reason": reason,
             "judgment_source": "AUTHOR_ADJUDICATION_FULL_RECORD_V6"}
    else:
        raise SystemExit(f"judgment needed: {r['id']} {r['kind']} {json.dumps(r['proposal'], ensure_ascii=False)[:300]}")
    sample.append(p)
    judgment[r["id"]] = p["correct"]
review = {"basis": basis, "source_reference_sha256": template["source_reference_sha256"], "targets": [], "proposal_sample": sample}
for t in template["targets"]:
    target = {k: v for k, v in t.items() if k not in {"outcome", "proposal_ids", "review_note", "previous_outcome_v5", "previous_outcome"}}
    finder = FINDERS.get(t["id"])
    if finder is None:
        target["outcome"] = "inaccessible"
        review["targets"].append(target)
        continue
    found = [r for r in x["records"] if finder(r)]
    good = [r for r in found if r["id"] in judgment and judgment[r["id"]]]
    bad = [r for r in found if r["id"] in judgment and not judgment[r["id"]]]
    held = [r for r in found if r["status"] == "UNRESOLVED"]
    if good:
        target["outcome"], refs = "correct", [good[0]["id"]]
    elif bad:
        target["outcome"], refs = "incorrect", [bad[0]["id"]]
    elif held:
        target["outcome"], refs = "unresolved", [r["id"] for r in held[:2]]
    elif t["id"] in PDF_FALLBACK:
        refs = [i for i in pdf if i.endswith(PDF_FALLBACK[t["id"]]) and pdf[i]["status"] == "UNRESOLVED"]
        target["outcome"] = "unresolved" if refs else "omitted"
    else:
        target["outcome"], refs = "omitted", []
    if refs:
        target["proposal_ids"] = refs
    if t["id"] == "statements-25" and target["outcome"] == "unresolved":
        target["hold_assessment"] = "HOLD_IS_THE_CORRECT_OUTCOME"
        target["hold_rationale"] = (
            "The source prints 'no reactions out of the 80 impacts' and 'Four of the additional 80 LOX samples "
            "reacted' with Table 3 LOX 4/80; the frozen expectation is to preserve both unresolved."
        )
    review["targets"].append(target)
with open(out, "w", encoding="utf-8", newline="\n") as handle:
    json.dump(review, handle, indent=2, ensure_ascii=False)
    handle.write("\n")
print(dict(Counter(t["outcome"] for t in review["targets"])), "judged", len(sample))
