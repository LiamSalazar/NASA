"""Run one already-exposed NASA source live through the ordinary curation services.

Development/regression only. The source must already be exposed (its frozen
evaluation is finished), so this run is never an independent evaluation. The
driver performs no extraction, mapping, JSON correction or approval itself: it
submits the verified original with its official acquisition provenance, then
calls CurationService.prepare_scientific with the configured NVIDIA models, and
records the outputs. Receipts are written to a new exclusive directory; the
SQLite workspace and the original PDF copy stay outside the repository.

Example (Linux or Windows):
    uv run python scripts/phase1_exposed_live_run.py \
        --pdf /path/20090043050.pdf \
        --provenance-from artifacts/phase1_generalizable_ingestion/v4/independent_ptfe/submission.json \
        --workspace /tmp/nasa-ptfe-live --directory artifacts/.../ptfe_live_<commit> \
        --timeout-seconds 1800
"""

import argparse
import gzip
import hashlib
import json
import re
import shutil
import subprocess
import sys
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from nasa_fire_ai.config import Settings  # noqa: E402
from nasa_fire_ai.evidence import EvidenceRegistry  # noqa: E402
from nasa_fire_ai.ingestion.document_extraction import ExtractionBudget  # noqa: E402
from nasa_fire_ai.ingestion.extraction_resources import ProviderEnvelope  # noqa: E402
from nasa_fire_ai.services.curation import CurationService  # noqa: E402

CREDENTIAL = re.compile(r"nvapi-[A-Za-z0-9_\-]{8,}")


def load(path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def write(path, value):
    text = json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if CREDENTIAL.search(text):
        raise RuntimeError("Refusing to write a receipt containing a credential")
    if path.suffix == ".gz":
        with gzip.open(path, "xt", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
    else:
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(text)


def git(*args):
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=False
    ).stdout.strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--provenance-from", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=float)
    parser.add_argument("--max-model-calls", type=int)
    parser.add_argument("--request-timeout-seconds", type=float)
    args = parser.parse_args()

    out = args.directory if args.directory.is_absolute() else ROOT / args.directory
    workspace = args.workspace.resolve()
    if ROOT in [workspace, *workspace.parents]:
        raise ValueError("The workspace must be outside the repository")
    reference = load(args.provenance_from)["package"]
    data = args.pdf.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    expected = {i["sha256"] for i in reference["inputs"]}
    if sha not in expected:
        raise ValueError("Original PDF does not match the recorded official source hash")
    out.mkdir(parents=True, exist_ok=False)
    for name in ("domain", "ontology", "data/canonical"):
        if not (workspace / name).exists():
            shutil.copytree(ROOT / name, workspace / name)

    settings = Settings(root=workspace)
    if not settings.nvidia_api_key:
        raise RuntimeError("NVIDIA_API_KEY is not configured")
    registry = EvidenceRegistry(workspace / "data/index/evidence.sqlite")
    service = CurationService(workspace, registry)
    started = datetime.now(UTC).isoformat()
    try:
        submission = service.submit(
            reference["title"],
            reference["purpose"],
            [(reference["inputs"][0]["name"], data)],
            reference["creator"],
        )
        # Official acquisition provenance only; never a scientific mapping.
        submission["package"]["source_provenance"] = reference.get("source_provenance")
        submission = service.save(submission["package"], reference["creator"])
        package_id = submission["package"]["id"]
        before = {
            r[0]
            for r in registry.db.execute(
                "SELECT cache_key FROM phase3_cache WHERE cache_kind='scientific_document_attempt'"
            )
        }
        prepared = service.prepare_scientific(
            package_id,
            settings,
            model_enabled=True,
            budget=ExtractionBudget(
                max_model_calls=args.max_model_calls,
                timeout_seconds=args.timeout_seconds,
                call_timeout_seconds=args.request_timeout_seconds,
            ),
        )
        attempts = [
            {"cache_key": r[0], **json.loads(r[1])}
            for r in registry.db.execute(
                "SELECT cache_key,payload_json FROM phase3_cache "
                "WHERE cache_kind='scientific_document_attempt'"
            )
            if r[0] not in before
        ]
        completed = datetime.now(UTC).isoformat()
        validation = service.validate(prepared["package"])
        summary = {
            "kind": "PHASE1_EXPOSED_SOURCE_LIVE_RUN",
            "membership": "EXPOSED_DEVELOPMENT_REGRESSION_ONLY",
            "git_head": git("rev-parse", "HEAD"),
            "uncommitted_src_changes": bool(git("status", "--porcelain", "--", "src")),
            "started_at": started,
            "completed_at": completed,
            "package_id": package_id,
            "source_sha256": sha,
            "official_url": (reference.get("source_provenance") or {}).get("source_url"),
            "configuration": {
                "model": settings.scientific_model,
                "fallback_models": list(settings.nvidia_science_fallback_models),
                "vision_model": settings.nvidia_science_vision_model,
                "endpoint": settings.nvidia_base_url or "https://integrate.api.nvidia.com/v1",
                "provider_envelope": asdict(ProviderEnvelope()),
                "timeout_seconds": args.timeout_seconds,
                "max_model_calls": args.max_model_calls,
            },
            "digest": prepared["digest"],
            "processing": prepared["processing"],
            "attempts": len(attempts),
            "validation_errors": validation.get("errors", []),
            "source_integrity_errors": service.validate_originals(prepared["package"]),
            "approvals": registry.db.execute("SELECT count(*) FROM research_approvals").fetchone()[
                0
            ],
            "publications": registry.db.execute("SELECT count(*) FROM research_active").fetchone()[
                0
            ],
            "sqlite_integrity": registry.db.execute("PRAGMA integrity_check").fetchone()[0],
            "scientific_acceptance": "NOT_ESTABLISHED_BY_RUN",
        }
        write(out / "submission.json", submission)
        write(out / "attempts.json.gz", {"attempts": attempts})
        write(out / "prepared.json.gz", prepared)
        write(out / "validation.json.gz", validation)
        write(out / "summary.json", summary)
        print(json.dumps({k: summary[k] for k in ("package_id", "digest", "attempts")}))
        print(json.dumps(summary["processing"], indent=2)[:4000])
    finally:
        registry.db.close()


if __name__ == "__main__":
    main()
