# Phase 3C change log

R1 occurred before holdout selection. R2 and R3 occurred after the documentary first pass.

Pre-holdout benchmark repair R1: GENERIC_BUG_FIX. The original projection seeded
canonical entity identities only from rows in the legacy execution view. The first
parity pass consequently failed to compile queries for reviewed PMMA. Registering
reviewed identities independently of corpus occupancy fixes that initialization
error. The declarative registry lists identities already present in the approved
lexicon and canonical investigation records. No new alias or scientific source
interpretation was introduced. Planner/evaluator/classifier code is unchanged.

The first architecture freeze, dynamic benchmark, post-freeze stress result, parity
result, and first live interpreter receipt are preserved. Second-pass results and a
second pre-holdout freeze use distinct filenames. They are not first-pass results.

R2, after documentary first pass: GENERIC_BUG_FIX in the evaluation adapter only.
Bounded synthesis now caps each supplied scientific record list at four, alongside
the existing two-passage cap. The first synthesis attempt timed out. Its failure
receipt remains intact. This limits model context for representative regression;
it changes no native semantic mapping, executor, graph, or holdout ingestion result.

R3: GENERIC_BUG_FIX, projection provenance. Numeric values copied from the normalized
legacy execution view now populate canonical value/unit slots only. They no longer
populate reported slots as though NASA originally reported those normalized units.
Original source values and units remain in the unchanged canonical ConditionRecords
and Evidence Registry passages. Categorical source labels retain their reported form.
No planner, evaluator, classifier, query gold, raw source, or holdout graph was changed.
Earlier projection artifacts are retained as pre-repair results and must not be used
to claim original reported-unit preservation. A separate projection-repair freeze and
parity result record the repair; it changes provenance, not scientific matching gold.
