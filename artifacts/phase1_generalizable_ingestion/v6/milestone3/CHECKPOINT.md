# Phase 1 v6 checkpoint after milestone 3 (`diego/research`)

**PHASE1_COMPLETE=NO.** Resume from here.

## Code state

- Code commits after milestone 2: `05e689e`, `a798003`, `aff5039`, `2adc6e8` (author Diegomed11). `main` untouched at `54445d0`.
- Quality at `2adc6e8`: `ruff format --check`, `ruff check`, `pytest` pass (671 tests).

## Measured at `2adc6e8` (36 frozen PTFE targets, 34 accessible; exposed development source only)

| Run | Recall | Precision | Critical |
| --- | --- | --- | ---: |
| 1 | 23/34 = 0.68 | 91/92 | 0 |
| 2 | 24/34 = 0.71 | 82/83 | 0 |
| 4 | 19/34 = 0.56 | 68/69 | 0 |
| 5 | 17/34 = 0.50 | 69/72 | 0 |
| 6 | 21/34 = 0.62 | 78/81 | 0 |
| 7 | 18/34 = 0.53 | 64/67 | 0 |

Every accessible target except 18, 31 and 33 is correct in at least one run.
Recall per run stays below 0.80 because each run recovers a different subset
of them.

## Next concrete action

1. **Stability.**
   - The 1,800 s deadline cut run 7's quantity recovery. Measure a live run whose deadline covers every recovery stage (for example 3,600 s; the free endpoint has no monetary limit per Liam's mandate §11).
   - Order the work so the focused recovery comes before the whole-window relationship stage, whose output the structure candidates now largely replace.
2. **Remaining omissions.**
   - Salox-M® composition (18): the printed name is "composition" and the components are Bronze and PTFE.
   - Salox-M® filler relation (33) and the Investigation-to-specimen relation (31): no approved relation fits the printed "uses Bronze filler", so this needs a staged relation proposal, not an activated one.
3. **Holdout.** Not until §12 readiness: recall on the exposed corpus must reach 0.80 in a typical run, not only across runs.
