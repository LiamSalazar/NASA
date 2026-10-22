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
