# Phase 1 v6 checkpoint after milestone 4 (`diego/research`)

**PHASE1_COMPLETE=NO.** Resume from here.

## Code state

- Code commits after milestone 3: `9d509ff`, `37d9953`, `00dac49`, `6a83a2f`, `7021bac`, `c314286` (author Diegomed11). `main` untouched at `54445d0`.
- Quality at `c314286`: `ruff format --check`, `ruff check`, `pytest` pass (677 tests).

## Measured (exposed PTFE, 36 frozen targets, 34 accessible)

- **Live runs with the current pipeline:** 28/34 (0.82) at precision 0.97, and 27/34 (0.79) at 0.91. 0 critical in both.
- **Six older runs replayed:** 24–28/34, precision 0.96–0.99.
- **Stability:** 21 targets are correct in all eight runs, and the ceiling under current vocabulary is 28/34.

## Next concrete action

1. Precision rules for the ninth run's error families (test media typed as materials, configurations of cited work, procedures typed as interpretations), each checked against all eight runs before it is kept.
2. Two more live runs at 3,600 s with the current code. The development gate is 28/34 at precision ≥ 0.95 in consecutive runs.
3. Send Liam the vocabulary request: an approved material-to-component relation for targets 18 and 33.
4. Only then, the §14 prospective holdout on a new, unexposed NASA source.
