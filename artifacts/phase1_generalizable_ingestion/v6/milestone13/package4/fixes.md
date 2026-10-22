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
