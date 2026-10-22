"""List active records of a run with no earlier judgment for the same proposal id.

    python unjudged.py PREPARED.json.gz [ADJUDICATED_PREPARED...]   (run from the repo root)

Prior judgments: v5/v6 source_review.json proposal samples (PTFE). For other
sources, ADJUDICATED_PREPARED are earlier prepared packages whose verdicts are
given separately; here only the ids are compared.
"""
import glob, gzip, json, sys
sys.stdout.reconfigure(encoding="utf-8")
pkg = json.load(gzip.open(sys.argv[1], "rt", encoding="utf-8"))["package"]
x = pkg["scientific_extraction"]["records"]
ev = {e["evidence_id"]: e for e in pkg["evidence"]}
lab = {e["proposal"]["key"]: " ".join(e["proposal"]["label"].split()) for e in x if e["kind"] == "entities"}
prior = set()
for path in glob.glob("artifacts/phase1_generalizable_ingestion/v[56]/**/source_review.json", recursive=True):
    prior |= {p["proposal_id"] for p in json.load(open(path, encoding="utf-8")).get("proposal_sample", [])}
n = 0
for r in x:
    if r["status"] != "SOURCE_SUPPORTED" or r.get("duplicate_of"):
        continue
    n += 1
    if r["id"] in prior:
        continue
    p = r["proposal"]
    sp = r.get("quantity_value_spans") or r.get("support_spans") or [{}]
    page = ev.get(sp[0].get("evidence_id"), {}).get("page")
    if r["kind"] == "entities":
        d = f"{p['class_id']} {p.get('study')} | {' '.join(p['label'].split())}"
    elif r["kind"] == "statements":
        d = f"{p['epistemic']} {p.get('study')} subj={[lab.get(s) for s in p.get('subjects', [])]} | {' '.join(p['text'].split())}"
    elif r["kind"] == "relations":
        d = f"{lab.get(p['subject'])} --{p['relation']}--> {lab.get(p['object'])}"
    else:
        d = f"{p['epistemic']} {p['label']} = {p['expression']} {p.get('unit')} subj={lab.get(p['subject'])} prop={r.get('mapping',{}).get('property_id')} printed={p.get('printed_name')}"
    print(r["id"][-8:], r["kind"][0], f"p{page}", d)
print("active", n, file=sys.stderr)
