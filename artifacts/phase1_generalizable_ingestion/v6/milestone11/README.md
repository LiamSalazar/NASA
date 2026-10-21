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

## Evaluation B at frozen code `8e3f4e7` (two predetermined rounds, all runs reported)

Round 1 ran one source at a time. Round 2 ran two sources at a time (textiles with regulator, ignition with PTFE); running in parallel is a possible cause of variation under the addendum. No HTTP 429 appeared, so the runs stayed paired. Budget 3,600 s per run, 0 approvals. Per-target and per-record judgments are in `evaluation_b.json`.

| Run | Calls / time | Recall | Precision | Critical | Provider |
| --- | --- | --- | --- | --- | --- |
| textiles r1 | 4 / 172 s | 7/29 | 21/23 = 0.913 | 0 | none |
| textiles r2 | 4 / 138 s | 10/29 | 18/24 = 0.750 | 0 | none |
| regulator r1 | 9 / 712 s | 10/32 | 57/73 = 0.781 | 0 | none |
| regulator r2 | 8 / 437 s | 14/32 | 38/55 = 0.691 | 0 | none |
| ignition r1 | 23 / 3,078 s | 13/29 | 85/112 = 0.759 | 0 | 4 × HTTP 500 and 3 deadlines; 3 windows answered by the fallback; 0 lost |
| ignition r2 | 19 / 1,890 s | 13/29 | 86/111 = 0.775 | 0 | none |
| PTFE r1 | 10 / 5,423 s | 25/34 | 105/106 = 0.991 | 0 | chained 600 s deadlines on the primary and the fallback; window pp. 9–12/18 **lost** |
| PTFE r2 | 12 / 789 s | 28/34 | 114/115 = 0.991 | 0 | one HTTP 500, recovered |

About PTFE r1:
- It overlapped a Remote Control disconnection (08:10 UTC). The PC did not sleep, and the run completed with full receipts, so it counts as a predetermined run, with cause "provider".
- An extra PTFE run started afterwards (`ptfe_live_8e3f4e7_r1b/`), detached from the session. It is reported separately below and does not replace r1.

## Evaluation A next to B (frozen v4 targets)

A is the milestone 7 outputs replayed at this code.

| Source | A | B r1 | B r2 |
| --- | --- | --- | --- |
| Lunar ignition | 14/29 | 13/29 | 13/29 |
| Oxygen regulator | 19/32 | 10/32 | 14/32 |
| Textiles | 11/29 | 7/29 | 10/29 |
| PTFE | 27–28/34 (12 runs) | 25/34 | 28/34 |

## Variability between r1 and r2

| Source | Reached in both | Only r1 | Only r2 | Cause |
| --- | --- | --- | --- | --- |
| Ignition | 12 | statements-25 | statements-22 | model generation: the role of two tentative statements |
| Regulator | 8 | statements-23, statements-25 | entities-04/05/06, quantities-11/13/14 | model generation: the class and name of the three test series (runs with figure-caption names in r1, held; groups with heading names in r2). In r1 the statements were proposed with a subject. |
| Textiles | 7 | none | entities-04, quantities-14/15 | model generation plus candidate inventory: the patch specimen was not proposed in r1, and the "tested at" reader skipped it because of the material "outer jacket fabric" |
| PTFE | 25 | none | statements of the lost window | provider (r1 lost a window) |

By category: entities and quantities vary only through the class or name the model gives a group or specimen. Statements vary in role or subject.

## What the model proposed versus what printed-structure candidates added (accepted / proposed)

| Run | Entities | Quantities | Relations | Statements |
| --- | --- | --- | --- | --- |
| textiles r1 / r2 | model 8/18, 4/11 | model 1/20, 0/13; candidates 1/1, 4/4 | model 1/4, 1/3; candidates 0/1, 0/6 | model 12/45, 15/55 |
| regulator r1 / r2 | model 10/17, 14/17 | model 2/96, 4/44; candidates 1/1, 1/1 | model 0/5, 0/14; candidates 1/1, 1/1 | model 59/258, 35/186 |
| ignition r1 / r2 | model 31/59, 29/54 | model 8/163, 5/114; candidates 4/5, 4/5 | model 3/28, 1/23; candidates 2/7, 1/5 | model 64/287, 71/302 |
| PTFE r1 / r2 | model 21/58, 15/21; candidates 3/3, 3/4 | model 2/41, 11/33; candidates 33/41, 24/27 | model 0/0, 6/10; candidates 26/26, 8/8 | model 21/176, 48/157 |

Reading:
- 0 critical errors in all eight runs. The two critical paths found in milestone 10 did not recur.
- The model's quantity proposals still rarely pass. Accepted quantities come mostly from printed-structure candidates.
- The largest run-to-run losses are classes and names the model gives to groups and specimens. Milestone 12 addresses these with printed structure, by Diego's decision.

## Extra PTFE run (`ptfe_live_8e3f4e7_r1b/`)

This run was made after round 2, detached from the session, at the same frozen code. It is reported and does not replace r1.
- 13 calls / 2,866 s.
- One 600 s deadline, answered by the fallback; 0 windows lost.
- **27/34**, precision 118/121 = 0.975, 0 critical (official scorer).
