# Phase 1 v6, milestone 3: relations from the printed structure, correct holds, seventh live run

**Status: `PHASE1_COMPLETE=NO`.** Relations were the most variable part of the
model output: run 6 had no `madeOf`, and every run held the batch conditions.
Table 3 prints both: each batch group under its material's name, and its LOX/GOX
rows. This milestone turns that printed structure into validated relation
candidates. The scorer now reports correct holds separately from recall, and a
seventh live run measures the result. Recall on the exposed PTFE source is
0.50–0.71 by run, precision 0.96–0.99, 0 critical errors. No holdout was consumed.

## Code (`diego/research`, main untouched at `54445d0`)

| Commit | Change |
| --- | --- |
| `05e689e` | Structure relation candidates, validated like model proposals and marked `candidate_origin=PRINTED_SOURCE_STRUCTURE`: a group printed as "<material> (qualifier)" `madeOf` that material; a group whose own rows print a condition `hasCondition` it (same study only). `hasCondition` is supported when the subject's own row group, with no cited lineage, prints exactly that condition (`SUBJECT_TABLE_ROWS_PRINT_CONDITION`). |
| `a798003` | Scorer: an unresolved target may carry `hold_assessment: HOLD_IS_THE_CORRECT_OUTCOME` with a source rationale; such targets are listed under `correctly_held_targets` with `counts_as_recall: false`. Strict recall, retention and denominators are unchanged. |
| `aff5039` | An instrument or test-method noun typed as an Intervention is held (`APPARATUS_OR_METHOD_IS_NOT_AN_INTERVENTION`); a label that is a value in an interpreted unit is held as `NUMERIC_VALUE_IS_NOT_A_NAMED_ENTITY`. |
| `2adc6e8` | The value-label hold applies only when nothing but "of <quantity>" or a parenthetical equivalent follows the value ("98 Joules of energy (72 ft-lbs)"), never to names such as "100% PBI knit fabric", "0.8 mm PMMA Sample" or "37% O2 at 8.2 psia". |

Quality at `2adc6e8`: `ruff format --check`, `ruff check`, `pytest` pass (671 tests).

## Seventh live run (`ptfe_live_a798003/`)

12 model calls, 1,878 s, `PARTIAL_MODEL_COVERAGE`, 0 approvals, 0 publications, SQLite `ok`. The deadline deferred the focused quantity recovery (`DEFERRED_BUDGET`), so the narrative values of p9 were not recovered in this run.

| Review | Correct | Unresolved | Omitted | Recall | Retained | Precision (entities / statements / relations / quantities) | Correct holds | Critical |
| --- | ---: | ---: | ---: | --- | --- | --- | ---: | ---: |
| As produced (`review/`) | 18 | 10 | 6 | 18/34 = 0.53 | 28/34 | 64/75 = 0.85 (20/27, 29/32, 13/13, 2/3) | 1 | 0 |
| Replayed at `2adc6e8` (`revalidated_2adc6e8/review/`) | 18 | 10 | 6 | 18/34 = 0.53 | 28/34 | 64/67 = 0.96 (20/20, 29/32, 13/13, 2/2) | 1 | 0 |

- **New in this run:** the p4 specimen entity "Brass-filled PTFE samples" (`entities-02`) is correct for the first time in any run. So is batch #1 under LOX/GOX (`relations-32`).
- **Where the relations come from:** all 13 relations are correct. Eight are batch conditions bound to Table 3 rows; the rest are memberships by printed name.
- **What the new holds fixed:** as produced, five instruments or methods were typed as interventions and two values as conditions. They are held at `2adc6e8`.

## All reviewed runs at `2adc6e8` (`rescored_2adc6e8/`, `ptfe_live_a798003/revalidated_2adc6e8/`)

| Run | v5 | v6 M2 (`17b88c2`) | v6 M3 (`2adc6e8`) | Approved-property only | Retained | Precision | Critical |
| --- | --- | --- | --- | --- | --- | --- | ---: |
| First live run | 17/34 | 23/34 | **23/34 = 0.68** | 20/34 | 27/34 | 91/92 | 0 |
| Second live run | 18/34 | 22/34 | **24/34 = 0.71** | 22/34 | 28/34 | 82/83 | 0 |
| Fourth live run | 14/34 | 18/34 | **19/34 = 0.56** | 17/34 | 25/34 | 68/69 | 0 |
| Fifth live run | — | 17/34 | 17/34 = 0.50 | 15/34 | 24/34 | 69/72 | 0 |
| Sixth live run | — | 19/34 | **21/34 = 0.62** | 18/34 | 30/34 | 78/81 | 0 |
| Seventh live run | — | — | 18/34 = 0.53 | 17/34 | 28/34 | 64/67 | 0 |

`statements-25` is a correct hold in every run (the source prints conflicting counts), and it is not counted as recall.

- **Other sources** (`rescored_2adc6e8/exposed_sources_comparison.json`): 0 structure candidates on LUCI, ignition, regulator, textiles or the v4 PTFE package; the v4 PTFE package holds "Mechanical Impact Test" typed as an intervention; LUCI keeps its 9 correct staged quantities.
- **Negatives:** 29 historical items, 0 critical regressions.
- **Errata:** `review_errata.json` records that the first-run review's "Mechanical Impact Test" as an intervention is reversed to incorrect, consistently with the seventh run.

## What blocks 0.80 now

- **Variance between runs:** each run recovers a different subset (run 6 the p9 values, run 7 the specimen entity and conditions). A target that is correct in some run (2, 11–13, 15, 16, 32, 34) is often missing in another.
- **Deadline:** with 12–17 calls, the 1,800 s deadline cuts the recovery stages (run 7 deferred quantity recovery entirely).
- **Never recovered:** the Salox-M® composition (18), the Investigation-to-specimen relation (31) and the Salox-M® filler relation (33). Holds that strict recall does not count: 14, 17, 19, 22, 24, 26 and 28.

## Reproduce

```bash
uv run python scripts/phase1_offline_replay.py artifacts/phase1_generalizable_ingestion/v6/milestone3/ptfe_live_a798003/prepared.json.gz --output OUT
```
