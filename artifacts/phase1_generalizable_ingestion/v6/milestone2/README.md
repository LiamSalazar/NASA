# Phase 1 v6, milestone 2 (part 1): fifth live PTFE run and lineage holds

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
