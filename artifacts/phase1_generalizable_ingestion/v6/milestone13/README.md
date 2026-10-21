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

## Evaluation B at b4be17d (one round, sources in pairs)

Detached from the session: textiles with regulator, then ignition with PTFE, at 600 s per call and 3,600 s per run. Strict recall is against frozen v4 targets. Precision is record by record (`evaluation_b.json`, `adjudication.json`). PTFE uses the official scorer.

| source | recall m13 r1 | m12 r1 / r2 | precision | critical | calls | failed attempts |
|---|---|---|---|---|---|---|
| textiles | 7/29 | 10/29 / 10/29 | 17/22 | 0 | 5 | 1 deadline |
| regulator | 10/32 | 14/32 / 17/32 | 16/30 | 0 | 11 | 4 network |
| ignition | 15/29 | 11/29 / 14/29 | 86/115 | 0 | 16 | 0 |
| PTFE (official) | 28/34 | 27/34 / 28/34 | 137/139 | 0 | 20 | 2 HTTP 500 |

Causes of variation:
- **Textiles (model):** the custom patches were typed Material, not Sample, so their two values had no subject.
- **Regulator (provider):** the window with the impact times failed three times on the 120b model and was answered by the 30b fallback, which proposed none of them.
- **Ignition:** gained the WSTF chamber pressure, the igniter diameter and the GRC slow flow.
- **PTFE:** meets the gate in this run (0.82 recall, 0.986 precision, 0 critical).

The gate (recall >= 0.80 stable across several sources) is not met. The miss diagnosis (`target_miss_diagnosis.md`) still applies: most misses are proposals rejected by a rule.

Latency per call (s), p50 / p90 / max, calls over 240 s:
- textiles: 17 / 221 / 221, 0
- regulator: 12 / 69 / 88, 0
- ignition: 22 / 55 / 123, 0
- PTFE: 27 / 245 / 279, 2

Only PTFE has calls over 240 s.

Local time this round is inflated, so it is not a clean measurement:
- The code is b4be17d, which predates the per-document computation below.
- The session profiled and replayed on the same machine while the runs went on.
- Textiles spent 1,390 s after its extraction, for a reason not established (`service.validate` takes 4–12 s on the same package). The run summary now records `post_extraction_seconds` to locate it.

Experiment outside evaluation B: textiles with `nvidia/nemotron-3.5-lightning-30b-a3b` as primary model.
- Result: 5/29 recall, 10/19 precision, 0 critical.
- Time: 112 s of extraction (4 calls, p90 32 s), against 331 s for the 120b.
- Conclusion: faster, but with lower recall and precision.

## Engineering after evaluation B (no change to criteria, scorer, ontology or targets)

These commits change no criterion, so the 46-input replay must stay identical:
- `ae420ab` computes a document's page titles, running headers, slide-deck reading and major sections once per document, and caches text normalization.
  - Profile (regulator r1 replay): before, `validate_output` took 508 of 538 s, with `running_headers` called 8,336 times (305 s); after, the replay took 16 s.
  - Replay of the 46 inputs: 4 min 18 s instead of about 40 min.
- `ae642ed` records each call's start and a per-run `timing` summary in `summary.json`. It covers provider seconds (overlapping calls counted once), local, setup and post-extraction seconds, failures by cause, p50/p90/max, calls over 240 s, tokens and the per-call detail.
- `3e746b1` adds window prefetch (`SCIENCE_WINDOW_CONCURRENCY`, default 3).
  - At the start of each stage, each window's first request is computed exactly as the sequential loop computes it, and up to three are sent ahead.
  - The loop is unchanged and merges in window order. It uses an answer only when its request is byte-for-byte identical, and otherwise calls itself.
  - SQLite and the merges stay on the main thread.
  - A rate limit stops sending ahead; the ordinary Retry-After backoff then applies.
  - Receipts count sent, used, discarded and cancelled requests.
- `09bef51`, `36a3fe6` add the Anthropic transport, selected only by `SCIENCE_PROVIDER=anthropic`. NVIDIA stays the default.

Proof:
- Replay of the 46 inputs after each commit gives a whole package identical to b4be17d, 46 of 46.
- `tests/test_window_prefetch.py`: concurrency 1 against 3 sends the same requests and yields the same records with overlapping calls; a 429 stops sending ahead.
- `tests/test_run_timing.py`: overlapping calls count once.
- `tests/test_anthropic_provider.py`: stand-in client, no live call.

## Pending

- Live pilot with the Anthropic transport (textiles with `claude-sonnet-5-5`, at concurrency 1 and 3, then `claude-opus-5-5`), outside evaluation B. Changing the primary model waits for Liam.
- Next batch from the miss diagnosis: rejected proposals, led by `QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT` (printed_name, now in the request) and `STATEMENT_REQUIRES_EXPERIMENTAL_SCOPE`.
- No live run was in progress at the shutdown of 2026-10-21 19:19 UTC; none was lost.
