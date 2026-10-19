# Phase 1 v6, milestone 4: recall from the printed structure, role and class recovery

**Status: `PHASE1_COMPLETE=NO`.** The goal was 28/34 = 0.82 (recall ≥ 0.80) in
a single run. The two live runs made with the current pipeline reach 28/34
(0.82) and 27/34 (0.79), with 0 critical errors; precision is 0.97 and 0.91.
The development gate is met in one live run of two, and the precision target
(≥ 0.95) in one of two. No holdout has been consumed.

Exposed development source only (PTFE, NTRS 20090043050). The reviews are the
branch author's adjudications from full records, not expert gold.

## What changed (`diego/research`, main untouched at `54445d0`)

A per-target table across the reviewed runs (`rescored_c314286/target_matrix.json`) showed which targets were missed most often. The fixes take those targets from what the document prints, and the validator decides on them exactly as on model proposals.

| Commit | Change |
| --- | --- |
| `9d509ff` | Printed-structure candidates (`candidate_origin=PRINTED_SOURCE_STRUCTURE`): a "<tested material> samples" Sample with its sentence; condition entities from a "Condition(s)" column of current rows; a value applied in a test step that the subject's own rows print under a column (name from that column, pronoun from the preceding sentence); a standard-deviation column as a derived value; a sample "discussed in this paper" belongsToInvestigation. |
| `37d9953` | Role recovery: a statement held only because its role contradicts what the validator detects is revalidated with the detected role (a criterion or conditional recording rule as a normative requirement; a "derived" sentence that reports a result with a finite verb as an observation). A current observation that reads a cited table is held whatever subject was proposed. |
| `00dac49` | The relationships stage runs after the targeted quantity recovery, so a deadline no longer starves the recovery. |
| `6a83a2f` | Recovery never moves a value onto a condition entity or onto a table cell without that subject's row binding (it had attributed cited Table 5 pressures to a current condition). A reported cell in a column whose values an applied test step prints, in the cell's own canonical unit, is a configuration. |
| `7021bac` | A setting-versus-result conflict on one cell is settled by its column's state word (initial/set → setting, final/measured → result). |
| `c314286` | A printed "<material> (qualifier)" group proposed as a Material, beside that material, is revalidated as its Sample group; a pronoun's antecedent for a test value counts a material only when the document's tables show it tested here. |

A paragraph-level cited-work guard was tried and reverted: the PDF text loses paragraph breaks, so it held dozens of correct current-study sentences.

Quality at `c314286`: `ruff format --check`, `ruff check`, `pytest` pass (677 tests).

## Live runs with the current pipeline

| Run | Code | Calls / time | Recall | Approved-property only | Retained | Precision | Critical |
| --- | --- | --- | --- | --- | --- | --- | ---: |
| Eighth (`ptfe_live_00dac49/`) | `00dac49`, replayed at `c314286` | 19 / 2,137 s of 3,600 s | **28/34 = 0.82** | 24/34 | 32/34 | **129/133 = 0.97** | 0 |
| Ninth (`ptfe_live_7021bac/`) | `7021bac`, replayed at `c314286` | 15 / 2,101 s of 3,600 s | 27/34 = 0.79 | 24/34 | 32/34 | 83/91 = 0.91 | 0 |

The ninth run's eight incorrect records are model errors with no safe general rule yet:
- LOX, GOX and Nitrogen typed as test materials;
- two configurations of the cited Bryan/KSC work scoped to this study;
- two procedures or criteria typed as an interpretation or observation;
- one material description typed as a configuration.

## All reviewed runs at `c314286` (`rescored_c314286/`)

| Run | v5 | M3 (`2adc6e8`) | **M4 (`c314286`)** | Precision | Critical |
| --- | --- | --- | --- | --- | ---: |
| First | 17/34 | 23/34 | **28/34** | 134/135 | 0 |
| Second | 18/34 | 24/34 | **28/34** | 89/90 | 0 |
| Fourth | 14/34 | 19/34 | 26/34 | 85/86 | 0 |
| Fifth | — | 17/34 | 24/34 | 86/89 | 0 |
| Sixth | — | 21/34 | 27/34 | 87/90 | 0 |
| Seventh | — | 18/34 | 24/34 | 70/73 | 0 |
| Eighth | — | — | **28/34** | 129/133 | 0 |
| Ninth | — | — | 27/34 | 83/91 | 0 |

- **Correct in all eight runs:** 21 of the 34 accessible targets.
- **Never correct (6):** 14 and 17 (relative percentages: comparison against cited data, batch-specific percentages), 18 and 33 (the Salox-M® composition and its filler relation, which need an approved material-component relation), 24 (a cited result) and 25. Target 25 is a correct hold (`correctly_held_targets`).
- **Ceiling with current vocabulary and strict scoring:** 28/34.
- **Other sources and negatives:** unchanged on the other exposed sources, and the 29 historical negatives show 0 critical regressions (`rescored_c314286/exposed_sources_comparison.json`, `historical_negatives_receipt.json`).

## What remains

1. **Precision ≥ 0.95 in every run.** The ninth run's error families need general rules: a test medium typed as a material, configurations of cited work in a cited-work paragraph (needs reliable paragraph boundaries), and procedures typed as interpretations.
2. **Stability of 28/34.** Statements 19, 26 and 28 still vary by run.
3. **Vocabulary for Liam:** an approved material-to-component relation (for example `hasComponent`, Material → Material) for targets 18 and 33.
4. **§14 holdout.** Only after the development gate holds in consecutive live runs: a new, unexposed NASA source chosen prospectively, with frozen code and protocol.
