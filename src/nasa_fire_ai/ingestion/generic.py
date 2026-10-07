"""Source-independent table profiling and semantic staging; never publishes science."""

import re
from dataclasses import dataclass

from nasa_fire_ai.query.v2 import SemanticRegistry


@dataclass(frozen=True)
class ColumnProfile:
    label: str
    normalized_label: str
    raw_unit: str | None
    datatype: str
    nullable: bool
    samples: list[str]


@dataclass(frozen=True)
class SemanticResolution:
    raw_label: str
    status: str
    property_id: str | None
    raw_unit: str | None
    datatype: str


def resolve_column(profile: ColumnProfile, registry: SemanticRegistry) -> SemanticResolution:
    """Registry-only semantic proposal; unknowns deliberately remain unresolved."""
    status, property_id = registry.resolve_property(profile.normalized_label, profile.raw_unit)
    return SemanticResolution(
        profile.label, status, property_id, profile.raw_unit, profile.datatype
    )


def profile_table(rows: list[dict[str, str]], sample_size: int = 5) -> list[ColumnProfile]:
    headers = list(rows[0]) if rows else []
    profiles = []
    for header in headers:
        values = [str(row.get(header, "")).strip() for row in rows]
        nonempty = [x for x in values if x]
        unit = re.search(r"\(([^)]+)\)", header)
        numeric = nonempty and all(re.fullmatch(r"[-+]?\d+(?:\.\d+)?", x) for x in nonempty)
        ranged = nonempty and all(
            re.fullmatch(r"[-+]?\d+(?:\.\d+)?\s*[-–]\s*[-+]?\d+(?:\.\d+)?", x) for x in nonempty
        )
        label_without_unit = re.sub(r"\([^)]*\)", "", header)
        profiles.append(
            ColumnProfile(
                header,
                re.sub(r"[^a-z0-9]+", " ", label_without_unit.lower()).strip(),
                unit.group(1) if unit else None,
                "numeric" if numeric else "range" if ranged else "categorical",
                len(nonempty) != len(values),
                nonempty[:sample_size],
            )
        )
    return profiles
