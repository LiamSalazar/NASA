import gzip, json, sys, re
sys.stdout.reconfigure(encoding="utf-8")
tid, *runs = sys.argv[1:]
for r in runs:
    rv = json.load(open(f"scored/run{r}/source_review.json", encoding="utf-8"))
    t = next(t for t in rv["targets"] if t["id"] == tid)
    x = json.load(gzip.open(f"run{r}/prepared.json.gz", "rt", encoding="utf-8"))["package"]["scientific_extraction"]
    key = " ".join(t["quote"].split())[:50]
    print(f"== run {r} {t['outcome']} | {t['expectation'][:150]}")
    print("   quote:", key)
    for rec in x["records"]:
        spans = rec.get("support_spans") or []
        q = " ".join(" ".join(s.get("quote", "") for s in spans).split())
        if key[:35] in q or (rec.get("quantity_value_spans") and any(s.get("evidence_id") == t["evidence_id"] and abs(s.get("start", -999) - t["start"]) < 3 for s in rec["quantity_value_spans"])):
            p = rec["proposal"]
            print("   ", rec["id"][-8:], rec["kind"], rec["status"], p.get("class_id"), p.get("epistemic") or p.get("role"), p.get("study"), rec.get("reasons"), (p.get("label") or p.get("expression") or "")[:40])
