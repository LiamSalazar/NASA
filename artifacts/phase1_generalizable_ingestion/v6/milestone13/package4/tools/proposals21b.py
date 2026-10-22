"""Count the 2.1b new-term proposals of a run and what became of them.

    python proposals21b.py RUN_DIR
"""
import collections, gzip, json, sys
sys.stdout.reconfigure(encoding="utf-8")
run = sys.argv[1]
pkg = json.load(gzip.open(f"{run}/prepared.json.gz", "rt", encoding="utf-8"))["package"]
attempts = json.load(gzip.open(f"{run}/attempts.json.gz", "rt", encoding="utf-8"))["attempts"]
raw = collections.Counter()
for a in attempts:
    text = a.get("raw_response") or ""
    raw["PROPOSE_NEW_CLASS"] += text.count("PROPOSE_NEW_CLASS")
    raw["PROPOSE_NEW_RELATION"] += text.count("PROPOSE_NEW_RELATION")
x = pkg["scientific_extraction"]
records = [r for r in x["records"] if r["kind"] in ("entities", "relations")]
staged = [r for r in records if r.get("proposal_state") == "PROPOSED_ONTOLOGY_EXTENSION"]
reasons = collections.Counter(
    reason for r in records for reason in r.get("reasons") or [] if str(reason).startswith("PROPOSED_TERM")
)
ext = x.get("ontology_extension_proposals") or pkg.get("ontology_extension_proposals") or []
print(json.dumps({
    "sentinels_in_model_responses": dict(raw),
    "records_proposed_ontology_extension": [
        {"id": r["id"][-8:], "kind": r["kind"], "term": r["proposal"].get("class_id") or r["proposal"].get("relation"),
         "label": " ".join((r["proposal"].get("label") or "").split())[:80], "status": r["status"]} for r in staged],
    "rejections": dict(reasons),
    "extension_proposals": collections.Counter(p.get("kind") for p in ext),
    "proposed_extension_items": len(pkg.get("proposed_extension_items") or x.get("proposed_extension_items") or []),
}, ensure_ascii=False, indent=1, default=str))
