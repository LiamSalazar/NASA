"""Free prejudgment of an admissible-subject menu for statements (0 model calls).

    uv run python prejudge_admissible.py OUT.json PREPARED.json.gz [...]   (repo root)

For each saved package: replay it, then for each statement held only because its
proposed subject is not shown to apply to its passage, take the first subject the
passage admits for its role (admissible_statement_subjects) as if the model had picked it
from the menu, revalidate, and list the statements that become SOURCE_SUPPORTED.
Nothing is judged here; the list is for record-by-record adjudication.
"""
import copy, gzip, json, sys, tempfile
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from phase1_offline_replay import replay  # noqa: E402

from nasa_fire_ai.evidence import EvidenceRegistry  # noqa: E402
from nasa_fire_ai.ingestion.document_extraction import (  # noqa: E402
    Output, admissible_statement_subjects, extraction_semantic, locate, merge_output,
    normalized, validate_output,
)
from nasa_fire_ai.services.curation import CurationService  # noqa: E402

HELD = {"STATEMENT_SUBJECT_APPLICABILITY_UNRESOLVED", "STATEMENT_REQUIRES_EXPERIMENTAL_SCOPE"}


def main():
    out, paths = sys.argv[1], sys.argv[2:]
    result = {}
    with tempfile.TemporaryDirectory() as tmp:
        import shutil
        for name in ("domain", "ontology", "data/canonical"):
            shutil.copytree(ROOT / name, Path(tmp) / name)
        registry = EvidenceRegistry(Path(tmp) / "data/index/evidence.sqlite")
        service = CurationService(Path(tmp), registry)
        for path in paths:
            prepared, _ = replay(json.load(gzip.open(path, "rt", encoding="utf-8")), service)
            package = prepared["package"]
            x = package["scientific_extraction"]
            document, entities = x["document"], x["entities_by_key"]
            evidence = {e["evidence_id"]: e for e in package["evidence"]}
            raw = copy.deepcopy(x["raw_proposals"])
            changed = []
            for record in x["records"]:
                if record["kind"] != "statements" or record["status"] == "SOURCE_SUPPORTED":
                    continue
                if not HELD & set(record["reasons"]) or set(record["reasons"]) - HELD:
                    continue  # held for another reason too: a subject alone cannot free it
                spans = record.get("support_spans") or locate(record["proposal"]["support"], evidence)
                menu = admissible_statement_subjects(
                    spans, entities, document, record["proposal"]["epistemic"]
                )
                if not menu:
                    continue
                for item in raw["statements"]:
                    if normalized(item["text"]) == normalized(record["proposal"]["text"]) and (
                        item["epistemic"] == record["proposal"]["epistemic"]
                    ):
                        if item["subjects"] != [menu[0]]:
                            item["subjects"] = [menu[0]]
                            changed.append(record["id"])
            consolidated = Output().model_dump()
            merge_output(consolidated, raw)
            after = validate_output(consolidated, package, document, extraction_semantic(service, package))
            before = {r["id"]: r["status"] for r in x["records"]}
            labels = {k: e["label"] for k, e in after["entities_by_key"].items()}
            freed = [
                {
                    "id": r["id"][-8:],
                    "epistemic": r["proposal"]["epistemic"],
                    "subjects": [labels.get(s, s) for s in r["proposal"].get("subjects", [])],
                    "text": " ".join(r["proposal"]["text"].split())[:300],
                }
                for r in after["records"]
                if r["kind"] == "statements"
                and r["status"] == "SOURCE_SUPPORTED"
                and before.get(r["id"]) != "SOURCE_SUPPORTED"
                and not r.get("duplicate_of")
            ]
            other = sum(
                1
                for r in after["records"]
                if r["kind"] != "statements" and before.get(r["id"]) not in (None, r["status"])
            )
            result[path] = {"menu_applied": len(changed), "freed": freed, "other_kind_status_changes": other}
            print(path.split("/")[-2], "menu applied", len(changed), "freed", len(freed), "other changes", other)
        registry.db.close()
    with open(out, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, indent=1, ensure_ascii=False)
        handle.write("\n")


main()
