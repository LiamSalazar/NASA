"""Records whose status or text changed between two replays of the same inputs.

    python diff.py BASE_DIR NEW_DIR
"""
import gzip, json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
base, new = sys.argv[1:3]
for run in sorted(os.listdir(new)):
    p = os.path.join(new, run, "prepared.json.gz")
    if not os.path.exists(p):
        continue
    load = lambda d: {r["id"]: r for r in json.load(gzip.open(os.path.join(d, run, "prepared.json.gz"), "rt", encoding="utf-8"))["package"]["scientific_extraction"]["records"]}
    a, b = load(base), load(new)
    changes = []
    for rid in sorted(set(a) | set(b)):
        x, y = a.get(rid), b.get(rid)
        sx = (x["status"], bool(x.get("duplicate_of"))) if x else None
        sy = (y["status"], bool(y.get("duplicate_of"))) if y else None
        tx = x and (x["proposal"].get("text") or x["proposal"].get("label"))
        ty = y and (y["proposal"].get("text") or y["proposal"].get("label"))
        if sx != sy or tx != ty:
            changes.append((rid[-8:], (y or x)["kind"], sx, sy, " ".join((ty or tx or "").split())[:150], (y or {}).get("reasons", [])[:2]))
    active = lambda d: sum(r["status"] == "SOURCE_SUPPORTED" and not r.get("duplicate_of") for r in d.values())
    print(f"## {run}: active {active(a)} -> {active(b)}, changed {len(changes)}")
    for c in changes:
        print("  ", *c)
