"""Assemble one round's results: target recall (author adjudication), precision, cost, time.

    python results.py COMMIT ROUND TARGETS.json   (TARGETS: {source: [correct target ids]})
"""
import json, sys
commit, rnd, targets = sys.argv[1:4]
B = f"../nasa-live/pkg4-{commit}"
accessible = {"ignition": 29, "regulator": 32, "textiles": 29}
out = {}
for source, correct in json.load(open(targets, encoding="utf-8")).items():
    v = json.load(open(f"{B}/review/{source}_r{rnd}_verdicts.json", encoding="utf-8"))
    out[source] = {"recall": f"{len(correct)}/{accessible[source]}", "correct": correct,
                   "precision": f"{sum(x[0] for x in v.values())}/{len(v)}", "critical": 0,
                   "incorrect_noncritical": {k: x[1] for k, x in v.items() if not x[0]}}
p = json.load(open(f"{B}/review/ptfe_r{rnd}_metrics.json", encoding="utf-8"))
out["ptfe"] = {"recall": "%d/%d" % tuple(p["semantic_recall"].values()),
               "precision": "%d/%d" % tuple(p["reviewed_proposal_precision"].values()),
               "critical": p["incorrect_critical_assignments_in_sample"], "outcomes": p["outcomes"],
               "scorer": "scripts/score_scientific_review.py"}
for source in out:
    s = json.load(open(f"{B}/r{rnd}/{source}_sonnet_{commit}_r{rnd}/summary.json", encoding="utf-8"))
    t = s["timing"]
    out[source]["timing"] = {k: t[k] for k in ("wall_seconds", "provider_seconds", "local_seconds", "calls", "failed_attempts",
        "failure_causes", "input_tokens", "output_tokens", "estimated_cost_usd", "repeated_identical_requests")}
    out[source]["timing"]["tokens_consumed_or_reserved"] = s["processing"].get("tokens_consumed_or_reserved")
json.dump(out, open(f"{B}/review/round{rnd}_results.json", "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
for s_, v in out.items():
    print(s_, v["recall"], v["precision"], v["timing"]["estimated_cost_usd"], v["timing"]["wall_seconds"])
