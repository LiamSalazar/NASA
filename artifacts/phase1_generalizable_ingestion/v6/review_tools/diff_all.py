import gzip, json, sys
sys.stdout.reconfigure(encoding="utf-8")
a_root, b_root = sys.argv[1:3]
names = [f"run{r}" for r in (1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13)] + ["dev_ignition", "dev_regulator", "dev_textiles"]
def act(path):
    x = json.load(gzip.open(path, "rt", encoding="utf-8"))["package"]["scientific_extraction"]["records"]
    lab = {e["proposal"]["key"]: " ".join(e["proposal"]["label"].split()) for e in x if e["kind"] == "entities"}
    return {(z["kind"], " ".join((z["proposal"].get("text") or z["proposal"].get("label") or "").split())[:80], z["proposal"].get("epistemic") or z["proposal"].get("class_id") or z["proposal"].get("relation"), lab.get(z["proposal"].get("subject")), lab.get(z["proposal"].get("object")), z["proposal"].get("expression")) for z in x if z["status"] == "SOURCE_SUPPORTED" and not z.get("duplicate_of")}
for n in names:
    try:
        a, b = act(f"{a_root}/{n}/prepared.json.gz"), act(f"{b_root}/{n}/prepared.json.gz")
    except FileNotFoundError as e:
        print(n, "missing", e); continue
    if a != b:
        print(n, "ADDED", sorted(b - a, key=str)); print("   REMOVED", sorted(a - b, key=str))
