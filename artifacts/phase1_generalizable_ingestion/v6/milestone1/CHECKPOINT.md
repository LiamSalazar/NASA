# Phase 1 v6 checkpoint after milestone 1 (`diego/research`)

**PHASE1_COMPLETE=NO.** Resume from here.

## Code state

- Code commits: `ab8176f`, `2806ba3`, `b5cc4d8` (author Diegomed11). `main` untouched at `54445d0`.
- Quality at `b5cc4d8`: `ruff format --check`, `ruff check`, `pytest` pass (660 tests).

## Done (milestone 1: work packages A and B)

- Units and dimensions, approved-property reuse through state modifiers, staged properties gated by printed name–value syntax, subject revalidation and preservation, material-as-tested table scope, sentence-local role cues, quantity role conflicts and duplicates.
- PTFE recall 0.62 / 0.65 / 0.53 on the three reviewed runs (from 0.50 / 0.53 / 0.41), precision 0.99, 0 critical; 0 critical regressions on 29 historical negatives; LUCI +9 correct staged quantities.

## Next (milestone 2: work packages C, D, E)

1. Narrative quantities (targets 14–18): source-grounded candidate inventory for prose values and targeted recovery of their experimental subject; the specimen entity of p4 (`entities-02`) and the relations 31–33 are omitted by the model in every run.
2. Statement roles still held (22, 24, 25, 28): check each hold against its expectation; 26 and 28 differ by run.
3. Then a fifth live run through `scripts/phase1_exposed_live_run.py` to measure variance with the new validators.
