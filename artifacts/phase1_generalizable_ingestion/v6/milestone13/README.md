# Milestone 13 (work in progress, pushed before a scheduled shutdown)

Evaluation A only (offline replay of saved inputs, 0 model calls). No evaluation B was run on this code.

## Correction 2: precision by printed structure (commit "Hold an entity or observation printed only under a background, theory or analysis heading")

- Classification: document structure.
- Rule: an entity (not Investigation or Material, not cited), or a measured observation or experimental configuration, whose whole support lies under a printed introduction, background, theory, analysis or model heading, or under a section that prints numbered equations on their own lines, is set to UNRESOLVED with reason `SUPPORT_ONLY_IN_BACKGROUND_OR_ANALYSIS_SECTION`. In decks with no roman-numbered sections, a heading governs only its own page. No source title is listed.
- Motivating source: regulator (thermal-model analysis statements; the theory concepts "Heat Transfer Limit" and "Limiting Oxygen Concentration"; model boundary conditions).
- Replay of the 46 saved inputs (milestones 10 to 12):
  - 36 records held, none critical;
  - 0 targets lost in the 4 sources;
  - PTFE and textiles unchanged;
  - 29 historical negatives: 0 critical regressions, 1 known non-critical.
- Tests: `tests/test_background_sections.py` (6, metamorphic and negative).

## Correction 3: one statement per printed sentence across windows (WIP commit)

- Classification: document structure.
- Rule: statements with the same normalized text, status, epistemic role, study, reasons and support positions are one statement. The owner keeps the union of the scopes, each validated on its own. Before this change, the scope was part of the key, so the same sentence proposed from two windows with different subjects stayed duplicated.
- Motivating source: regulator, m12 r1 (the "Sixty test runs were executed..." pair).
- Tests: `tests/test_statement_window_duplicates.py`, passing:
  - two windows give one statement with both scopes;
  - order metamorphic;
  - a different role stays separate.
- PENDING: the 46-input replay and the 29 negatives have not been run with this change.

## Pending

- Replay plus negatives for correction 3.
- Correction 1 (`printed_name` in the model request plus a subject by group subsection) is not started. It changes the request schema and therefore the cache keys.
- Target-by-target miss diagnosis (`target_miss_diagnosis.md`/`.json`) is not produced yet.
- Evaluation B of milestone 13 (one round, sources two at a time, detached runs).
- No live run was in progress at shutdown.
