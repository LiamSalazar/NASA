# Phase 1 v6, milestone 1: source quantities, staged properties, subject recovery

**Status: `PHASE1_COMPLETE=NO`.** Milestone 1 of Liam's consolidated mandate
(work packages A and B, with the role fixes they exposed) is implemented in the
ordinary validation path and measured offline on the exposed corpus. Recall on
the exposed PTFE source rose from 0.41–0.53 to 0.53–0.65 with precision kept at
0.98–0.99 and 0 critical errors, which is still below the 0.80 target. No
holdout was consumed.

PTFE (NTRS 20090043050) stays `EXPOSED_DEVELOPMENT_REGRESSION_ONLY`. The
reviews are the branch author's adjudications from full records, not expert
gold.

## Code (`diego/research`, main untouched at `54445d0`)

| Commit | Change |
| --- | --- |
| `ab8176f` | Units (psi/psia/psig with absolute/gauge reference, affine °C/°F, J, ft-lbf/ft-lbs, cal/g, inches, °F/min); a label made of an approved alias plus state modifiers reuses that property (`Initial Test Pressure (psia)` → `Pressure`, `vapor pressure` does not); an unapproved property is staged on a source-supported value (`activation: NONE`, never projected); `validate_quantity` revalidates a rejected subject against every other source-supported experimental subject and keeps the value `UNRESOLVED` without the rejected association when none or several survive, never falling back to the Investigation; a current-study table row naming a material scopes the value to the material as tested here; the configuration/derived cue of a prose value is read in its own sentence; standard deviations are dispersion statistics; one printed value under two roles is held; exact duplicate quantities are consolidated. |
| `2806ba3` | The scorer adds `semantic_recall_approved_properties_only`, so values correct only with a staged property are visible. |
| `b5cc4d8` | A staged property needs printed name–value syntax (column header, post-value dimensional adjective, `name = / : / was / is / of value`, or an ordered `respectively` list whose change verb is in the label); otherwise the value stays `UNRESOLVED` as before. `1-g` is not a quantity name; `g` is no longer read as grams. |

Quality at `b5cc4d8`: `ruff format --check`, `ruff check` and `pytest` pass (660 tests; 643 before).

## Measurements (offline replay of saved raw proposals, 0 model calls, same 36 frozen targets, 34 accessible)

| Run | v5 at `0ade8f1` | v6 M1 at `b5cc4d8` | Approved-property only | Retained | Precision (quantities) | Critical |
| --- | --- | --- | --- | --- | --- | --- |
| First live run (`2b7d1d6` proposals) | 17/34, 64/65 | **21/34 = 0.62**, 87/88 | 19/34 | 25/34 | 23/23 | 0 |
| Second live run (`e19b7c0` proposals) | 18/34, 61/62 | **22/34 = 0.65**, 70/71 | 20/34 | 26/34 | 9/9 | 0 |
| Fourth live run (`63e9bb9` proposals) | 14/34, 61/62 | **18/34 = 0.53**, 65/66 | 16/34 | 24/34 | 4/4 | 0 |

Targets newly correct in all three runs (they were `UNRESOLVED` for vocabulary or
subject alone in v5):

- `quantities-09`: 1332 cal/gram, Table 1 row `bBrass-filled PTFE` (legend NASA-STD-6001), material as tested here; property staged.
- `quantities-11`: AIT `>425` °C, Table 2, kept as a lower bound with the native value deferred (never 425); property staged.
- `quantities-12`, `-13`: initial 1500 and final 2268 psia, Table 2; approved `Pressure` reused through `initial test` / `final test`.

Every other target keeps its v5 outcome. Newly supported records not tied to a
target are the Table 3 reaction counts and specimen thicknesses of the batch,
Salox-M® and Algoflon® row groups (reviewed cell by cell against pages 12–13;
the LOX `4/80` of Batch #1 is faithful to the table and its conflict with the
p9 prose stays with `statements-25`).

Still blocked: `quantities-10` (standard deviation, no derived proposal),
`14`–`18` (narrative values: the fourth run attaches them to the Investigation
and no single experimental subject survives revalidation, so they stay
`UNRESOLVED`; the other runs did not propose them), the omitted entity and
relations, and the held statements.

### Other exposed sources (`exposed_sources_comparison.json`)

- LUCI: 7 → 16 supported quantities. The 9 new ones are staged flame-spread, width, length and preheat values printed as `name = value` or ordered lists, all correct on review; one decrease read as a length was held by `b5cc4d8`.
- Ignition: no new supported quantity; an intermediate version supported 7 staged values whose labels named objects or criteria, which led to the `b5cc4d8` gate.
- PTFE v4, regulator, textiles: unchanged.

### Negatives (`historical_negatives_receipt.json`)

All 29 historical items re-checked: 0 critical regressions; the same 2 known
non-critical records remain supported.

## Reproduce

```bash
uv run python scripts/phase1_offline_replay.py artifacts/phase1_generalizable_ingestion/v5/phase1_closure/ptfe_live_63e9bb9/prepared.json.gz --output OUT
```

```bash
uv run python scripts/score_scientific_review.py OUT/prepared.json artifacts/phase1_generalizable_ingestion/v6/milestone1/ptfe_run4_replay/review/source_review.json --output METRICS.json
```

The scorer reads plain JSON (decompress `prepared.json.gz` first). On Windows set `PYTHONUTF8=1`.

## Files

- `ptfe_run1_replay/`, `ptfe_run2_replay/`, `ptfe_run4_replay/`: replayed package, replay receipt, `review/source_review.json` (targets with `previous_outcome_v5` where re-adjudicated; earlier judgments reused only for identical proposal ids) and `review/scientific_metrics.json`.
- `exposed_sources_comparison.json`, `historical_negatives_receipt.json`, `CHECKPOINT.md`.
