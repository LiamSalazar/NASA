"""Runtime entry point for isolated scientific preparation and authorized test review."""

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from nasa_fire_ai.evidence import EvidenceRegistry
from nasa_fire_ai.services.curation import CurationService, ReviewPolicy


def initialize_workspace(destination):
    destination = Path(destination).resolve()
    if destination == ROOT:
        raise ValueError("Development workspace must be isolated from the repository")
    destination.mkdir(parents=True, exist_ok=True)
    for name in ("domain", "ontology", "data/canonical"):
        target = destination / name
        if not target.exists():
            shutil.copytree(ROOT / name, target)
    return destination


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    commands = parser.add_subparsers(dest="action", required=True)
    commands.add_parser("initialize")
    submit = commands.add_parser("submit")
    submit.add_argument("--title", required=True)
    submit.add_argument("--purpose", required=True)
    submit.add_argument("files", nargs="+", type=Path)
    status = commands.add_parser("status")
    status.add_argument("package_id")
    args = parser.parse_args()
    workspace = initialize_workspace(args.workspace)
    if args.action == "initialize":
        print(json.dumps({"workspace": str(workspace), "approval": "isolated development only"}))
        return
    registry = EvidenceRegistry(workspace / "data/index/evidence.sqlite")
    service = CurationService(
        workspace, registry, ReviewPolicy(frozenset({"development-scientist"}), True)
    )
    if args.action == "submit":
        result = service.submit(
            args.title,
            args.purpose,
            [(p.name, p.read_bytes()) for p in args.files],
            "development-scientist",
        )
    else:
        result = service.validate(service.get(args.package_id)["package"])
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
