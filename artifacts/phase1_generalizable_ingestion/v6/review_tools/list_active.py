import gzip, json, sys
sys.stdout.reconfigure(encoding="utf-8")
pkg = json.load(gzip.open(sys.argv[1], "rt", encoding="utf-8"))["package"]
x = pkg["scientific_extraction"]["records"]
ev = {e["evidence_id"]: e for e in pkg["evidence"]}
lab = {e["proposal"]["key"]: " ".join(e["proposal"]["label"].split()) for e in x if e["kind"] == "entities"}
for r in x:
    if r["status"] != "SOURCE_SUPPORTED" or r.get("duplicate_of"):
        continue
    p = r["proposal"]
    sp = r.get("quantity_value_spans") or r.get("support_spans") or [{}]
    page = ev.get(sp[0].get("evidence_id"), {}).get("page")
    if r["kind"] == "entities":
        d = f"{p['class_id']} {p.get('study')} | {' '.join(p['label'].split())}"
    elif r["kind"] == "statements":
        d = f"{p['epistemic']} {p.get('study')} subj={[lab.get(s) for s in p.get('subjects', [])]} | {' '.join(p['text'].split())[:200]}"
    elif r["kind"] == "relations":
        d = f"{lab.get(p['subject'])} --{p['relation']}--> {lab.get(p['object'])}"
    else:
        d = f"{p['epistemic']} {p['label']} = {p['expression']} {p.get('unit')} subj={lab.get(p['subject'])} prop={r.get('mapping',{}).get('property_id')}"
    print(r["id"][-8:], r["kind"][0], f"p{page}", d)
