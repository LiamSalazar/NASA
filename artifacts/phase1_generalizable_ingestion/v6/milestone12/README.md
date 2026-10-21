# Phase 1 v6, milestone 12: printed structure settles a specimen line, a series' class and an unknown study

**Status: `PHASE1_COMPLETE=NO`.** The §13 gate is not met and the holdout has not been acquired.

Diego approved these three corrections on 2026-10-21 ("sí sigue con todo"). They come from the round 1 / round 2 variation of milestone 11's evaluation B. One commit each, all general: no source, material, value or target is named in code.

| Commit | Mechanism | Class (addendum §2) | Motivated by |
| --- | --- | --- | --- |
| `09fc2b8` | The "tested at" specimen reader skips a printed line only when a proposed specimen or group names part of it, or a proposed material heads it ("Alpha seals" are Alpha's). Before, it also skipped when the material came later in the line. A material printed later ("… sewn to outer jacket fabric") is a constituent and no longer hides the specimen. The check also runs on the printed line before a continued line is joined, so a bullet heading is never joined into a specimen headed by a material. | document structure | textiles, milestone 11 r1: the model proposed the material "outer jacket fabric", and the reader then skipped "Custom fire-resistant patches sewn to outer jacket fabric" |
| `1d520b4` | A proposed `ExperimentalRun` whose printed name is the plural of a test unit ("… Tests", "… Test Series", "… Runs", "… Trials") is a group of runs. It is revalidated as an `ExperimentFamily` under its printed name, recorded in `class_recovery`, with no model vote. A singular name ("Run 3") or a name the document does not print keeps its class. | document structure | regulator, milestone 11 r1: the three test series proposed as runs, with figure-caption names, and held (`ENTITY_TYPE_SOURCE_ROLE_UNRESOLVED`) |
| `17b953f` | Two proposals of the same `entity_id` and class, one with study `unknown` and one `current`, are one entity, and the proposal with a known study owns it. A `cited` proposal stays separate. | document structure (consolidation) | ignition: "1-g"/"normal gravity" and "microgravity" proposed twice, unknown and current |

Notes:
- PMMA `unknown` and PMMA `current` resolve to two different `entity_id`s, so they are not merged. The rule needs the same entity.
- The first version of `09fc2b8` checked only the joined name. On the v4 textiles package it joined the bullet heading "Fire-resistant patches" onto the line "100% PBI knit fabric coupons tested at 48% O2 …", creating a false specimen that would have carried the coupons' settings. It was caught in replay before commit, and the line check and a negative test were added.

## Tests

| File | Metamorphic | Negative |
| --- | --- | --- |
| `tests/test_tested_at_specimen_lines.py` | two constituent materials | a material heading the line; a proposed specimen; a joined bullet heading |
| `tests/test_series_class_by_structure.py` | caption series name and "Test Series" | "Run 3"; an unprinted name |
| `tests/test_unknown_study_duplicates.py` | | a cited proposal stays separate |

All three fail on `8e3f4e7` except the negatives, which already held.

## Effect (offline replay, 0 model calls; 38 inputs)

Inputs:
- the 5 exposed v4 packages;
- the 2 PTFE runs with historical negatives;
- the 12 reviewed PTFE runs;
- the 3 milestone 7 development runs;
- the 4 milestone 9 B runs;
- the 4 milestone 10 r1 runs;
- the 8 milestone 11 B runs.

| Input | Change against milestone 11 code |
| --- | --- |
| milestone 11 regulator r1 | +3 groups and their impact times (~360, 137–148, 46–49 msec): entities-04/05/06 and quantities-11/13/14. Recall **10/32 → 16/32** |
| milestone 11 textiles r1 | + patch specimen with 37 % and 8.2 psia: entities-04 and quantities-14/15. Recall **7/29 → 10/29** |
| ignition (v4, development, milestone 9 B, milestone 10 r1, milestone 11 r2) | the `unknown` "normal gravity" proposal merged into the current 1-g |
| LUCI (exposed) | an `unknown` "SIBAL fabric" proposal merged into the current one |
| PTFE, 12 runs, B and milestone 11 r1/r2 | no change |
| everything else | no change |

No frozen target is lost on any input. The 29 historical negatives: 0 critical regressions, 1 known non-critical (`rescored_1fe6596/`).

## Evaluation B at frozen code `0a5a860` (two predetermined rounds, all runs reported)

Each run was launched as a process detached from the session, with its own log, so a lost connection could not stop it. Round 1 ran one source at a time. Round 2 ran two at a time (textiles with regulator, ignition with PTFE); no HTTP 429 appeared. Budget 3,600 s, 0 approvals. Judgments are in `evaluation_b.json`.

| Run | Calls / time | Recall | Precision | Critical | Provider |
| --- | --- | --- | --- | --- | --- |
| textiles r1 | 4 / 183 s | 10/29 | 18/22 = 0.818 | 0 | none |
| textiles r2 | 5 / 475 s | 10/29 | 19/25 = 0.760 | 0 | one deadline, answered by the fallback |
| regulator r1 | 17 / 1,800 s | 14/32 | 45/65 = 0.692 | 0 | 3 × HTTP 500, PARTIAL_SCHEMA splits; the fallback answered 3 windows |
| regulator r2 | 10 / 656 s | 17/32 | 55/70 = 0.786 | 0 | none |
| ignition r1 | 19 / 1,788 s | 11/29 | 95/131 = 0.725 | 0 | none |
| ignition r2 | 17 / 1,960 s | 14/29 | 81/101 = 0.802 | 0 | 2 × HTTP 500 and one deadline; the fallback answered 1 window |
| PTFE r1 | 14 / 1,635 s | 27/34 | 96/104 = 0.923 | 0 | one deadline and 2 × HTTP 500; the fallback answered 1 window |
| PTFE r2 | 17 / 2,861 s | 28/34 | 128/129 = 0.992 | 0 | deadlines on the primary and the fallback, then recovered; the fallback answered 2 windows |

No window was lost in any of the eight runs.

## B across milestones 9 to 12 (frozen v4 targets)

| Source | M9 B | M10 r1 | M11 r1 / r2 | M12 r1 / r2 | A at this code |
| --- | --- | --- | --- | --- | --- |
| Lunar ignition | 12/29 | 14/29 | 13 / 13 | 11 / 14 | 14/29 |
| Oxygen regulator | 12/32 | 16/32 | 10 / 14 | 14 / 17 | 19/32 |
| Textiles | 10/29 | 11/29 | 7 / 10 | 10 / 10 | 11/29 |
| PTFE | 23/34 | 28/34 | 25 / 28 | 27 / 28 | 27–28/34 |

## Variability between r1 and r2

| Source | Reached in both | Only r1 | Only r2 | Cause |
| --- | --- | --- | --- | --- |
| Textiles | 10 | none | none | stable: the specimen and its settings come from printed structure in both rounds |
| Regulator | 13 | statements-21 | statements-20/24/25/28 | model generation: statements' roles and subjects. The groups and their times are reached in both rounds. |
| Ignition | 11 | none | quantities-06, quantities-15, statements-22 | model generation: in r1 the model spent its proposals on theory-section concepts ("extinction", "heat transfer limit") and did not propose the WSTF 57 kPa or the GRC slow flow as group configurations |
| PTFE | 27 | none | one | model generation |

Milestone 12's effect is visible:
- Regulator groups and textiles specimens no longer vary between rounds.
- The remaining variation is in statements' roles and in which quantities the model proposes.

## Model proposals versus printed-structure candidates (accepted / proposed)

| Run | Entities | Quantities | Relations | Statements |
| --- | --- | --- | --- | --- |
| textiles r1 / r2 | model 4/8, 4/8 | model 0/9, 0/15; candidates 4/4, 4/4 | model 1/4, 0/2; candidates 0/2, 1/3 | model 13/56, 16/55 |
| regulator r1 / r2 | model 9/15, 14/21 | model 4/180, 5/65; candidates 1/1, 1/1 | model 0/9, 0/13; candidates 1/1, 1/1 | model 50/499, 49/144 |
| ignition r1 / r2 | model 49/82, 23/51 | model 4/159, 7/86; candidates 3/3, 4/4 | model 1/20, 2/25; candidates 2/6, 1/10 | model 72/249, 64/264 |
| PTFE r1 / r2 | model 16/36, 16/21; candidates 3/3, 3/4 | model 3/46, 38/218; candidates 25/28, 17/20 | model 7/26, 10/24; candidates 7/7, 5/5 | model 43/149, 40/195 |

## Gate (§13)

§13 asks for recall ≥ 0.80, stable across several sources, precision ≥ 0.95 and 0 critical errors. It is **not met**.
- Recall in B is 0.34–0.53 on the three other development sources and 0.79–0.82 on PTFE.
- Precision is 0.69–0.99.
- Critical errors: 0 in all eight runs.

`PHASE1_COMPLETE=NO`; the holdout stays unacquired.
