"""Render the miss diagnosis json as milestone13/target_miss_diagnosis.md.

    python miss_md.py DIAG_JSON OUT_MD
"""

import collections
import json
import sys

d = json.load(open(sys.argv[1], encoding="utf-8"))
NAMES = {
    "NOT_PROPOSED": "not proposed",
    "PROPOSED_REJECTED": "proposed and rejected",
    "ACCEPTED_MISGRADED": "accepted, graded wrong",
    "WINDOW_LOST": "window lost",
}


def cell(r):
    if not r:
        return "correct"
    if r["class"] == "PROPOSED_REJECTED":
        return "rejected: `" + max(r["reasons"], key=r["reasons"].get) + "`"
    if r["class"] == "ACCEPTED_MISGRADED":
        return "accepted, graded wrong (" + ", ".join(str(s["type"]) for s in r["supported"]) + ")"
    if r["class"] == "NOT_PROPOSED" and r.get("other_kinds_overlapping"):
        return "not proposed (proposed as " + "/".join(r["other_kinds_overlapping"]) + ")"
    return NAMES[r["class"]]


out = [
    "# Milestone 13: diagnosis of each missed target (ignition, regulator, textiles)",
    "",
    "Built from the milestone 12 evaluation B runs at `0a5a860` (r1 and r2) and their",
    "offline replays at milestone 13 code (0 model calls). Each accessible frozen v4 target",
    "that the run's adjudication (`milestone12/evaluation_b.json`) did not count correct",
    "gets one class:",
    "",
    "- **window lost**: no finished model request carried the target's printed words;",
    "- **not proposed**: no record of the target's kind overlaps the target span;",
    "- **proposed and rejected**: records of the kind overlap it, none SOURCE_SUPPORTED",
    "  (the most frequent first reason code is shown);",
    "- **accepted, graded wrong**: a SOURCE_SUPPORTED record overlaps it, but the",
    "  adjudication did not count it correct (wrong subject, value, role or type).",
    "",
    "Overlap is by evidence span, so a rejected record that only shares the sentence",
    "counts as a proposal for the target. This is a diagnosis aid, not a scorer, and does",
    "not change any frozen target or adjudication.",
    "The milestone 13 replay of the same inputs gives the same class for every target,",
    "since corrections 2 and 3 only remove records.",
    "",
    "## Summary (target-run pairs, live milestone 12)",
    "",
    "| source | correct r1 / r2 | not proposed | proposed and rejected | accepted, graded wrong | window lost |",
    "|---|---|---|---|---|---|",
]
codes = collections.Counter()
for src in ("ignition", "regulator", "textiles"):
    c = collections.Counter()
    acc = d["runs"][f"{src}_r1_live_m12"]["accessible"]
    for run in ("r1", "r2"):
        v = d["runs"][f"{src}_{run}_live_m12"]
        c.update(v["by_class"])
        for r in v["targets"].values():
            if r["class"] == "PROPOSED_REJECTED":
                codes[(max(r["reasons"], key=r["reasons"].get), r["kind"])] += 1
    out.append(
        f"| {src} | {d['runs'][f'{src}_r1_live_m12']['correct']}/{acc} / "
        f"{d['runs'][f'{src}_r2_live_m12']['correct']}/{acc} | {c['NOT_PROPOSED']} | "
        f"{c['PROPOSED_REJECTED']} | {c['ACCEPTED_MISGRADED']} | {c['WINDOW_LOST']} |"
    )
out += ["", "## Rejection codes (target-run pairs)", "", "| code | kind | pairs |", "|---|---|---|"]
for (code, kind), n in codes.most_common():
    out.append(f"| `{code}` | {kind} | {n} |")
for src in ("ignition", "regulator", "textiles"):
    out += ["", f"## {src}", "", "| target | kind | printed words | r1 | r2 |", "|---|---|---|---|---|"]
    r1 = d["runs"][f"{src}_r1_live_m12"]["targets"]
    r2 = d["runs"][f"{src}_r2_live_m12"]["targets"]
    for tid in sorted(set(r1) | set(r2)):
        r = r1.get(tid) or r2.get(tid)
        quote = r["quote"][:90].replace("|", "/")
        out.append(f"| {tid} | {r['kind']} | {quote} | {cell(r1.get(tid))} | {cell(r2.get(tid))} |")
open(sys.argv[2], "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
print("ok")
