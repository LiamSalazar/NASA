# New propositions request (prepared, not yet run)

Two changes to what the model is asked. Neither changes validation, so the replay of saved outputs is unchanged by construction. Their effect can only be measured live.

## 1. Statement role card (on)

`STAGE_INSTRUCTIONS["propositions"]` now defines the ten statement roles of the schema, each with an invented example. It is not a keyword list: no example comes from a development source or the holdout (`tests/test_prompt_has_no_source_phrases.py`). The card states the rules:
- a plan, a goal or a status claim is never `documentary_context`;
- what the source says is not known is `open_question`;
- an answer offered while asking for more work is `tentative_interpretation`;
- a conclusion about the authors' own work is `author_reported_conclusion`.

Tests: `tests/test_statement_request.py` checks that every role of the schema is defined.

## 2. Admissible subjects per statement anchor (implemented, **off**)

With `SCIENCE_ADMISSIBLE_SUBJECTS=1`, each in-task statement anchor carries `admissible_subjects`: the known subjects its own passage admits, narrowest first (`admissible_statement_subjects`). These are the same tests the validator applies to a proposed subject: `applicable` or `document_statement_scope`. The pattern is the one quantities already use (`source_applicable_subjects`). The default is off.

**Free prejudgment** (0 model calls, `../tools/prejudge_admissible.py`, receipt `prejudge_admissible_subjects.json`):
- **Method:** each saved package was replayed at HEAD. For each statement held only by subject applicability (`STATEMENT_SUBJECT_APPLICABILITY_UNRESOLVED` or `STATEMENT_REQUIRES_EXPERIMENTAL_SCOPE`), the narrowest admissible subject replaced the model's, as if chosen from the menu, and the statement was revalidated.
- **Statements freed:** PTFE 6, 5, 5 (Sonnet r1, r2, NVIDIA round B); ignition 5, 2, 2; regulator 13, 17, 30; textiles 0, 0, 0. No record of another kind changed.
- **PTFE judged record by record:**
  - Sonnet r1, 6 freed, all correct: the post-test photo observations, "Two additional batches ... zero reactions", and the resin description as documentary context. Precision 100/101 → 106/107.
  - Sonnet r2, 5 freed, all correct. Precision 117/119 → 122/124.
  - NVIDIA round B, 5 freed, 2 correct and 3 incorrect. Precision 134/136 → 136/141 = 0.965, with 3 new errors:
    - "This paper will compare ..." gets the narrowest subject Algoflon®, narrower than what it states;
    - "Existing Data Library The data used ..." carries its heading;
    - "two types of Algoflon® were tested" is an execution typed documentary context.
- **Bar, agreed before the prejudgment:** the menu stays off if PTFE precision falls below 0.978, or gains more than one new error in a run. It fails on the NVIDIA PTFE package, so **the menu stays off**.
- **Also seen:**
  - Taking the narrowest subject puts a condition or a material on abstract-level documentary sentences (ignition "lunar gravity", regulator "dodecane").
  - The regulator gains are large and mostly plausible, for example statements-17 on the printed "Sixty ..." series, and -20, -23, -25. But they include the 80–93 msec sentence (statements-19) at study scope, and the SOP history on "dodecane".
  - The ordering would need to depend on the role (the study for documentary context) before it is reconsidered.

## Anthropic request size

Not changed here. Diego decided it at 17:18 UTC, and the coordinator is computing the values; it is to be a separate Anthropic envelope that does not touch NVIDIA's defaults.
