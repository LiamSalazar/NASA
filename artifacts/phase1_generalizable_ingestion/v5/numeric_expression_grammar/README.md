# Phase 1 v5 — numeric-expression grammar (defect 2)

Scope: checkpoint v4 defect 2 only ("numeric-expression grammar rejects original
thousands separators, reaction-count ratios and some unit-bearing expressions").
Tables/batch identity (defect 1) and scope/attribution (defect 3) are not part of
this work. `PHASE1_COMPLETE=NO` is unchanged.

## Code

- `src/nasa_fire_ai/ingestion/numeric_expressions.py` (new): syntax only. It
  returns PARSED / AMBIGUOUS / NOT_NUMERIC, the form (SCALAR, RANGE, BETWEEN,
  FROM_TO, PLUS_MINUS, RATIO, WORDS), qualifiers, exact decimal-string
  candidates, footnote markers and ambiguity codes. It assigns no scientific
  role (`scientific_role: NOT_DETERMINED_BY_SYNTAX`).
- `document_extraction.py`:
  - `quantity_expression_pattern()` now delegates to the new finder.
  - The quantity gate in `validate_output` uses the parser. A unit a model
    copied into the expression is split only when it is unambiguous and the
    split is recorded in `expression_normalization`.
  - Source value location (`validate_output`, `quantity_name_value_binding`)
    uses `source_numeric_matches`.
  - Ambiguous expressions become UNRESOLVED (`NUMERIC_EXPRESSION_AMBIGUOUS`).
  - Ratios are not flagged `QUANTITY_UNIT_UNSPECIFIED`.
- `pdf_quantities.py`: PDF cells are gated by the parser (`table_cell=True`).
  The parse is attached as `proposal.numeric_expression`.
- No validator was loosened. No prompt, provider, ontology or SHACL change.

Grouped thousands such as "1,250" are read using the document's own
unambiguous numerals (`decimal_convention`). Without that evidence every
candidate is kept and the expression is reported ambiguous.

## Offline replay on exposed v4 receipts

`scripts/phase1_numeric_replay.py` replays saved source text and saved raw
Nemotron quantity proposals through the production validator. It makes 0 model
calls. `before_liam_main/` ran at `7bc6516`, which is main `54445d0` plus the
Windows portability fix. `after_a0bff78/` ran at `a0bff78`. Both src trees
were clean.

| Receipt | Raw quantities | Numeric-gate rejections | PDF table cells | Statuses |
| --- | ---: | ---: | ---: | --- |
| ptfe prepared_1 | 69 | 56 → 0 | 125 → 265 | 69 REJECTED → 69 REJECTED |
| regulator prepared_1 | 73 | 5 → 1 | 0 → 0 | 1 UNRESOLVED → REJECTED (see below) |
| ignition prepared_1 / _2 | 55 / 89 | 4 → 1 / 4 → 1 | 39 → 39 | unchanged |
| luci_application_final | 35 | 0 → 0 | 9 → 9 | unchanged (7 SOURCE_SUPPORTED kept) |
| textiles prepared_1 | 8 | 0 → 0 | 0 → 0 | unchanged |

**Totals over all 10 replayed receipts:**

- Numeric-gate rejections fell from 69 to 3. All 3 remaining are genuinely not
  one value: `'~.9 and 4.3'` (two values) and `'approximately a'` (twice).
- No SOURCE_SUPPORTED quantity was lost.
- No previously rejected quantity became accepted.

The one retained → rejected change is a fidelity correction. The source reads
"up to ~ 1pph"; the proposal `~ 1` dropped the upper bound. Before, it was
retained. Now it is QUANTITY_EXPRESSION_ABSENT.

**Main finding.** The 56 PTFE proposals that used to fail on syntax now fail on
`QUANTITY_SUBJECT_NOT_IN_APPLICABLE_SOURCE`, and so do 4 regulator and 6
ignition proposals. These include `10,000 psia`, `0/20` reactions/tests and
`50 ft-lbs (68J)`. The numeric grammar was masking the scope/attribution
defect, which is now the binding constraint for those quantities. Recall will
not move until scope (M2) is repaired.

## Source values that were wrong before

These come from the production coverage inventory replayed on the same saved
text.

| Source | Before (located value) | After |
| --- | --- | --- |
| PTFE "10,000 psia" (×3), "5,000", "1,500" | "000 psia" ×4, "500 psia" ×2 | whole numbers |
| PTFE "from 60 psia to 3,250 psia" | "250 psia" | ordered pair |
| PTFE "above 425 °C" | "425 °C" | bound kept |
| Ignition "1/6 g" | "6 g" | ratio kept |
| Regulator "up to 100 mg", "below -50 F" | "100 mg", "-50 F" | bound kept |
| Textiles "up to 37 %" | "37 %" | bound kept |

The inventory feeds the targeted quantity-recovery stage, where these items are
offered to the model as Q candidates.

## Quality

- `uv run ruff format --check .` and `uv run ruff check .` pass.
- `uv run pytest -q`: 508 passed.
  - The 37 failures/errors are identical before and after this work. They all
    need the uncommitted `data/index/evidence.sqlite` or `artifacts/phase3c_*`.
- `tests/test_numeric_expressions.py` has 61 cases:
  - syntax families;
  - metamorphic equivalent/different writings;
  - an earlier-grammar superset check;
  - integration through `validate_output` and `pdf_table_quantities`.

## Units inherited from table headers (`4a2f99d`)

A table value binds to a unit only through the literal "(unit)" in its own
column header on a supporting page; see `pdf_quantities.header_unit_binding`.
The binding is recorded in `record["unit_binding"]` with its table locator and
no conversion, and unit comparison is case-sensitive.

On the live PTFE raw output, `QUANTITY_UNIT_NOT_BOUND_TO_EXPRESSION` fell from
48 to 30. The remaining 30 are all in continuation tables whose detected header
is a data row.

## Live run

`ptfe_live_2b7d1d6/` contains a real Nemotron run of the exposed PTFE source
through the ordinary application, plus an equal-standard comparison with v4.
See its README.

## Checkpoint

- **Done:**
  - defect 2 syntax and integration;
  - header-unit inheritance;
  - a live exposed run and its equal-standard review.
- **Not done:** CSV table path (`curation.parse_value` / line ~2900 in
  `document_extraction.py`) still uses the earlier NUMBER grammar.
  - It was left unchanged to avoid colliding with concurrent curation work.
- **Next executable actions (M1/M2 owner):**
  - continuation-table header inheritance (pages 13, 16, 17);
  - row/batch subject binding for table quantities;
  - comparator-material lineage.
  - Reproduce offline with `uv run python scripts/phase1_numeric_replay.py --output <new dir> --packages artifacts/phase1_generalizable_ingestion/v5/numeric_expression_grammar/ptfe_live_2b7d1d6/prepared.json.gz`.
