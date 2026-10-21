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
