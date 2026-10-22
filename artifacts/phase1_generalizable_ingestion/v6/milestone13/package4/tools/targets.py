"""Per frozen target, the overlapping records of a run with their judgment.

    python targets.py SOURCE ROUND   (repo root)
"""
import collections, gzip, json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
source, rnd = sys.argv[1:3]
C = os.environ.get("PKG_COMMIT", "dc6f342")
B = f"../nasa-live/pkg4-{C}"
A = "artifacts/phase1_generalizable_ingestion"
pkg = json.load(gzip.open(f"{B}/r{rnd}/{source}_sonnet_{C}_r{rnd}/prepared.json.gz", "rt", encoding="utf-8"))["package"]
carry = json.load(open(f"{B}/review/{source}_r{rnd}_carry.json", encoding="utf-8"))
manual = {}
for folder in ("../nasa-live/pkg4-dc6f342", B):
    path = f"{folder}/review/{source}_manual.json"
    if os.path.exists(path):
        manual.update(json.load(open(path, encoding="utf-8")))
verdict = {k: v[0] for k, v in carry["carried"].items()}
verdict.update({k: v[0] for k, v in manual.items()})
review = json.load(open(f"{A}/v4/independent_{source}/source_review.json", encoding="utf-8"))
recs = pkg["scientific_extraction"]["records"]
lab = {e["proposal"]["key"]: " ".join(e["proposal"]["label"].split()) for e in recs if e["kind"] == "entities"}
earlier = {}
for m in ("milestone12", "milestone13"):
    for name, run in json.load(open(f"{A}/v6/{m}/evaluation_b.json", encoding="utf-8"))["runs"].items():
        if name.startswith(source + "_"):
            earlier[f"{m[-2:]}{name[len(source):]}"] = set(run["correct"])
for name, run in json.load(open(f"{A}/v6/milestone13/pilot_anthropic/pilot_results.json", encoding="utf-8"))["runs"].items():
    if name.startswith(source + "_"):
        earlier[name[len(source) + 1:]] = set(run["correct"])


def overlaps(r, t):
    for s in (r.get("quantity_value_spans") or []) + (r.get("support_spans") or []):
        if s.get("evidence_id") == t["evidence_id"] and s.get("start") is not None and s["start"] < t["end"] and s.get("end", s["start"]) > t["start"]:
            return True
    return False


def show(r):
    p = r["proposal"]
    if r["kind"] == "entities":
        d = f"{p['class_id']} {p.get('study')} {lab.get(p['key'])}"
    elif r["kind"] == "statements":
        d = f"{p['epistemic']} {p.get('study')} subj={[lab.get(s) for s in p.get('subjects', [])]} | {' '.join(p['text'].split())[:150]}"
    elif r["kind"] == "relations":
        d = f"{lab.get(p['subject'])} --{p['relation']}--> {lab.get(p['object'])}"
    else:
        d = f"{p['epistemic']} {p['label']} = {p['expression']} {p.get('unit')} subj={lab.get(p['subject'])}"
    return d


for t in review["targets"]:
    if t["outcome"] == "inaccessible":
        continue
    hits = [r for r in recs if r["kind"] == t["kind"] and overlaps(r, t) and not r.get("duplicate_of")]
    prior = "".join("+" if t["id"] in v else "." for v in earlier.values())
    print(f"== {t['id']} [{prior}] {t['expectation'][:150]}")
    print("   quote:", " ".join(t["quote"].split())[:150])
    for r in hits:
        st = r["status"]
        j = verdict.get(r["id"][-8:]) if st == "SOURCE_SUPPORTED" else None
        reason = "" if st == "SOURCE_SUPPORTED" else str((r.get("reasons") or [""])[0])[:60]
        print(f"   {r['id'][-8:]} {st[:9]} {'OK ' if j else 'BAD' if j is False else '   '} {show(r)[:170]} {reason}")
print("earlier runs:", list(earlier))
