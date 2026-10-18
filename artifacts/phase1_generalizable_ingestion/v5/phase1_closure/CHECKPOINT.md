# Phase 1 v5 closure checkpoint (`diego/research`)

**PHASE1_COMPLETE=NO.** Resume from here; no architectural analysis is needed.

## Code state

- Final code commit: `0ade8f1` (author Diegomed11). `main` untouched at `54445d0`.
- Quality at `0ade8f1`: `ruff format --check`, `ruff check` and `pytest` pass (643 tests).
- Receipts in this folder: replays and reviews at `0ade8f1`; the `63e9bb9` replays and reviews are kept because the fourth run's review reuses their judgments by proposal id. `README.md` holds the §18 matrix.

## Completed

- M1: numeric grammar (§5), continuation tables, row groups, legend-backed footnote markers in both directions, row/cell/header-unit binding, table-structure receipt.
- M2: document-investigation scope, cited attribution and cited tables, comparator lineage, `madeOf` by printed name, statement integrity holds (fragments, conflicts, criteria, caveats, pointers, procedures and bare test steps, validity caveats typed as interpretations, incompatible roles, caption identities), omission recovery through a bounded split path, curation gated to `SOURCE_SUPPORTED`.
- §8: four-question source eligibility, stored in `source_provenance`, review requirement kept in `validate()`.
- Measurements: PTFE replays 17/34, 18/34 and 14/34 correct (first, second and fourth runs), precision 64/65, 61/62 and 61/62, 0 critical; the fourth run as produced measured 61/66 and its three role errors are held by `0ade8f1`; 26 historical critical negatives still rejected or held; five-source comparison unchanged by the last holds; curation and eligibility receipts.
- `docs/PHASE1_GENERALIZABLE_SCIENTIFIC_INGESTION.md` has the v5 section at the top, updated for the fourth run.

## Remaining reproducible work

1. Nothing is pending inside this branch's scope. Recall on the exposed source (0.41–0.53) stays below the §11 target of 0.80 for reasons outside the branch: property vocabulary and units, scorer credit for correctly held targets, model omissions and variance (the fourth run proposed no `madeOf` and attached every quantity to the Investigation; see README, "Blockers for Liam"). No holdout is to be consumed until §12 readiness is demonstrated.
2. A fifth live run is only worth running after the vocabulary decision; the runner and the review helpers are in place (`scripts/phase1_exposed_live_run.py`, `scripts/score_scientific_review.py`).

## Next concrete action

Send Liam the blockers list (README, "Blockers for Liam") and wait for the vocabulary and scorer decisions.
