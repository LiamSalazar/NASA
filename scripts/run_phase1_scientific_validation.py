"""Execute ordinary submission/preparation services in a new isolated workspace.

No extraction, JSON correction, scientific mappings or approval live in this driver.
The optional final investigation requires a prospectively frozen v3 contract.
"""

import argparse
import hashlib
import json
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from nasa_fire_ai.config import Settings
from nasa_fire_ai.evidence import EvidenceRegistry
from nasa_fire_ai.ingestion.document_extraction import ExtractionBudget
from nasa_fire_ai.services.curation import CurationService

SOURCES = {
    "luci": ("holdout_first_pass", "20250010653"),
    "bass": ("development_run1", "20150008961"),
    "depress": ("development_run1", "20260003546"),
    "psi": ("development_run1", "PSI-98"),
}


def write(path, value):
    with path.open("x") as f:
        json.dump(value, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", choices=[*SOURCES, "holdout"])
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--timeout-seconds", type=float)
    parser.add_argument("--recover", action="store_true")
    parser.add_argument("--max-model-calls", type=int)
    args = parser.parse_args()
    out = args.directory.resolve()
    if args.source == "holdout":
        freeze = json.loads(
            (
                ROOT / "artifacts/phase1_generalizable_ingestion/v3/final_contract_freeze.json"
            ).read_text()
        )
        for name, sha in freeze["files"].items():
            if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != sha:
                raise ValueError("Final contract changed: " + name)
    out.mkdir(parents=True, exist_ok=args.resume)
    invocation = len(list(out.glob("implementation_*.json"))) + 1
    write(
        out / f"implementation_{invocation}.json",
        {
            str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for directory in ("src", "scripts", "ontology", "domain")
            for p in sorted((ROOT / directory).rglob("*"))
            if p.is_file() and "__pycache__" not in p.parts
        },
    )
    with ZipFile(out / f"implementation_{invocation}.zip", "x", ZIP_DEFLATED) as archive:
        for name in json.loads((out / f"implementation_{invocation}.json").read_text()):
            archive.write(ROOT / name, name)
    started = datetime.now(UTC).isoformat()
    workspace = out / "workspace"
    for name in ("domain", "ontology", "data/canonical"):
        if not (workspace / name).exists():
            shutil.copytree(ROOT / name, workspace / name)
    registry = EvidenceRegistry(workspace / "data/index/evidence.sqlite")
    service = CurationService(workspace, registry)
    settings = Settings(root=workspace)
    if args.resume:
        submission = json.loads((out / "submission.json").read_text())
        version = len(list(out.glob("prepared_*.json"))) + 1
    else:
        if args.source == "holdout":
            submission = service.submit_ntrs("20240006315", "phase1-validation")
        else:
            campaign, identifier = SOURCES[args.source]
            historical = ROOT / "artifacts/phase1_generalizable_ingestion/v1" / campaign
            package = json.loads((historical / (identifier + "_baseline.json")).read_text())[
                "package"
            ]
            originals = [
                (item["name"], (historical / "workspace" / item["stored_input"]).read_bytes())
                for item in package["inputs"]
            ]
            submission = service.submit(
                package["title"], package["purpose"], originals, package["creator"]
            )
            # Preserve official acquisition provenance, never a scientific mapping.
            submission["package"]["source_provenance"] = package.get("source_provenance")
            submission = service.save(submission["package"], package["creator"])
        write(out / "submission.json", submission)
        version = 1
    earlier_attempts = {
        r[0]
        for r in registry.db.execute(
            "SELECT cache_key FROM phase3_cache WHERE cache_kind='scientific_document_attempt'"
        )
    }
    prepared = service.prepare_scientific(
        submission["package"]["id"],
        settings,
        model_enabled=not args.offline,
        budget=ExtractionBudget(
            max_model_calls=args.max_model_calls,
            timeout_seconds=args.timeout_seconds,
            recovery_only=args.recover,
        ),
    )
    attempts = [
        {"cache_key": r[0], **json.loads(r[1])}
        for r in registry.db.execute(
            "SELECT cache_key,payload_json FROM phase3_cache WHERE cache_kind='scientific_document_attempt'"
        )
        if r[0] not in earlier_attempts
    ]
    write(
        out / f"attempts_{version}.json",
        {
            "started_at": started,
            "completed_at": datetime.now(UTC).isoformat(),
            "attempts": attempts,
        },
    )
    write(out / f"prepared_{version}.json", prepared)
    write(out / f"validation_{version}.json", service.validate(prepared["package"]))
    (out / f"package_{version}.zip").write_bytes(
        service.export_package(submission["package"]["id"])
    )
    write(
        out / f"summary_{version}.json",
        {
            "source": args.source,
            "package_id": submission["package"]["id"],
            "digest": prepared["digest"],
            "processing": prepared["processing"],
            "scientific_coverage": prepared["package"]["scientific_extraction"][
                "scientific_coverage"
            ],
            "source_integrity_errors": service.validate_originals(prepared["package"]),
            "approvals": registry.db.execute("SELECT count(*) FROM research_approvals").fetchone()[
                0
            ],
            "publications": registry.db.execute("SELECT count(*) FROM research_active").fetchone()[
                0
            ],
            "sqlite_integrity": registry.db.execute("PRAGMA integrity_check").fetchone()[0],
        },
    )
    print(
        json.dumps(
            {
                "source": args.source,
                "directory": str(out),
                "status": prepared["processing"]["status"],
                "new_model_calls": prepared["processing"]["new_model_calls"],
                "scientific_completeness": prepared["processing"]["scientific_completeness"],
            }
        )
    )
    registry.db.close()


if __name__ == "__main__":
    main()
