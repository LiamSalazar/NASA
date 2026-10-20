"""Compare HEAD replays of the five v4 exposed sources with the v5 closure counts,
and re-check every historical critical negative.

    python exposed_compare.py REPLAY_ROOT OUT_DIR
REPLAY_ROOT/<source>/prepared.json.gz must exist for the five sources and for
ptfe_live_2b7d1d6 and ptfe_live_e19b7c0_7997b58.
"""

import gzip
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

root, out = Path(sys.argv[1]), Path(sys.argv[2])
V5 = Path("artifacts/phase1_generalizable_ingestion/v5/phase1_closure")
head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()


def records(path):
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)["package"]["scientific_extraction"]["records"]


def counts(rs):
    return {
        k: dict(Counter(r["status"] for r in rs if r["kind"] == k))
        for k in ("entities", "quantities", "statements", "relations")
    }


closure = json.load(open(V5 / "exposed_sources_replay/comparison.json", encoding="utf-8"))
comparison = {
    "kind": "PHASE1_V6_M1_EXPOSED_SOURCE_REPLAY_COMPARISON",
    "inputs": "Saved v4 application receipts (raw Nemotron proposals); 0 model calls",
    "closure_code": closure["closure_code"],
    "code": head,
    "scientific_acceptance": "STATUS CHANGES ONLY; NEW SOURCE_SUPPORTED RECORDS LISTED FOR REVIEW",
    "sources": {},
}
for name, data in closure["sources"].items():
    rs = records(root / name / "prepared.json.gz")
    now = counts(rs)
    newly = [
        {
            "id": r["id"],
            "kind": r["kind"],
            "label": r["proposal"].get("label"),
            "expression": r["proposal"].get("expression"),
            "unit": r["proposal"].get("unit"),
            "subject_recovery": (r.get("subject_recovery") or {}).get("status"),
            "mapping": (r.get("mapping") or {}).get("kind"),
        }
        for r in rs
        if r["kind"] == "quantities" and r["status"] == "SOURCE_SUPPORTED" and not r.get("duplicate_of")
    ]
    comparison["sources"][name] = {
        "closure": data["closure"],
        "v6_m1": now,
        "changed_kinds": sorted(k for k in now if now[k] != data["closure"].get(k)),
        "supported_quantities_now": newly,
    }
negatives = json.load(open(V5 / "historical_negatives_receipt.json", encoding="utf-8"))
replay_for = {
    "ignition_v4": "independent_ignition_application",
    "regulator_v4": "independent_regulator_application",
    "textiles_v4": "independent_textiles_application",
    "ptfe_live_2b7d1d6_review": "ptfe_live_2b7d1d6",
    "ptfe_live_e19b7c0_review": "ptfe_live_e19b7c0_7997b58",
}
receipt = {
    "kind": "PHASE1_HISTORICAL_NEGATIVES_RECEIPT",
    "git_head": head,
    "model_calls": 0,
    "rule": negatives["rule"],
    "previous_receipt": (V5 / "historical_negatives_receipt.json").as_posix(),
    "sets": [],
}
regressions = known = 0
for s in negatives["sets"]:
    path = root / replay_for[s["label"]] / "prepared.json.gz"
    now = {r["id"]: r for r in records(path)}
    items = []
    for item in s["items"]:
        r = now.get(item["id"])
        status = r["status"] if r else "ABSENT"
        items.append(
            {
                "id": item["id"],
                "critical": item["critical"],
                "status_v5": item["status_now"],
                "status_now": status,
                "reasons_now": r["reasons"] if r else [],
            }
        )
    supported = [i["id"] for i in items if i["status_now"] == "SOURCE_SUPPORTED"]
    crit = [i for i in supported if next(x for x in items if x["id"] == i)["critical"]]
    regressions += len(crit)
    known += len(supported) - len(crit)
    receipt["sets"].append(
        {
            "label": s["label"],
            "original_package": s["original_package"],
            "replay_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "count": len(items),
            "status_now": dict(Counter(i["status_now"] for i in items)),
            "critical_regressions_now_supported": crit,
            "noncritical_still_supported": [i for i in supported if i not in crit],
            "items": items,
        }
    )
receipt.update(total=sum(s["count"] for s in receipt["sets"]), critical_regressions=regressions,
               known_noncritical_incorrect_still_supported=known)
out.mkdir(parents=True, exist_ok=True)
for name, data in (("exposed_sources_comparison.json", comparison), ("historical_negatives_receipt.json", receipt)):
    with open(out / name, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
for name, data in comparison["sources"].items():
    print(name, "changed:", data["changed_kinds"], "quantities", data["closure"]["quantities"], "->", data["v6_m1"]["quantities"], "supported", len(data["supported_quantities_now"]))
print("negatives total", receipt["total"], "critical regressions", regressions, "noncritical supported", known)
