"""Bounded minimal linguistic proposals resolved against explicit registry authority."""

import re

from pydantic import BaseModel, ConfigDict

from nasa_fire_ai.query.v2 import (
    ComparisonV2,
    EntityConstraintV2,
    GenericValue,
    PropertyConstraintV2,
    QueryIntentV2,
)


class PropertyMention(BaseModel):
    model_config = ConfigDict(extra="forbid")
    label: str
    expression: str


class MinimalInterpretationV2(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation: str = "search"
    targets: list[str] = []
    entities: list[str] = []
    properties: list[PropertyMention] = []
    requested_information: list[str] = []
    comparison_operands: list[str] = []
    sources: list[str] = []
    unknown: list[str] = []
    ambiguous: list[str] = []
    conversation_reference: str | None = None


PROMPT_VERSION = "phase3c-minimal-v1"
SYSTEM_PROMPT = """Interpret the user's linguistic query. Return JSON only with these keys:
operation (search/compare/explain), targets (raw class mentions), entities (raw mentions),
properties (list of {label: raw property mention, expression: original numeric/categorical expression}),
requested_information (raw mentions), comparison_operands (raw mentions), sources (raw source IDs),
unknown (unrecognized terms), ambiguous (ambiguous terms), conversation_reference (string or null).
Do not invent canonical ontology IDs, perform unit conversions, or add scientific constraints.
Preserve numbers, units, inequalities, ranges, approximate wording and explicit +/- tolerance.
Bare flow/velocity and acrylic require ambiguity preservation. Airflow velocity is distinct from
flame-spread velocity. An unknown concept must remain unknown. No prose or additional keys."""


def parse_expression(expression, datatype, operators):
    if datatype == "categorical":
        return "EQ", GenericValue(reported_value=expression, raw_expression=expression)
    text = expression.strip().lower()
    nums = re.findall(r"[-+]?\d+(?:\.\d+)?", text)
    unit_match = re.search(r"cm/s|mm/s|m/s|kpa|pa|fraction|%|\bk\b|\bs\b|\bw\b|\bm\b", text)
    unit = unit_match.group(0) if unit_match else None
    if not nums:
        raise ValueError("numeric expression has no value")
    value = GenericValue(
        reported_value=float(nums[0]), reported_unit=unit, raw_expression=expression
    )
    if "between" in text or (len(nums) == 2 and re.search(r"\d\s*[-–]\s*\d", text)):
        if len(nums) != 2:
            raise ValueError("range requires two values")
        value.reported_value = None
        value.lower, value.upper = map(float, nums)
        return "BETWEEN", value
    if any(x in text for x in ("about", "roughly", "approximately", "±", "+/-")):
        value.approximate = True
        if "±" in text or "+/-" in text:
            if len(nums) != 2:
                raise ValueError("tolerance requires two values")
            value.tolerance = float(nums[1])
        return "APPROX", value
    for mention in sorted(operators, key=len, reverse=True):
        if mention in text:
            return operators[mention], value
    return "EQ", value


def resolve_minimal(proposal, registry, language, context=None):
    unresolved = list(proposal.unknown)
    ambiguous = list(proposal.ambiguous)
    entities = []
    for mention in proposal.entities:
        matches = [
            (eid, meta)
            for eid, meta in language["entity_mentions"].items()
            if mention.lower() in {eid.lower(), *(a.lower() for a in meta["aliases"])}
        ]
        if len(matches) == 1 and matches[0][0] in registry.entities:
            entities.append(
                EntityConstraintV2(relation=matches[0][1]["relation"], entity_id=matches[0][0])
            )
        else:
            unresolved.append(mention)
    properties = []
    for mention in proposal.properties:
        status, pid = registry.resolve_property(mention.label)
        if status != "CANONICAL":
            (ambiguous if status == "AMBIGUOUS" else unresolved).append(mention.label)
            continue
        try:
            operator, value = parse_expression(
                mention.expression, registry.properties[pid].datatype, language["operators"]
            )
            c = PropertyConstraintV2(property_id=pid, operator=operator, value=value)
            registry.validate(c)
            properties.append(c)
        except ValueError:
            unresolved.append(mention.expression)
    information = []
    for mention in proposal.requested_information:
        matches = [
            cid
            for cid, aliases in language["information_mentions"].items()
            if mention.lower() in {cid.lower(), *(a.lower() for a in aliases)}
        ]
        if len(matches) == 1:
            information.extend(matches)
        else:
            unresolved.append(mention)
    targets = []
    for mention in proposal.targets:
        matches = [cid for cid in registry.target_classes if cid.lower() == mention.lower()]
        matches += [
            cid
            for cid, aliases in language["information_mentions"].items()
            if cid in registry.target_classes and mention.lower() in {a.lower() for a in aliases}
        ]
        if matches:
            targets.append(matches[0])
        else:
            unresolved.append(mention)
    operands = []
    for mention in proposal.comparison_operands:
        matches = [
            eid
            for eid in registry.entities
            if eid.lower() == mention.lower() or eid.lower().endswith("-" + mention.lower())
        ]
        if len(matches) == 1:
            operands.extend(matches)
        else:
            unresolved.append(mention)
    if proposal.conversation_reference and context and context.current_investigation:
        entities.append(
            EntityConstraintV2(
                relation="belongsToInvestigation", entity_id=context.current_investigation
            )
        )
    return QueryIntentV2(
        operation={"search": "SEARCH", "compare": "COMPARE", "explain": "EXPLAIN"}.get(
            proposal.operation.lower(), "SEARCH"
        ),
        targets=list(dict.fromkeys(targets)),
        entity_constraints=entities,
        property_constraints=properties,
        requested_information=list(dict.fromkeys(information)),
        comparison=ComparisonV2(operands=operands) if len(operands) >= 2 else None,
        source_constraints=proposal.sources,
        unresolved_mentions=list(dict.fromkeys(unresolved)),
        ambiguities=list(dict.fromkeys(ambiguous)),
        clarification_required=bool(ambiguous),
        conversation_reference=proposal.conversation_reference,
    )
