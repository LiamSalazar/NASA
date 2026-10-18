# Phase 1 v5 closure checkpoint (`diego/research`)

**PHASE1_COMPLETE=NO.** Resume from here; no architectural analysis is needed.

## Code state

- Final code commit: `63e9bb9` (author Diegomed11). `main` untouched at `54445d0`.
- Quality at `63e9bb9`: `ruff format --check`, `ruff check` and `pytest` pass (639 tests).
- Receipts in this folder were generated at `63e9bb9`; `README.md` holds the §18 matrix.

## Completed

- M1: numeric grammar (§5), continuation tables, row groups, legend-backed footnote markers in both directions, row/cell/header-unit binding, table-structure receipt.
- M2: document-investigation scope, cited attribution and cited tables, comparator lineage, `madeOf` by printed name, statement integrity holds (fragments, conflicts, criteria, caveats, pointers, procedures, incompatible roles), omission recovery through a bounded split path, curation gated to `SOURCE_SUPPORTED`.
- §8: four-question source eligibility, stored in `source_provenance`, review requirement kept in `validate()`.
- Measurements: PTFE replays 17/34 and 18/34 correct, precision 64/65 and 61/62, 0 critical; 26 historical critical negatives still rejected or held; five-source comparison; curation and eligibility receipts.
- `docs/PHASE1_GENERALIZABLE_SCIENTIFIC_INGESTION.md` has the v5 section at the top.

## Remaining reproducible work

1. Fourth live run (`C:/Users/legom/Documents/proyects/nasa-live/ptfe-63e9bb9-out/`, started by `scripts/phase1_exposed_live_run.py` at `63e9bb9`): when it finishes, copy `prepared.json.gz`, `attempts.json.gz`, `validation.json.gz`, `submission.json` and a gzipped `summary.json` into `ptfe_live_63e9bb9/`, judge every non-duplicate `SOURCE_SUPPORTED` record (helper: `%TEMP%/nfa/adjudicate_v3.py`, add a `run3` configuration), score with `scripts/score_scientific_review.py`, and replace the `<<RUN4_…>>` placeholders in `README.md`.
2. Nothing else is pending inside this branch's scope. Recall on the exposed source (0.50–0.53) stays below the §11 target of 0.80 for reasons outside the branch: property vocabulary and units, scorer credit for correctly held targets, model omissions (see README, "Blockers for Liam"). No holdout is to be consumed until §12 readiness is demonstrated.

## Next concrete action

Finish item 1 above, commit the receipts, push `diego/research`, and send Liam the blockers list.
