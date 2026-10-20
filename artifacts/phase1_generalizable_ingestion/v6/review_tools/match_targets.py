"""List, per frozen target, the active records whose spans overlap its source passage.

    python match_targets.py SOURCE_REVIEW.json PREPARED.json.gz [TARGET_IDS...]
"""
import gzip, json, sys
sys.stdout.reconfigure(encoding="utf-8")
review = json.load(open(sys.argv[1], encoding="utf-8"))
pkg = json.load(gzip.open(sys.argv[2], "rt", encoding="utf-8"))["package"]
x = pkg["scientific_extraction"]
want = set(sys.argv[3:])
lab = {e["proposal"]["key"]: " ".join(e["proposal"]["label"].split()) for e in x["records"] if e["kind"] == "entities"}
def spans(r):
    return (r.get("quantity_value_spans") or []) + (r.get("support_spans") or [])
for t in review["targets"]:
    if want and t["id"] not in want:
        continue
    hits = []
    for r in x["records"]:
        if r["kind"] != t["kind"] or r.get("duplicate_of") or r["status"] != "SOURCE_SUPPORTED":
            continue
        for s in spans(r):
            if s.get("evidence_id") == t.get("evidence_id") and s.get("start") is not None and s["start"] < t["end"] and s.get("end", s["start"]) > t["start"]:
                hits.append(r); break
    print(f"== {t['id']} p{t.get('page')} v4={t['outcome']} | {t['expectation'][:140]}")
    print("   quote:", " ".join(t["quote"].split())[:160])
    for r in hits:
        p = r["proposal"]
        print("   ", r["id"][-8:], r["status"][:6], p.get("class_id") or p.get("relation") or p.get("epistemic"), p.get("epistemic") if r["kind"] == "statements" else "", p.get("study") or "", "|", (p.get("label") or p.get("text") or "")[:70].replace("\n", " "), "|", lab.get(p.get("subject")), lab.get(p.get("object")), p.get("expression"), p.get("unit"), r["reasons"][:2])
