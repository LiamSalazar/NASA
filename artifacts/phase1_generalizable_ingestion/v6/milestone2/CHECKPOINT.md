# Phase 1 v6 checkpoint after milestone 2 (`diego/research`)

**PHASE1_COMPLETE=NO.** Resume from here.

## Code state

- Code commits after milestone 1: `8bc0d04`, `2a64310`, `b8db2a5`, `0294286`, `17b88c2` (author Diegomed11). `main` untouched at `54445d0`.
- Quality at `17b88c2`: `ruff format --check`, `ruff check`, `pytest` pass (668 tests).

## Measured at `17b88c2` (36 frozen PTFE targets, 34 accessible; exposed development source only)

| Run | Recall | Precision | Critical |
| --- | --- | --- | ---: |
| 1 | 23/34 = 0.68 | 91/92 | 0 |
| 2 | 22/34 = 0.65 | 70/71 | 0 |
| 4 | 18/34 = 0.53 | 64/65 | 0 |
| 5 | 17/34 = 0.50 | 69/72 | 0 |
| 6 | 19/34 = 0.56 | 66/69 | 0 |

LUCI keeps 9 correct staged quantities; ignition, regulator and textiles have
nothing new; 29 historical negatives show 0 critical regressions.

## What blocks recall (by target)

- **Model omissions, run to run:**
  - p4 specimen entity (02);
  - relations 31–34 (run 6 has none);
  - Salox-M® composition (18), whose model labels ("Bronze percentage") are not printed names.
- **Correct holds that strict recall does not count:**
  - 13 when two roles are proposed for one cell;
  - 14, a difference against cited data;
  - 17, batch percentages proposed on the material instead of its batches;
  - 22 recording rule, 24 cited result, 25 printed conflict (can never count), 26 and 28 role review.

## Next concrete action

1. **Relations (work package C).** Run the existing relationship recovery with the
   same narrowing used for quantities: offer only the subjects of omitted
   sentences and the tested materials, then measure with a seventh live run.
2. **Batch-scoped prose values (17).** When a value is followed by "in batch N"
   and a row group of that material carries batch N, revalidate on that group
   (the existing narrowest-subject rule).
3. **Scorer (work package E).** Report "correctly held" targets separately from
   recall, without changing strict recall. Liam's decision B requires this
   separation; target 25 is the case where unresolved is the only correct outcome.
