"""Carry judgments to identical assertions under new proposal ids.

    python assertion_judgments.py BASE_JUDGMENTS.json OUT.json PREPARED.json.gz ...
An assertion is the same when its kind, normalized text or label, role, class,
study, unit, value and resolved subject/scope labels are identical to a record
already judged in the rescored c314286 reviews. Prints what stays unjudged.
"""
import glob, gzip, json, sys
sys.stdout.reconfigure(encoding="utf-8")
base, out, *paths = sys.argv[1:]
judgments = json.load(open(base, encoding="utf-8"))
B = "artifacts/phase1_generalizable_ingestion/v6/milestone4/rescored_c314286"


def keyed(package):
    x = package["scientific_extraction"]
    ents = {e["proposal"]["key"]: " ".join(e["proposal"]["label"].split()) for e in x["records"] if e["kind"] == "entities"}
    ids = {e.get("entity_id"): " ".join(e["proposal"]["label"].split()) for e in x["records"] if e["kind"] == "entities"}
    out = {}
    for r in x["records"]:
        p = r["proposal"]
        k = (
            r["kind"],
            " ".join((p.get("text") or p.get("label") or "").split()),
            p.get("epistemic"), p.get("class_id"), p.get("study"), p.get("relation"),
            p.get("expression"), p.get("unit"),
            ents.get(p.get("subject")), ents.get(p.get("object")),
            tuple(sorted(ids.get(s, s) for s in r.get("scope", []))),
        )
        out[r["id"]] = (k, r)
    return out


known = {}
for path in sorted(glob.glob(f"{B}/ptfe_run*/prepared.json.gz")):
    review = json.load(open(path.replace("prepared.json.gz", "review/source_review.json"), encoding="utf-8"))
    j = {p["proposal_id"]: p for p in review["proposal_sample"]}
    for pid, (k, r) in keyed(json.load(gzip.open(path, "rt", encoding="utf-8"))["package"]).items():
        if pid in j:
            known.setdefault(k, (j[pid]["correct"], j[pid]["reason"], pid))
prior = set()
for path in glob.glob("artifacts/phase1_generalizable_ingestion/v[56]/**/source_review.json", recursive=True):
    prior.update(p["proposal_id"] for p in json.load(open(path, encoding="utf-8")).get("proposal_sample", []))
for path in paths:
    for pid, (k, r) in keyed(json.load(gzip.open(path, "rt", encoding="utf-8"))["package"]).items():
        if r["status"] != "SOURCE_SUPPORTED" or r.get("duplicate_of") or pid in prior or pid[-8:] in judgments:
            continue
        if k in known:
            c, reason, src = known[k]
            judgments[pid[-8:]] = [c, reason + f" (same assertion as judged proposal {src[-8:]})"]
        else:
            print("UNJUDGED", path.split("/")[-2], pid[-8:], k[0], k[2] or k[3] or k[5], "|", k[1][:200], "|", k[6], k[7], k[8], k[9], k[10][:2])
with open(out, "w", encoding="utf-8", newline="\n") as handle:
    json.dump(judgments, handle, indent=1, ensure_ascii=False)
