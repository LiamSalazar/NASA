# Phase 1 v6 checkpoint after milestone 2, part 1 (`diego/research`)

**PHASE1_COMPLETE=NO.** Resume from here.

## Code state

- Code commits after milestone 1: `8bc0d04`, `2a64310` (author Diegomed11). `main` untouched at `54445d0`.
- Quality at `2a64310`: `ruff format --check`, `ruff check`, `pytest` pass (663 tests).

## Measured

- PTFE recall by run: 0.62, 0.65 and 0.53 (runs 1, 2 and 4 replayed), and 0.50 in the fifth live run.
- Precision 0.96–0.99 after the holds, 0 critical.
- 29 historical negatives: 0 critical regressions.

## What blocks recall now

In every run the model omits the same items: the p4 specimen entity
(`entities-02`), the narrative values of p7, p9 and p10 (`quantities-14`–`18`),
statement 19 and relations 31–33. Proposals that do exist for them fail on
names that are printed only in a table header ("Impact Energy" for "impacted
with 98 Joules"), on the anaphoric subject "It", or on a material subject in
prose.

## Next concrete action (work package C)

Use the source inventory (`scientific_coverage.coverage`) to name these omitted
prose sentences and values to `recover_stage` with their candidate subjects. In
the deterministic validator, accept a prose value whose name and unit are
printed for the same material under a column header of this document's own
current-study table. Then measure with a sixth live run.
