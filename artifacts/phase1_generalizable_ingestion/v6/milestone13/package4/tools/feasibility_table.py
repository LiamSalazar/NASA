"""Feasibility table: the blocking class of every frozen target, and the ceiling by source.

    python feasibility_table.py        (repo root; reads feasibility/best_states_raw.json)

The blocking class of each target never correct in a live run is the branch
author's judgment from its frozen expectation and its records, written below.
"""
import json

P = "artifacts/phase1_generalizable_ingestion/v6/milestone13/package4/feasibility"
ROLE, SUBJ, REJ, SCHEMA, CLASH = (
    "wrong role",
    "wrong subject",
    "rejection",
    "schema lacks the role",
    "contract against target",
)
B = {
    "ignition": {
        "quantities-07": (REJ, "QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT", "the dimensions are labelled with the object ('samples'); no dimension name is printed"),
        "quantities-08": (REJ, "QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT", "as quantities-07"),
        "quantities-13": (REJ, "QUANTITY_SEMANTICS_OR_UNIT_UNRESOLVED", "the printed typo 'internal height if 30.5 cm' leaves the value unnamed; the validator is stricter than the expectation"),
        "quantities-16": (ROLE, "", "a cited estimate (Takahashi) proposed as a current reported quantity"),
        "quantities-17": (REJ, "QUANTITY_SEMANTICS_OR_UNIT_UNRESOLVED", "a derived delta with no eligible subject"),
        "statements-18": (REJ, "CHANGING_OBSERVATION_IS_NOT_ESTABLISHED_CONFIGURATION", "the execution step held as a changing observation"),
        "statements-19": (ROLE, "", "test coverage typed documentary context"),
        "statements-20": (ROLE, "", "explicit uncertainty typed a condition or a conclusion"),
        "statements-21": (REJ, "STATEMENT_SUBJECT_APPLICABILITY_UNRESOLVED", "the whole sentence held on three specimen subjects; the accepted record is a cut fragment"),
        "relations-26": (SUBJ, "", "WSTF hasCondition proposed to the primer flow, not the documented chamber configuration"),
        "quantities-28": (REJ, "ORIGINAL_TABLE_QUANTITY_ROLE_AND_EXPERIMENTAL_SCOPE_REQUIRE_REVIEW", "a cited model-input table cell; math-font glyphs also unbind its unit"),
        "quantities-29": (REJ, "ORIGINAL_TABLE_QUANTITY_ROLE_AND_EXPERIMENTAL_SCOPE_REQUIRE_REVIEW", "a derived table cell with its confidence role"),
    },
    "regulator": {
        "quantities-07": (ROLE, "", "a transient model prediction typed a configuration or a measurement"),
        "quantities-09": (REJ, "QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT", "'20uL was injected': unprinted label, and the test article (POR) as subject"),
        "quantities-10": (REJ, "QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT", "'~100 mg/ft2 film coating' as a target loading, on the test article"),
        "quantities-12": (REJ, "TEST_ARTICLE_ALIAS_EXPERIMENTAL_GROUP_SCOPE_REQUIRES_REVIEW", "the deliberate test-article alias hold"),
        "statements-15": (ROLE, "", "a cited partial test typed a current observation"),
        "statements-16": (REJ, "STATEMENT_REQUIRES_EXPERIMENTAL_SCOPE", "the contaminant-selection configuration without a scope"),
        "statements-18": (REJ, "INFERRED_INTERPRETATION_IS_NOT_DIRECT_OBSERVATION", "the post-dry functional result held as an interpretation"),
        "statements-19": (REJ, "STATEMENT_SUBJECT_APPLICABILITY_UNRESOLVED", "a system-only adjustment: false on the POR, right at study scope"),
        "statements-26": (REJ, "STATEMENT_INCLUDES_A_RUNNING_PAGE_HEADER", "the running header glued to the sentence, or the test article as subject"),
        "statements-27": (ROLE, "", "a Thermal Desktop model result typed a measurement or a conclusion"),
    },
    "textiles": {
        "entities-02": (SUBJ, "", "the fabric ('100% PBI knit fabric') proposed instead of the PBI material identity"),
        "quantities-05": (CLASH, "QUANTITY_SUBJECT_NOT_IN_APPLICABLE_SOURCE", "the proposed Artemis atmosphere has no eligible experimental subject"),
        "quantities-06": (CLASH, "QUANTITY_SUBJECT_NOT_IN_APPLICABLE_SOURCE", "as quantities-05"),
        "quantities-07": (CLASH, "QUANTITY_SUBJECT_NOT_IN_APPLICABLE_SOURCE", "as quantities-05"),
        "quantities-08": (SCHEMA, "QUANTITY_SUBJECT_NOT_IN_APPLICABLE_SOURCE", "a historical mission atmosphere (Apollo): no historical-context subject or role"),
        "quantities-09": (SCHEMA, "QUANTITY_SUBJECT_NOT_IN_APPLICABLE_SOURCE", "as quantities-08 (Skylab)"),
        "quantities-10": (SCHEMA, "QUANTITY_UNIT_NOT_BOUND_TO_EXPRESSION", "a normative acceptance criterion value: quantities have no criterion role"),
        "quantities-11": (REJ, "QUANTITY_SEMANTICS_OR_UNIT_UNRESOLVED", "the specimen composition '100% PBI' held unnamed"),
        "quantities-16": (SCHEMA, "QUANTITY_SUBJECT_NOT_IN_APPLICABLE_SOURCE", "an assessment target (design criterion) value"),
        "quantities-17": (SCHEMA, "QUANTITY_SUBJECT_NOT_IN_APPLICABLE_SOURCE", "as quantities-16"),
        "statements-18": (CLASH, "SUPPORT_ONLY_IN_BACKGROUND_OR_ANALYSIS_SECTION", "held on the Background slide"),
        "statements-19": (CLASH, "NORMATIVE_ROLE_NOT_EXPLICIT_IN_SOURCE", "a pass criterion the slide does not print as one"),
        "statements-21": (ROLE, "", "a permitted method typed guidance or configuration"),
        "statements-23": (ROLE, "", "current development activities typed documentary context"),
        "statements-27": (SCHEMA, "", "a stated goal: no goal or plan role"),
    },
}


def main():
    with open(f"{P}/best_states_raw.json", encoding="utf-8") as handle:
        raw = json.load(handle)
    out, summary = {}, []
    lines = [
        "# Feasibility of every frozen target (ignition, regulator, textiles)",
        "",
        "Best state over all graded live runs:",
        "- NVIDIA evaluation B of milestones 10–13;",
        "- the Anthropic pilot (Sonnet and Opus);",
        "- the three package 4 Sonnet rounds.",
        "",
        "Classes come from the corrected `miss_diag` (value spans, table cells, lost windows), and the blocking class of each target never correct is judged from its frozen expectation and records (`../tools/feasibility_table.py`). Replay recoveries (point A, block 3b) are listed apart, since they are not live runs.",
        "",
        "Receipts: `best_states_raw.json` (every run) and `feasibility.json`. 0 model calls.",
        "",
        "Blocking classes: not proposed, wrong role, wrong subject, rejection (with its code), the schema lacks the role, contract against target, window lost.",
        "",
    ]
    for source, v in raw.items():
        rows, counts = [], {}
        for tid, t in v["targets"].items():
            state = t["best_live"]["state"]
            if state == "CORRECT":
                cls, code, note = "reached live", "", f"correct in {len(t['best_live']['runs'])} of {len(v['runs'])} runs"
            elif t["replay_gain"]:
                cls, code, note = "reached in replay", "", t["replay_gain"]
            else:
                cls, code, note = B[source][tid]
            counts[cls] = counts.get(cls, 0) + 1
            rows.append(
                {
                    "target": tid,
                    "kind": t["kind"],
                    "best_live_state": state,
                    "best_runs": t["best_live"]["runs"],
                    "blocking_class": cls,
                    "code": code,
                    "note": note,
                    "expectation": t["expectation"],
                }
            )
        acc = v["accessible"]
        live = counts.get("reached live", 0)
        replay = live + counts.get("reached in replay", 0)
        rule = replay + counts.get(REJ, 0)
        model = rule + counts.get(ROLE, 0) + counts.get(SUBJ, 0) + counts.get("not proposed", 0) + counts.get("window lost", 0)
        liam = counts.get(SCHEMA, 0) + counts.get(CLASH, 0)
        out[source] = {
            "accessible": acc,
            "runs": v["runs"],
            "counts": counts,
            "ceilings": {
                "live_union": live,
                "live_and_replay_union": replay,
                "plus_every_rejection": rule,
                "plus_every_model_side_miss": model,
                "needs_liam": liam,
            },
            "targets": rows,
        }
        summary.append((source, acc, live, replay, rule, model, liam, -(-4 * acc // 5)))
        lines += [
            f"## {source} ({acc} accessible targets, {len(v['runs'])} graded runs)",
            "",
            "| target | kind | best live state | blocking class | code | note |",
            "|---|---|---|---|---|---|",
        ]
        lines += [
            f"| {r['target']} | {r['kind']} | {r['best_live_state']} | {r['blocking_class']} | "
            + (f"`{r['code']}`" if r["code"] else "")
            + f" | {r['note']} |"
            for r in rows
        ]
        lines.append("")
    lines += [
        "## Ceiling by source",
        "",
        "| source | accessible | live union | + replay | + every rejection fixed | + every model-side miss fixed | needs Liam (schema, contract) | needed for 0.80 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for s, acc, a, b, c, d, liam, need in summary:
        lines.append(
            f"| {s} | {acc} | {a} ({a / acc:.2f}) | {b} ({b / acc:.2f}) | {c} ({c / acc:.2f}) | {d} ({d / acc:.2f}) | {liam} | {need} |"
        )
    lines += [
        "",
        "How to read it:",
        "- **Live union** is what some live run reached; no single run reached it.",
        "- **+ every rejection fixed** assumes each held proposal was right as proposed. Several are correct holds by the contracts (see the notes), so it is an upper bound.",
        "- **+ every model-side miss fixed** also assumes the model proposes the right role and subject. Only a request change, measured live, can show that.",
        "- **The rest** needs Liam: roles the schema lacks, and contracts the frozen targets contradict.",
    ]
    with open(f"{P}/feasibility.md", "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines) + "\n")
    with open(f"{P}/feasibility.json", "w", encoding="utf-8", newline="\n") as handle:
        json.dump(out, handle, indent=1, ensure_ascii=False)
        handle.write("\n")
    for row in summary:
        print(row)


main()
