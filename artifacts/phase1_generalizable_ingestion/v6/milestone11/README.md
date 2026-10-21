# Phase 1 v6, milestone 11: the two critical paths found in evaluation B, closed

**Status: `PHASE1_COMPLETE=NO`.** The §13 gate is not met and the holdout has not been acquired.

Evaluation B of milestone 10 (round 1, frozen code `96a2fa2`) found two critical errors. Neither came from a milestone 10 mechanism. Diego asked to close both paths before rerunning (2026-10-21). One commit per mechanism; all three are general.

| Commit | Mechanism | Class (addendum §2) | Motivated by |
| --- | --- | --- | --- |
| `d3cb50b` | A quantity is never given to a condition or intervention unless it is that condition's own printed magnitude: the same name ("vehicle rotation" of 2 RPM), or the value printed in its label ("10 cm/s primer flow"). Only the association is rejected (`QUANTITY_SUBJECT_IS_A_CONDITION`). The existing full revalidation then tries every other subject. If none fits, the value is kept held without a subject (mandate §4). | general scientific | regulator: "nominal operating pressure ~200 psia" given to the condition "3750 psia supply pressure" |
| `c32e88d` | "N% lower/higher/greater/less/more/above/below/faster/slower in <quantity> (than …)" is a printed difference, held as `RELATIVE_DIFFERENCE_IS_A_DERIVED_QUANTITY`, never an absolute value of the quantity. Before, only "N% lower than" was read. | general scientific (dimensional/semantic) | ignition: "occurred 1% lower in oxygen concentration than a case where it did not" accepted as "oxygen concentration 1 %" |
| `6fc2e44` | Two entity proposals that resolve to the same `entity_id` with the same class and study are one entity. Later ones are marked `duplicate_of`; references are unchanged because the entity is the same. | document structure (consolidation) | ignition: "Polycarbonate"/"polycarbonate", "Nomex Velcro" ×2, "Cotton T-Shirt material (Beefy-T)" ×2 |

The duplicate rule was implemented under Diego's general permission for general corrections. Proposals that differ in study, the same name typed `unknown` and `current` ("1-g", "microgravity", "PMMA"), are **not** merged: they are only audited. Neither is an ExperimentFamily with another label ("1-g buoyant flow testing" beside the WSTF group). Merging those would need a decision on which study is right.

Contract kept: an existing test (`test_saved_source_quantity_can_traverse_staged_production_pipeline`) gives a condition its own value ("vehicle rotation" of N RPM). The first mechanism therefore allows a condition its own printed magnitude, and nothing else.

## Tests

`tests/test_quantity_subject_guards.py`. Before these commits the tests for the difference rule and the duplicate rule fail; so does the condition test with the regulator wording.
- **Metamorphic:** two wordings and numbers for the condition case; "lower … than", "higher … than" and "lower in …" with no "than" for the difference.
- **Negative:** a condition with its own printed magnitude stays allowed; an absolute value with a comparison elsewhere in the sentence is not a difference; the same entity name with another study stays separate.

## Effect (offline replay, 0 model calls)

Inputs:
- the 5 exposed v4 packages;
- the 2 PTFE runs with historical negatives;
- the 12 reviewed PTFE runs;
- the 3 milestone 7 development runs;
- the 4 evaluation B runs of milestone 9;
- the 3 finished milestone 10 round 1 runs.

| Input | Change |
| --- | --- |
| milestone 10 regulator r1 | the critical "~200 psia" record leaves (held) |
| milestone 10 ignition r1 | the critical "1 %" record leaves (held); 4 duplicate entity proposals merged |
| milestone 9 B ignition, development ignition, v4 ignition, LUCI | duplicate entity proposals merged (same entity_id, class and study) |
| PTFE, 12 runs and B | no change: 27–28/34, precision ≥ 0.981, 0 critical |
| everything else | no change |

No frozen target is lost on any input. The 29 historical negatives: 0 critical regressions, 1 known non-critical (`rescored_6fc2e44/`).

Precision of the milestone 10 round 1 runs, re-read at this code with the same per-record judgments:

| Source | Milestone 10 | Milestone 11 |
| --- | --- | --- |
| Regulator | 44/59 = 0.746, 1 critical | 44/58 = 0.759, 0 critical |
| Ignition | 84/117 = 0.718, 1 critical | 82/111 = 0.739, 0 critical |
| Textiles | 21/24 = 0.875 | 21/24 = 0.875 |
