# Milestone 13

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

## Correction 3: one statement per printed sentence across windows

- Classification: document structure.
- Rule: statements with the same normalized text, status, epistemic role, study, reasons and support positions are one statement. The owner keeps the union of the scopes, each validated on its own. Before this change, the scope was part of the key, so the same sentence proposed from two windows with different subjects stayed duplicated.
- Motivating source: regulator, m12 r1 (the "Sixty test runs were executed..." pair).
- Tests: `tests/test_statement_window_duplicates.py`, passing:
  - two windows give one statement with both scopes;
  - order metamorphic;
  - a different role stays separate.
- Replay of the 46 inputs at `4b18bf5` (against the correction 2 replay):
  - 15 duplicate statements folded into their twins (ignition 6, regulator 3, PTFE 6), and 0 other changes;
  - 0 target classes changed in the miss diagnosis;
  - PTFE official scorer (judgments `judg_ptfe_B`): recall unchanged in all 13 PTFE replays (27–28/34; B_ptfe 23/34); precision only loses the duplicates (for example run11 132/133 → 129/130); 0 critical;
  - 29 historical negatives: 0 critical regressions, 1 known non-critical (`replay_4b18bf5/historical_negatives_receipt.json`).

## Correction 1: printed_name, and the group subject for quantities

- Classification: semantic with evidence.
- Change:
  - `Quantity` gains an optional `printed_name`: the words of the value's own clause that name it, copied exactly, when the label's words are not printed with the value.
  - The propositions prompt and the focused quantities request ask for it.
  - The group-key instruction now also makes the group the subject of a quantity printed under its heading, unless the sentence names another.
- Validator: a printed_name names the value only when it shares a clause with the value (`quantity_name_value_binding`), holds a word that is not the value, its unit or a joining word, and has at most 6 words. Its basis is `MODEL_PRINTED_NAME_IN_VALUE_CLAUSE`. The label stays the model's. A staged property must also pass the name-to-value syntax with the printed words.
- Motivating source: the miss diagnosis (`target_miss_diagnosis.md`). `QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT` is the most frequent rejection, with 10 target-run pairs in ignition, regulator and textiles ("rotated at 20.4 RPM", "20uL was injected", "~100 mg/ft2 film coating").
- Effect on saved inputs: none. Replay of the 46 inputs gives 0 active-record changes, since no saved response carries printed_name. Its effect is measurable only in live runs (evaluation B).
- Cache keys: the request schema changes, so every model cache key changes. Saved outputs replay unchanged, but no earlier live response is reused.
- Tests: `tests/test_model_printed_name.py` (7 tests). The baseline without printed_name is still rejected. The negatives are a word from another clause, an unprinted word, the unit, the value and a joining word.

## Pending
- Target-by-target miss diagnosis: done in `target_miss_diagnosis.md`/`.json` (69 of 104 missed target-run pairs (66%) are proposals rejected by a rule; the main code is `QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT`).
- Evaluation B of milestone 13 (one round, sources two at a time, detached runs).
- No live run was in progress at the shutdown of 2026-10-21 19:19 UTC; none was lost.
