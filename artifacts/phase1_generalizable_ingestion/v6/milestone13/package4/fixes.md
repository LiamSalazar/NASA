# Fixes from the package 4 miss diagnosis (block 3b)

Ranked in `target_miss_diagnosis.md`. Diego's working rule applies: no live runs until the replay meets the threshold. Each fix is therefore measured by an offline replay with 0 model calls, never by new inference.
- **Replay set:** the six Sonnet packages at `a6d967b` (`package4/*_sonnet_a6d967b_r{1,2}`) and the four NVIDIA round B packages (`*_live_b4be17d_r1`).
- **Baseline:** the same set replayed at `a72a0cb`, the code before these fixes.
- **Changed records** come from `../nasa-live/replay/diff.py` and are judged one by one against the printed source.
- **Fix 7** (one test article named by its acronym) is not done: it touches the applicability contract and waits for Liam.

## Fix 2: a running footer after a whole sentence closes it

- **Classification:** document structure.
- **Motivating source:** textiles (slide deck). Statements-22 carried the footer "55th International Conference on Environmental Systems / July 12-16, 2026 / 5" and the slide's next block.
- **Rule** (`page_edge_suffix`, `page_edge_lines`):
  - Inside a statement, a line that is a running header or footer of the document ends the statement.
  - The footer's companion lines (page numbers, and any line repeated at the edge of most pages, such as the date) go with it, together with what follows.
  - Two conditions apply: what comes before must have at least five words, and what follows must not continue the sentence (nothing, or an uppercase or bullet start).
  - The statement and its support end before the footer (`page_edge_removed_after`).
  - A sentence that runs on in lowercase across a page break is not cut; the existing header hold applies to it.
  - No source text, name or value is listed.
- **Tests:** `tests/test_page_edge_suffix.py` (6). Positive: footer, date, page number and next block; footer at the end. Metamorphic: with and without the date line. Negative: continued sentence, short fragment, no footer, a line printed on few pages.
- **Replay effect:**
  - Records change only on textiles: 2 to 8 statements per package lose the footer from their text. No status changes on any source.
  - Ignition, regulator and PTFE are papers: 0 records changed in any of their 6 Sonnet and 3 NVIDIA packages.
- **Judgments of the changed supported records:**
  - Sonnet 2f8bd3b1, in r1 and r2, is now the slide's own comparative finding: correct. **Textiles statements-22 recovered in both runs.**
  - Sonnet 71823c4e (r2), "Certification testing will be performed at White Sands Test Facility (WSTF)", is a planned activity as documentary context, with no execution claimed: correct. **Textiles statements-24 recovered in r2.**
  - NVIDIA 3047b24d still carries the slide's figure labels ("Ignitor Test specimen Metal shield"): still incorrect.
- **Result:**
  - textiles recall 10 → 11/29 (r1) and 10 → 12/29 (r2);
  - textiles precision 20/22 → 21/22 (r1) and 20/27 → 22/27 (r2);
  - other sources unchanged; 0 critical.
- **Mark: single-source, suspect.** Textiles is the only slide deck in the development set, so no other source can confirm the rule. Ignition's title-block records (070d8288, 93638799) are a different mechanism: an author block, not a footer. They are not addressed.

## Fix 3: a label that is the value's own setting verb is named by it

- **Classification:** semantic with evidence. It closes a gap in 3.1: `printed_setting_name` ran only when the model's label was not printed.
- **Motivating source:** ignition quantities-14 ("the chamber was rotated at 20.4 RPM"). Sonnet labels the value "rotated", which is printed, so the setting-verb rule never ran and the staged-name syntax then held the value.
- **Rule:**
  - When the label is printed and `printed_setting_name` finds it is the verb that sets the value, the verb is the value's name (`PRINTED_SETTING_VERB_NAMES_VALUE`).
  - A label that is the verb cannot vouch for itself. The verb must therefore be a form of a noun of the unit's own dimension, from the existing `DIMENSION_NOUNS` ("rotation" for a rotational speed): `setting_verb_of_unit_dimension`. No verb list.
- **Tests:** `tests/test_setting_verb_name.py` (+7).
  - Positive: "rotated" at 20.4 RPM.
  - Metamorphic: the printed verb and its spelled-out label give the same outcome.
  - Negative: "cleaned" at the same value; "injected" for a volume, which is no form of a volume noun; a reported measurement; a conditional clause.
- **Replay effect (against fix 2):** one record changes on each ignition Sonnet package, `rotated = 20.4 RPM` on the GRC group, UNRESOLVED → SOURCE_SUPPORTED. It is correct: the GRC chamber's rotation before the drop. 0 records change on the other 10 packages.
- **Result:**
  - ignition recall 13 → 14/29 (r1) and 12 → 13/29 (r2); precision 71/85 → 72/86 and 63/76 → 64/77;
  - other sources unchanged; 0 critical.
- **Mark: single-source, suspect.** No other source has a value labelled by its own setting verb. Regulator's "20uL was injected" is not named, because "injected" is no form of a volume noun, and it stays held by its subject anyway.

## Fix 5: the token brake releases a connection that failed before any response

- **Classification:** orchestration (spending brake). No scientific rule changes.
- **Motivating run:** ignition `a6d967b` r2.
  - Two identity calls failed on the network after 38 s, with no content and no usage.
  - Their reservations stayed counted: 435,595 tokens reserved against 320,168 used.
  - A propositions window (71k reserved) was then `DEFERRED_BUDGET`, and statements-23 and -25 were lost.
- **Rule:** a failure of kind `network` with no usage and no received content releases its reservation, as a refusal before processing already does (`a6d967b`).
  - Any failure that received part of a response keeps its reservation, since it may be billed.
  - So do timeouts and every other kind.
  - The brake stays a spending ceiling and never truncates a request.
- **Tests:** `tests/test_request_schema_references.py` (+2). Positive: a connection error before any response frees its reservation. Negative: a timeout keeps it. Existing negative: other failures keep it.
- **Replay effect:** none by construction. The replay calls no provider, so 0 records change.
- **Expected live effect, not measured:** with the two reservations released, ignition r2 would have been at about 320k when it reached the deferred window, and the 71k window would have been sent. Whether statements-23 and -25 are then recovered depends on the model, as in r1, where they were. A live run is needed to measure it, and Diego's rule leaves that until the replay passes.
- **Caveat:** a connection that dropped while the provider was still reading the input could in principle be billed for input tokens. The receipts record the reservation released and the real usage, so any difference would show in the per-call cost.

## Fix 1: a caption that prints its data as taken during a named test series names that group

- **Classification:** document structure (a printed-structure candidate, as in milestone 8).
- **Motivating source:** regulator. Sonnet proposes the test article (POR s/n 003) and one dry group, but not the printed series, which NVIDIA did propose.
  - The diagnosis shows its values and statements held by the specimen applicability contract.
  - The series are named in figure captions: "Figure 11 - ... During the First Dodecane Wetted POR Interstage Impact Test Series".
- **Rule** (`structure_entity_candidates`):
  - A figure or table caption (`PRINTED_CAPTION_LINE`, with its wrapped next line) that prints "During (the) <three or more words> Series/Test Series/Tests/Runs" proposes that phrase as a current `ExperimentFamily` candidate, supported by the caption.
  - A caption that cites a source ("(3)", "[2]", "from (", "et al.") proposes nothing.
  - A group already proposed keeps its record, unless its name is shared by two or more printed series ("Wetted … Test Series" inside "First …" and "second …"). In that case the printed series are distinct and both are proposed.
  - Candidates are validated like any proposal and never become facts by themselves. No source name or value is listed.
- **Tests:** `tests/test_caption_test_series.py` (4).
  - Positive: three series, one of them wrapped onto the next line.
  - Negative: a cited caption, a caption without "During", a two-word name.
  - A proposed group keeps its record.
  - Metamorphic: a name two series share against a name only one contains.
- **Replay effect (against fix 3):** only regulator Sonnet changes. 0 records change on the other 9 packages, including NVIDIA's regulator, whose own series groups make the candidates redundant.
  - **r1:** +3 groups (the dry series, the first and the second wet series). The existing figure-reference scoping (`EXPLICIT_ORIGINAL_FIGURE_GROUP_REFERENCE`) then binds three impact-time values to their own series: ~360 msec dry, 137–148 msec first wet, 46–49 msec second wet. All six are correct.
  - **r2:** +3 groups and the dry ~360 msec value, all correct. Three records the adjudication judged incorrect leave the active set, because their subject was the model's group merging both wet series: two impact-time values and "The impact times ranged from 137-148 msec (Figure 11)". The merged group itself stays active and incorrect.
  - **Judged strictly:** the model's "60 dry pneumatic impact tests" is now a duplicate name of the printed "Sixty O2 Wetting Dry Impact Tests" in both runs, so it counts as incorrect.
- **Result:**
  - regulator recall 9 → 14/32 (r1: entities-05 and -06, quantities-11, -13 and -14) and 8 → 11/32 (r2: entities-05 and -06, quantities-11);
  - precision 31/34 → 36/40 (r1) and 29/36 → 32/37 (r2);
  - 0 critical.
- **Mark: single-source, suspect.** No other development source prints a test series in a caption, and the other 9 packages are unchanged.

## Fixes 4 and 6: not implemented, with reason

- **Fix 4** (dimension notation "A by B object", ignition quantities-07 and -08). Sonnet labels both values "samples", which names the object, not the dimension.
  - A rule could recognize the notation, but the value would then stand under a label that names no quantity.
  - Recovering the targets would need an unprinted name ("width", "length") written in for the model, which the contracts forbid.
  - The earlier adjudication judged such labels incorrect ("label 'OD ceramic rod' (fragment)"), so the targets would stay missed.
- **Fix 6** (math-font glyphs in table labels, ignition quantities-28). Table 1 prints model inputs from cited literature ("PMMA 21,22", "Nomex 23"). Sonnet proposes them as current reported quantities of the study's PMMA.
  - Repairing the glyphs would let the units bind, but the role would still be wrong. The best correct outcome is a hold, not recall.
  - The glyph repair itself would need a table specific to one font's broken mapping (Ethiopic syllables for brackets, Oriya letters for superscript digits), which is an overfitting risk.
  - Left as a detected, unaddressed item.

## Replay after fixes 2, 3, 1 (and 5): before and after, per source

- **Same inputs, 0 model calls.**
  - "Before" is the replay at `a72a0cb`, which is identical record for record to the live `a6d967b` packages (0 changes on all 8).
  - "After" is HEAD with fixes 2, 3, 1 and 5. Fix 5 has no replay effect.
- **Precision** is the record-by-record adjudication with the changed records judged above.
- **PTFE** is unchanged in every package, so its official scorer figures stand.
- **NVIDIA round B** changes only in the text of textiles statements, with no status change, so its point A adjudication stands.
- **Record changes:** `replay_fixes/record_changes_a72a0cb_to_fixes.txt`.

| source | Sonnet r1 before → after | Sonnet r2 before → after | NVIDIA round B (point A) before → after |
|---|---|---|---|
| PTFE | 28/34, 100/101 → same | 28/34, 117/119 → same | 28/34, 134/136 → same |
| ignition | 13/29, 71/85 → **14/29, 72/86** | 12/29, 63/76 → **13/29, 64/77** | 16/29, 86/114 → same |
| regulator | 9/32, 31/34 → **14/32, 36/40** | 8/32, 29/36 → **11/32, 32/37** | 11/32, 21/30 → same |
| textiles | 10/29, 20/22 → **11/29, 21/22** | 10/29, 20/27 → **12/29, 22/27** | 8/29, 19/23 → same |
| pooled recall | 60/124 = 0.48 → 67/124 = 0.54 | 58/124 = 0.47 → 64/124 = 0.52 | 63/124 = 0.51 → same |
| critical | 0 → 0 | 0 → 0 | 0 → 0 |

**Historical negatives** (`replay_fixes/historical_negatives_receipt.json`, `review_tools/exposed_compare.py` on the seven v4/v5 receipts replayed at HEAD): 29 checked, 0 critical regressions, 1 known non-critical still supported. Unchanged from point A.

**Threshold under Diego's rule** (recall ≥ 0.80 and precision ≥ 0.95 per source, 0 critical): **not met.**
- Only PTFE passes: 0.82 recall; 0.99 and 0.98 precision.
- Ignition is at 0.45–0.48 recall and 0.83–0.84 precision.
- Regulator is at 0.34–0.44 recall and 0.86–0.90 precision.
- Textiles is at 0.38–0.41 recall and 0.81–0.95 precision.
- So no live run is proposed.
- Fixes 1, 2 and 3 each help only the source that motivated them (marked "single-source, suspect"). The remaining gap is mostly model-side: roles, group equivalence, and values without an eligible subject (`target_miss_diagnosis.md`).

### Fix 5, restricted (after the independent review)

"No response arrived" does not prove "not billed": the provider may have received and processed a request whose connection was then reset or cut.
- **New rule:** the reservation is released only when the error chain proves the request never left this machine. That means an `httpx.ConnectError` or `httpcore.ConnectError` (name resolution, a refused connection, a TLS handshake failure), all raised before the body is sent. Both providers then record `request_not_sent` (`scientific_provider.request_never_sent`).
- **Kept:** a reset, a read or protocol error after connecting, and a timeout all keep the reservation, even with no response byte. A refusal before processing (HTTP 400) still releases it.
- **Tests:** `tests/test_request_schema_references.py`.
  - Positive: a connect error.
  - Negative: a read error, a protocol error, a timeout.
  - Unit: the error-chain check.
- **Effect on ignition r2:** its two network failures (38 s each, no detail recorded) would not be proven unsent, so they would keep their reservation as before. The deferred window there is not recovered by this fix.

## Anthropic request size and output floor (Diego's decision, 2026-10-22 17:18 UTC)

- **Request size** (`5c4676b`). Anthropic requests get their own limit before a window is split: `request_context_limit`, 96,000 estimated tokens by default, overridable with `ANTHROPIC_SCIENCE_REQUEST_CONTEXT_TOKENS`.
  - Windows (`segment_size`), shared context and NVIDIA's `ProviderEnvelope` are unchanged, so every unsplit request is byte-identical. Only the split decision changes.
  - Every split window of the 15 Anthropic runs was estimated at 68k–78k tokens (maximum 77,517), so all of them now go whole.
  - The coordinator's simulation of the same decision at 131,072 found:
    - the 8 context splits per round disappear (PTFE 2, ignition 3, regulator 3);
    - calls fall from 39 to 33;
    - cost falls by about 0.10 USD per round (about 2.17–2.19 USD);
    - the brake counter peaks at about 337k of 500k.
  - 96,000 gives the same outcome on these sources, with a lower cap.
  - The limit is recorded as `resource_policy.request_context_tokens` and in the live-run receipt.
- **Output floor** (this commit). `MIN_MAX_TOKENS` comes from `ANTHROPIC_SCIENCE_MIN_MAX_TOKENS`, default 32,768 instead of 64,000.
  - The largest Sonnet output seen was 9,463 tokens with thinking, and 0 of 126 attempts were cut for length.
  - Below the stage capacity, the truncation ladder (doubling `max_tokens`) can work again.
  - The worst-case cost per call falls from about 0.64 to about 0.33 USD.
- **Discarded prefetches** (this commit). A request sent ahead whose answer is not used is now recorded in the attempts with its usage, and counts toward the brake (`record_discarded_prefetch`). One never sent is cancelled and not recorded. The cost in receipts is then complete; ignition at `dc6f342` probably had 2 unrecorded.
- **Unchanged:** the envelope's output tokens (32,768), the per-run brake (500,000) and NVIDIA's defaults.
- **Replay:** the 12 saved packages give 0 record changes.
- **Tests:** `tests/test_request_context_limit.py` (3), `tests/test_discarded_prefetch.py` (3), `tests/test_anthropic_provider.py` (floor).

## Fix 8: a heading's outline marker copied into a label is not part of the name

- **Classification:** document structure.
- **Motivating source:** ignition, package 5 round 1. The model labelled the GRC group "B. NASA Glenn Research Center (GRC) Partial Gravity Testing", copying the heading's outline letter. The label was not in its support (`ENTITY_LABEL_ABSENT_FROM_SUPPORT`), so the group was rejected.
- **Rule** (`heading_outline_name`):
  - When a label equals a printed heading with its outline marker ("B.", "2.1", "IV."), the record keeps the printed name without the marker (`label_normalization`, basis `HEADING_OUTLINE_MARKER_IS_NOT_PART_OF_THE_NAME`).
  - The marker counts only if another heading of the document has a marker of the same kind (A./B., 2.1/2.2, III./IV.). A lone initial ("J. Smith Apparatus") or a letter inside the name ("Type A Tests") is kept.
  - A marker the heading does not print is never dropped.
  - No label is invented.
- **Tests:** `tests/test_heading_outline_marker.py` (5).
  - Metamorphic: B., 2.1 and IV., with and without the marker.
  - Negative: a lone initial, a letter inside a name, a marker not printed.
- **Replay:** all 20 saved packages (package 4 Sonnet, round B NVIDIA, package 5 Sonnet); only ignition changes.
  - **Package 5 r1:** the GRC group is accepted, which recovers **entities-02**. The WSTF group labelled "A. ..." becomes one record with the unlettered one. Recall 9 → 10/29, precision 75/90 → 76/91. The GRC chamber values stay on the investigation, because the model proposed them there, so quantities-11, -12, -15 and relations-27 are not recovered.
  - **Package 5 r2 and package 4 r1:** the lettered copies merge with the unlettered groups. The active set is unchanged.
  - Other sources: 0 changes.
- **29 historical negatives:** 0 critical regressions, 1 known non-critical (`../package5/historical_negatives_outline.json`).
- **Mark: single-source, suspect.**

## Spending brake: requests sent ahead obey it (independent review, 2026-10-22)

- **Problem:** `prefetch()` sent the first request of each window of a stage without `available()`. It reserved no tokens and counted no call when it sent, so the per-run brake stopped only the foreground.
  - With a network-free client billing 10,000 tokens per call, 12 sections, `segment_chars=1000` and `max_total_tokens=30000`, concurrency 3 sent 72 calls (720,000 tokens) where concurrency 1 sent 2.
  - The tests did not see it because `tests/conftest.py` sets concurrency 1.
  - Live runs did not reach it: the peak was 346k of 500k.
- **Fix** (orchestration):
  - **Sending ahead:** a request goes ahead only if `available()` admits it, and its reservation and call are counted when it is sent. At the brake or the call limit nothing more is sent ahead.
  - **Its own turn:** the foreground recognizes the identical request already sent (`ahead_reserved`) and does not count it again.
  - **Cancelling:** a request sent ahead and cancelled before leaving releases its reservation.
  - **Discarding:** a discarded request that left keeps its reservation, adjusted to its billed usage when known. A failure keeps it (it may have been billed) unless the error proves it never left (`request_not_sent`). `record_discarded_prefetch` now returns how the request settled.
  - **Anthropic reservation:** the reserved output is `max(capacity, MIN_MAX_TOKENS)`, which is what is sent as `max_tokens`. NVIDIA is unchanged. The context estimate, and so the split decision, is unchanged.
- **Frozen check** (`scripts/run_phase1_scientific_validation.py`, `inference_configuration`):
  - For Anthropic it records Anthropic's model, fallbacks, effort, endpoint (`ANTHROPIC_BASE_URL`), request limit and `max_tokens` floor, so an Opus fallback or a higher effort stops a frozen run and an NVIDIA-only change does not.
  - NVIDIA's dictionary is unchanged.
  - The script gains `--max-total-tokens`, 500,000 by default for Anthropic, recorded in its summary.
- **Tests:**
  - `tests/test_prefetch_brake.py` (3):
    - at concurrency 3 the billed total stays under the brake;
    - nothing is sent ahead at the brake;
    - with an unreached brake, concurrency 1 and 3 send the same requests and give the same records.
    - The first two fail on `effcb21`.
  - `tests/test_discarded_prefetch.py` (4).
  - `tests/test_frozen_inference_configuration.py` (4).
- **Equivalence with `effcb21`:** the synthetic run with an unreached brake gives byte-identical records and the same request multiset at concurrency 1 and 3, on both commits.
- **Replay:** no effect by construction, since validation is unchanged.
