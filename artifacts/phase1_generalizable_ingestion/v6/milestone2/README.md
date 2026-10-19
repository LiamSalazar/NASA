# Phase 1 v6, milestone 2: live runs 5 and 6, lineage holds, targeted recovery of prose values

## Part 2 (work package C): targeted recovery and prose values (`ptfe_live_b8db2a5/`, `rescored_17b88c2/`)

**Status: `PHASE1_COMPLETE=NO`.** In every earlier run the focused quantity
recovery returned empty. Its candidates were mostly Table 3 cells, which the
table binding already covers, and the prompt offered no material as a subject.
After `b8db2a5` the recovery asks for prose values on the materials this
document's own tables show tested here, and the sixth live run proposes them.
The validator then needed source-grounded rules to accept those values.

| Commit | Change |
| --- | --- |
| `b8db2a5` | Recovery candidates exclude values printed in a table cell on the same page (166 → 31 on the fifth run, all prose). A current material whose printed table rows exist and none is cited is established as tested here: it is offered as a recovery subject, and its prose values are scoped `MATERIAL_ESTABLISHED_AS_TESTED_IN_THIS_STUDY` (never a general property, never projected). |
| `0294286` | A prose value is named by the subject's own table column when one of its rows, with no cited lineage, prints the same number in the same unit dimension ("It was impacted with 98 Joules" ↔ "Impact Energy (ft-lbs/J)"). A pronoun that opens the sentence ("It", "They", "Each") binds to the one material, sample, group or run named in the preceding sentence of the paragraph. A value after an applied test step is not a measurement. "12% lower" is a printed relative difference kept as a derived value with its comparative. A sentence cut by a page break is read joined. A row group of a material wins over the material. |
| `17b88c2` | A label that is a number and any interpreted unit ("0.062 inches") is not a named entity. |

Quality at `17b88c2`: `ruff format --check`, `ruff check`, `pytest` pass (668 tests).

### Sixth live run (`ptfe_live_b8db2a5/`)

17 model calls, 1,857 s, `PARTIAL_MODEL_COVERAGE`, 0 approvals, 0 publications, SQLite `ok`. The focused quantity recovery returned 17 proposals in the central window (0 in every earlier run).

| Review | Correct | Unresolved | Omitted | Recall | Approved-property only | Retained | Precision | Critical |
| --- | ---: | ---: | ---: | --- | --- | --- | --- | ---: |
| As produced (`review/`) | 17 | 8 | 9 | 17/34 = 0.50 | 15/34 | 25/34 | 63/69 = 0.91 | 0 |
| Replayed at `17b88c2` (`revalidated_17b88c2/review/`) | 19 | 9 | 6 | 19/34 = 0.56 | 16/34 | 28/34 | 66/69 = 0.96 | 0 |

At `17b88c2` this run gets the 98 J and 10,000 psia of p9 right (targets 15 and 16) for the first time from recovered proposals. It also gets Algoflon® E2/F7 right as current. It proposes no accepted relation (relations 31–34 omitted), which is model variance.

### All reviewed runs at the current code (`rescored_17b88c2/` and `ptfe_live_b8db2a5/revalidated_17b88c2/`)

| Run | v5 (`0ade8f1`) | v6 at `17b88c2` | Approved-property only | Retained | Precision | Critical |
| --- | --- | --- | --- | --- | --- | ---: |
| First live run | 17/34 | **23/34 = 0.68** | 20/34 | 27/34 | 91/92 | 0 |
| Second live run | 18/34 | 22/34 = 0.65 | 20/34 | 26/34 | 70/71 | 0 |
| Fourth live run | 14/34 | 18/34 = 0.53 | 16/34 | 24/34 | 64/65 | 0 |
| Fifth live run | — | 17/34 = 0.50 | 15/34 | 24/34 | 69/72 | 0 |
| Sixth live run | — | 19/34 = 0.56 | 16/34 | 28/34 | 66/69 | 0 |

In the first run, targets 15 and 16 are newly correct at `17b88c2` from its own saved proposals. Four new records were judged; all are correct. Other sources at `17b88c2` (`rescored_17b88c2/exposed_sources_comparison.json`) have identical counts to `2a64310`. The 29 historical negatives show 0 critical regressions (`rescored_17b88c2/historical_negatives_receipt.json`).

### What still blocks 0.80

- **Omitted by the model in most runs:** the p4 specimen entity (02), the Salox-M® composition (18) and relations 31–33. Run 6 also proposed no relation.
- **Held by design:**
  - 13 in run 6: the same cell was proposed under two roles.
  - 14: a relative difference against cited data.
  - 17: batch-specific percentages proposed on the material.
  - 22, 24, 25, 26, 28: a recording rule, a cited result, a printed count conflict, and roles that need review.
  - 25 can never count under strict recall: its expectation is to keep both conflicting statements unresolved.

# Part 1: fifth live PTFE run and lineage holds

**Status: `PHASE1_COMPLETE=NO`.** The fifth live run measures the milestone 1
validators through the ordinary application. It exposed two families of
errors, both repaired generally. Recall on the exposed source is 0.50 in this
run (0.53–0.65 on the earlier runs replayed). It stays below 0.80 because the
model omits the same items run after run. No holdout was consumed.

## Code (`diego/research`, main untouched at `54445d0`)

| Commit | Change |
| --- | --- |
| `8bc0d04` | A material typed `cited` whose printed table rows are all of this study is held (`CITED_STUDY_CONTRADICTED_BY_CURRENT_TABLE_ROWS`), mirroring the existing hold for a `current` material printed only in cited rows. A row group that only adds a parenthetical to the name (`Kel-F®81 (PCTFE)`) counts as that material's rows. |
| `2a64310` | The validity-caveat hold ("only valid for …") also covers a caveat typed as an experimental configuration. |

Quality at `2a64310`: `ruff format --check`, `ruff check`, `pytest` pass (663 tests).

## Fifth live run (`ptfe_live_29aead3/`)

`scripts/phase1_exposed_live_run.py` at `29aead3` (milestone 1 code), NVIDIA `nemotron-3.5-super-vl-120b-a12b` with the configured fallback, 17 model calls, 1,208 s of a 1,800 s deadline, `PARTIAL_MODEL_COVERAGE`, 0 approvals, 0 publications, SQLite `ok`, no source-integrity error.

| Review | Correct | Unresolved | Incorrect | Omitted | Recall | Approved-property only | Retained | Precision (entities / statements / relations / quantities) | Critical |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- | --- | ---: |
| As produced (`review/`) | 17 | 5 | 2 | 10 | 17/34 = 0.50 | 15/34 | 22/34 | 69/77 = 0.90 (13/17, 32/36, 4/4, 20/20) | 0 |
| Replayed at `2a64310` (`revalidated_2a64310/review/`) | 17 | 7 | 0 | 10 | 17/34 = 0.50 | 15/34 | 24/34 | 69/72 = 0.96 (13/13, 32/35, 4/4, 20/20) | 0 |

- **Correct in this run:** the title Investigation, Brass-filled PTFE, Salox-M®, Batch #1 and #2, all four table quantities of targets 9 and 11–13, statements 20, 21, 23 and 27–30, and relation 34.
- **What the new holds fixed:** Algoflon® E2 and F7 typed `cited` (targets 5 and 6) were incorrect as produced and are held at `8bc0d04`. Kel-F® 81 typed `current` and a second Salox-M® typed `cited` are held too, as is the caveat at `2a64310`.
- **The 3 incorrect records left at `2a64310`, all non-critical role errors:** a calorimeter readout typed as an observation (also in the second run), a photo observation typed as an interpretation, and the narrative framing sentence typed as a conclusion that earlier runs also showed.
- **Omitted by the model:** the p4 specimen entity, narrative values 14–18, statement 19 and relations 31–33. The first, second and fourth runs omit most of the same targets.

### Other receipts at `2a64310`

- `exposed_sources_comparison.json`: LUCI 16 supported quantities (as at milestone 1); in the v4 PTFE package one more entity is held (Kel-F 81 typed `current`); ignition, regulator and textiles unchanged.
- `historical_negatives_receipt.json`: 29 items, 0 critical regressions, the same 2 known non-critical records supported.
- `review_errata.json`: the fourth run's `cited` Salox-M® judged correct earlier ("identity only") is wrong lineage by the standard the reviews already apply; it is held now, and run 4 precision at `2a64310` is 64/65 (no target changes).

## Reproduce

```bash
uv run python scripts/phase1_exposed_live_run.py --pdf 20090043050.pdf --provenance-from artifacts/phase1_generalizable_ingestion/v4/independent_ptfe_application/prepared.json.gz --workspace OUTSIDE_REPO --directory OUT --timeout-seconds 1800
```

```bash
uv run python scripts/phase1_offline_replay.py artifacts/phase1_generalizable_ingestion/v6/milestone2/ptfe_live_29aead3/prepared.json.gz --output OUT
```
