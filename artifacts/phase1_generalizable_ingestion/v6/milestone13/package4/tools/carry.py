"""Carry earlier judgments to identical records of a new run, and list the rest.

    python carry.py SOURCE PREPARED.json.gz OUT.json     (run from the repo root)

A record is identical when its content signature matches a record judged in an
earlier adjudicated run of the same source: kind, type (class, relation or
epistemic role), study, normalized label or text, subject/object/subjects
labels, value expression and unit. Earlier judgments come from
  - non-PTFE: evaluation_b.json of milestones 11-13 and pilot_results.json
    (active records of the run; listed ids incorrect, the rest correct);
  - PTFE: every v6 review/review.json proposal sample;
  - every earlier package 4 run, from its review/{source}_rN_verdicts.json.
Signatures judged both ways are not carried. Output: {suffix: [correct, reason,
source]} for carried records and a list of the records still to be judged.
"""
import glob, gzip, json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
V6 = "artifacts/phase1_generalizable_ingestion/v6"


def norm(s):
    return " ".join((s or "").split()).lower()


def load(path):
    return json.load(gzip.open(path, "rt", encoding="utf-8"))["package"]


def signatures(pkg):
    recs = pkg["scientific_extraction"]["records"]
    lab = {e["proposal"]["key"]: norm(e["proposal"]["label"]) for e in recs if e["kind"] == "entities"}
    out = {}
    for r in recs:
        if r["status"] != "SOURCE_SUPPORTED" or r.get("duplicate_of"):
            continue
        p = r["proposal"]
        sig = (
            r["kind"], p.get("class_id") or p.get("relation") or "", p.get("epistemic") or "",
            p.get("study") or "", norm(p.get("label") or p.get("text")),
            lab.get(p.get("subject"), ""), lab.get(p.get("object"), ""),
            tuple(sorted(lab.get(s, "") for s in p.get("subjects") or [])),
            p.get("expression") or "", norm(p.get("unit")),
        )
        out[r["id"]] = (sig, r)
    return out


def prior_runs(source):
    runs = []
    if source == "ptfe":
        for path in glob.glob(f"{V6}/**/ptfe_*/review/*review.json", recursive=True):
            folder = os.path.dirname(os.path.dirname(path))
            prepared = os.path.join(folder, "prepared.json.gz")
            if os.path.exists(prepared):
                sample = json.load(open(path, encoding="utf-8"))["proposal_sample"]
                runs.append((prepared, {p["proposal_id"][-8:]: (p["correct"], p["reason"]) for p in sample}, None))
        return runs
    for m, tag in (("milestone11", "8e3f4e7"), ("milestone12", "0a5a860"), ("milestone13", "b4be17d")):
        ev = json.load(open(f"{V6}/{m}/evaluation_b.json", encoding="utf-8"))["runs"]
        for name, run in ev.items():
            if name.startswith(source + "_") and "x30b" not in name:
                folder = f"{V6}/{m}/{source}_live_{tag}_{name.split('_')[1]}"
                if os.path.exists(folder):
                    bad = dict(run.get("incorrect_noncritical") or {})
                    bad.update(run.get("incorrect_critical") or {})
                    runs.append((f"{folder}/prepared.json.gz", None, bad))
    pilot = json.load(open(f"{V6}/milestone13/pilot_anthropic/pilot_results.json", encoding="utf-8"))
    for block in (pilot["runs"], pilot.get("opus_comparison", {}).get("runs", {})):
        for name, run in block.items():
            if name.startswith(source + "_"):
                for folder in glob.glob(f"{V6}/milestone13/pilot_anthropic/{name}_*"):
                    bad = dict(run.get("incorrect_noncritical") or {})
                    runs.append((f"{folder}/prepared.json.gz", None, bad))
    return runs


def package4_runs(source, prepared):
    """Earlier package 4 runs of the source, with their final verdicts."""
    runs = []
    for verdicts in sorted(glob.glob(f"../nasa-live/pkg4-*/review/{source}_r*_verdicts.json")):
        folder, name = os.path.split(verdicts)
        commit = folder.replace("\\", "/").split("/")[-2][len("pkg4-"):]
        rnd = name[len(source) + 2 : -len("_verdicts.json")]
        run = f"{os.path.dirname(folder)}/r{rnd}/{source}_sonnet_{commit}_r{rnd}/prepared.json.gz"
        if os.path.abspath(run) != os.path.abspath(prepared):
            explicit = {k: (v[0], v[1]) for k, v in json.load(open(verdicts, encoding="utf-8")).items()}
            runs.append((run, explicit, None))
    return runs


def main():
    source, prepared, out = sys.argv[1:4]
    judged = {}
    for path, explicit, bad in prior_runs(source) + package4_runs(source, prepared):
        for rid, (sig, r) in signatures(load(path)).items():
            suffix = rid[-8:]
            if explicit is not None:
                if suffix not in explicit:
                    continue
                verdict = explicit[suffix]
            else:
                verdict = (False, bad[suffix]) if suffix in bad else (True, "judged correct in that run")
            judged.setdefault(sig, {})[verdict[0]] = (verdict[1], os.path.dirname(path))
    carried, todo = {}, []
    lab_pkg = load(prepared)
    for rid, (sig, r) in signatures(lab_pkg).items():
        verdicts = judged.get(sig, {})
        if len(verdicts) == 1:
            correct, (reason, origin) = next(iter(verdicts.items()))
            carried[rid[-8:]] = [correct, reason, "CARRIED_IDENTICAL_RECORD: " + origin.replace("\\", "/")]
        else:
            todo.append({"id": rid[-8:], "kind": r["kind"], "conflict": len(verdicts) == 2, "sig": list(sig)[:9]})
    json.dump({"carried": carried, "to_judge": todo}, open(out, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    print(source, "active", len(carried) + len(todo), "carried", len(carried), "to judge", len(todo),
          "incorrect carried", sum(not v[0] for v in carried.values()))


main()
