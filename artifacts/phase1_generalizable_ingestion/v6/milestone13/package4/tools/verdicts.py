"""Write a run's final verdicts from its carry file and the manual judgments; print precision.

    python verdicts.py COMMIT SOURCE ROUND
"""
import json, sys
commit, source, rnd = sys.argv[1:4]
review = f"../nasa-live/pkg4-{commit}/review"
carry = json.load(open(f"{review}/{source}_r{rnd}_carry.json", encoding="utf-8"))
manual = json.load(open(f"{review}/{source}_manual.json", encoding="utf-8"))
out = {k: [v[0], v[1]] for k, v in carry["carried"].items()}
missing = [t["id"] for t in carry["to_judge"] if t["id"] not in manual]
if missing:
    raise SystemExit("judgment needed: " + " ".join(missing))
out.update({t["id"]: manual[t["id"]] for t in carry["to_judge"]})
# A manual judgment of the same record id prevails over a carried one (context-specific errors).
out.update({k: manual[k] for k in out if k in manual})
json.dump(out, open(f"{review}/{source}_r{rnd}_verdicts.json", "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
good = sum(v[0] for v in out.values())
print(source, f"r{rnd}", f"precision {good}/{len(out)}", "incorrect:", {k: v[1][:70] for k, v in out.items() if not v[0]})
