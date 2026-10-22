# Feasibility of every frozen target (ignition, regulator, textiles)

Best state over all graded live runs:
- NVIDIA evaluation B of milestones 10–13;
- the Anthropic pilot (Sonnet and Opus);
- the three package 4 Sonnet rounds.

Classes come from the corrected `miss_diag` (value spans, table cells, lost windows), and the blocking class of each target never correct is judged from its frozen expectation and records (`../tools/feasibility_table.py`). Replay recoveries (point A, block 3b) are listed apart, since they are not live runs.

Receipts: `best_states_raw.json` (every run) and `feasibility.json`. 0 model calls.

Blocking classes: not proposed, wrong role, wrong subject, rejection (with its code), the schema lacks the role, contract against target, window lost.

## ignition (29 accessible targets, 11 graded runs)

| target | kind | best live state | blocking class | code | note |
|---|---|---|---|---|---|
| entities-01 | entities | CORRECT | reached live |  | correct in 11 of 11 runs |
| entities-02 | entities | CORRECT | reached live |  | correct in 11 of 11 runs |
| entities-03 | entities | CORRECT | reached live |  | correct in 11 of 11 runs |
| entities-04 | entities | CORRECT | reached live |  | correct in 11 of 11 runs |
| quantities-05 | quantities | CORRECT | reached live |  | correct in 10 of 11 runs |
| quantities-06 | quantities | CORRECT | reached live |  | correct in 6 of 11 runs |
| quantities-07 | quantities | PROPOSED_REJECTED | rejection | `QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT` | the dimensions are labelled with the object ('samples'); no dimension name is printed |
| quantities-08 | quantities | PROPOSED_REJECTED | rejection | `QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT` | as quantities-07 |
| quantities-09 | quantities | CORRECT | reached live |  | correct in 5 of 11 runs |
| quantities-10 | quantities | CORRECT | reached live |  | correct in 11 of 11 runs |
| quantities-11 | quantities | CORRECT | reached live |  | correct in 11 of 11 runs |
| quantities-12 | quantities | CORRECT | reached live |  | correct in 11 of 11 runs |
| quantities-13 | quantities | ACCEPTED_MISGRADED | rejection | `QUANTITY_SEMANTICS_OR_UNIT_UNRESOLVED` | the printed typo 'internal height if 30.5 cm' leaves the value unnamed; the validator is stricter than the expectation |
| quantities-14 | quantities | PROPOSED_REJECTED | reached in replay |  | point A (3.1) and block 3b fix 3 |
| quantities-15 | quantities | CORRECT | reached live |  | correct in 7 of 11 runs |
| quantities-16 | quantities | PROPOSED_REJECTED | wrong role |  | a cited estimate (Takahashi) proposed as a current reported quantity |
| quantities-17 | quantities | PROPOSED_REJECTED | rejection | `QUANTITY_SEMANTICS_OR_UNIT_UNRESOLVED` | a derived delta with no eligible subject |
| statements-18 | statements | PROPOSED_REJECTED | rejection | `CHANGING_OBSERVATION_IS_NOT_ESTABLISHED_CONFIGURATION` | the execution step held as a changing observation |
| statements-19 | statements | ACCEPTED_MISGRADED | wrong role |  | test coverage typed documentary context |
| statements-20 | statements | ACCEPTED_MISGRADED | wrong role |  | explicit uncertainty typed a condition or a conclusion |
| statements-21 | statements | ACCEPTED_MISGRADED | rejection | `STATEMENT_SUBJECT_APPLICABILITY_UNRESOLVED` | the whole sentence held on three specimen subjects; the accepted record is a cut fragment |
| statements-22 | statements | CORRECT | reached live |  | correct in 4 of 11 runs |
| statements-23 | statements | CORRECT | reached live |  | correct in 9 of 11 runs |
| statements-24 | statements | CORRECT | reached live |  | correct in 11 of 11 runs |
| statements-25 | statements | CORRECT | reached live |  | correct in 4 of 11 runs |
| relations-26 | relations | ACCEPTED_MISGRADED | wrong subject |  | WSTF hasCondition proposed to the primer flow, not the documented chamber configuration |
| relations-27 | relations | CORRECT | reached live |  | correct in 11 of 11 runs |
| quantities-28 | quantities | PROPOSED_REJECTED | rejection | `ORIGINAL_TABLE_QUANTITY_ROLE_AND_EXPERIMENTAL_SCOPE_REQUIRE_REVIEW` | a cited model-input table cell; math-font glyphs also unbind its unit |
| quantities-29 | quantities | PROPOSED_REJECTED | rejection | `ORIGINAL_TABLE_QUANTITY_ROLE_AND_EXPERIMENTAL_SCOPE_REQUIRE_REVIEW` | a derived table cell with its confidence role |

## regulator (32 accessible targets, 9 graded runs)

| target | kind | best live state | blocking class | code | note |
|---|---|---|---|---|---|
| entities-01 | entities | CORRECT | reached live |  | correct in 9 of 9 runs |
| entities-02 | entities | CORRECT | reached live |  | correct in 9 of 9 runs |
| entities-03 | entities | CORRECT | reached live |  | correct in 9 of 9 runs |
| entities-04 | entities | CORRECT | reached live |  | correct in 8 of 9 runs |
| entities-05 | entities | CORRECT | reached live |  | correct in 5 of 9 runs |
| entities-06 | entities | CORRECT | reached live |  | correct in 4 of 9 runs |
| quantities-07 | quantities | PROPOSED_REJECTED | wrong role |  | a transient model prediction typed a configuration or a measurement |
| quantities-08 | quantities | CORRECT | reached live |  | correct in 9 of 9 runs |
| quantities-09 | quantities | PROPOSED_REJECTED | rejection | `QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT` | '20uL was injected': unprinted label, and the test article (POR) as subject |
| quantities-10 | quantities | PROPOSED_REJECTED | rejection | `QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT` | '~100 mg/ft2 film coating' as a target loading, on the test article |
| quantities-11 | quantities | CORRECT | reached live |  | correct in 4 of 9 runs |
| quantities-12 | quantities | PROPOSED_REJECTED | rejection | `TEST_ARTICLE_ALIAS_EXPERIMENTAL_GROUP_SCOPE_REQUIRES_REVIEW` | the deliberate test-article alias hold |
| quantities-13 | quantities | CORRECT | reached live |  | correct in 4 of 9 runs |
| quantities-14 | quantities | CORRECT | reached live |  | correct in 4 of 9 runs |
| statements-15 | statements | PROPOSED_REJECTED | wrong role |  | a cited partial test typed a current observation |
| statements-16 | statements | PROPOSED_REJECTED | rejection | `STATEMENT_REQUIRES_EXPERIMENTAL_SCOPE` | the contaminant-selection configuration without a scope |
| statements-17 | statements | CORRECT | reached live |  | correct in 6 of 9 runs |
| statements-18 | statements | ACCEPTED_MISGRADED | rejection | `INFERRED_INTERPRETATION_IS_NOT_DIRECT_OBSERVATION` | the post-dry functional result held as an interpretation |
| statements-19 | statements | PROPOSED_REJECTED | rejection | `STATEMENT_SUBJECT_APPLICABILITY_UNRESOLVED` | a system-only adjustment: false on the POR, right at study scope |
| statements-20 | statements | CORRECT | reached live |  | correct in 1 of 9 runs |
| statements-21 | statements | CORRECT | reached live |  | correct in 1 of 9 runs |
| statements-22 | statements | CORRECT | reached live |  | correct in 2 of 9 runs |
| statements-23 | statements | CORRECT | reached live |  | correct in 3 of 9 runs |
| statements-24 | statements | CORRECT | reached live |  | correct in 7 of 9 runs |
| statements-25 | statements | CORRECT | reached live |  | correct in 2 of 9 runs |
| statements-26 | statements | PROPOSED_REJECTED | rejection | `STATEMENT_INCLUDES_A_RUNNING_PAGE_HEADER` | the running header glued to the sentence, or the test article as subject |
| statements-27 | statements | ACCEPTED_MISGRADED | wrong role |  | a Thermal Desktop model result typed a measurement or a conclusion |
| statements-28 | statements | CORRECT | reached live |  | correct in 8 of 9 runs |
| relations-29 | relations | CORRECT | reached live |  | correct in 9 of 9 runs |
| relations-30 | relations | CORRECT | reached live |  | correct in 1 of 9 runs |
| relations-31 | relations | CORRECT | reached live |  | correct in 1 of 9 runs |
| relations-32 | relations | CORRECT | reached live |  | correct in 1 of 9 runs |

## textiles (29 accessible targets, 12 graded runs)

| target | kind | best live state | blocking class | code | note |
|---|---|---|---|---|---|
| entities-01 | entities | CORRECT | reached live |  | correct in 12 of 12 runs |
| entities-02 | entities | ACCEPTED_MISGRADED | wrong subject |  | the fabric ('100% PBI knit fabric') proposed instead of the PBI material identity |
| entities-03 | entities | CORRECT | reached live |  | correct in 12 of 12 runs |
| entities-04 | entities | CORRECT | reached live |  | correct in 10 of 12 runs |
| quantities-05 | quantities | PROPOSED_REJECTED | contract against target | `QUANTITY_SUBJECT_NOT_IN_APPLICABLE_SOURCE` | the proposed Artemis atmosphere has no eligible experimental subject |
| quantities-06 | quantities | PROPOSED_REJECTED | contract against target | `QUANTITY_SUBJECT_NOT_IN_APPLICABLE_SOURCE` | as quantities-05 |
| quantities-07 | quantities | PROPOSED_REJECTED | contract against target | `QUANTITY_SUBJECT_NOT_IN_APPLICABLE_SOURCE` | as quantities-05 |
| quantities-08 | quantities | PROPOSED_REJECTED | schema lacks the role | `QUANTITY_SUBJECT_NOT_IN_APPLICABLE_SOURCE` | a historical mission atmosphere (Apollo): no historical-context subject or role |
| quantities-09 | quantities | PROPOSED_REJECTED | schema lacks the role | `QUANTITY_SUBJECT_NOT_IN_APPLICABLE_SOURCE` | as quantities-08 (Skylab) |
| quantities-10 | quantities | PROPOSED_REJECTED | schema lacks the role | `QUANTITY_UNIT_NOT_BOUND_TO_EXPRESSION` | a normative acceptance criterion value: quantities have no criterion role |
| quantities-11 | quantities | ACCEPTED_MISGRADED | rejection | `QUANTITY_SEMANTICS_OR_UNIT_UNRESOLVED` | the specimen composition '100% PBI' held unnamed |
| quantities-12 | quantities | CORRECT | reached live |  | correct in 12 of 12 runs |
| quantities-13 | quantities | CORRECT | reached live |  | correct in 12 of 12 runs |
| quantities-14 | quantities | CORRECT | reached live |  | correct in 10 of 12 runs |
| quantities-15 | quantities | CORRECT | reached live |  | correct in 10 of 12 runs |
| quantities-16 | quantities | PROPOSED_REJECTED | schema lacks the role | `QUANTITY_SUBJECT_NOT_IN_APPLICABLE_SOURCE` | an assessment target (design criterion) value |
| quantities-17 | quantities | PROPOSED_REJECTED | schema lacks the role | `QUANTITY_SUBJECT_NOT_IN_APPLICABLE_SOURCE` | as quantities-16 |
| statements-18 | statements | PROPOSED_REJECTED | contract against target | `SUPPORT_ONLY_IN_BACKGROUND_OR_ANALYSIS_SECTION` | held on the Background slide |
| statements-19 | statements | PROPOSED_REJECTED | contract against target | `NORMATIVE_ROLE_NOT_EXPLICIT_IN_SOURCE` | a pass criterion the slide does not print as one |
| statements-20 | statements | CORRECT | reached live |  | correct in 12 of 12 runs |
| statements-21 | statements | PROPOSED_REJECTED | wrong role |  | a permitted method typed guidance or configuration |
| statements-22 | statements | ACCEPTED_MISGRADED | reached in replay |  | point A (3.2) and block 3b fix 2 |
| statements-23 | statements | ACCEPTED_MISGRADED | wrong role |  | current development activities typed documentary context |
| statements-24 | statements | ACCEPTED_MISGRADED | reached in replay |  | block 3b fix 2 |
| statements-25 | statements | CORRECT | reached live |  | correct in 12 of 12 runs |
| statements-26 | statements | CORRECT | reached live |  | correct in 6 of 12 runs |
| statements-27 | statements | ACCEPTED_MISGRADED | schema lacks the role |  | a stated goal: no goal or plan role |
| relations-28 | relations | CORRECT | reached live |  | correct in 3 of 12 runs |
| relations-29 | relations | CORRECT | reached live |  | correct in 1 of 12 runs |

## Ceiling by source

| source | accessible | live union | + replay | + every rejection fixed | + every model-side miss fixed | needs Liam (schema, contract) | needed for 0.80 |
|---|---|---|---|---|---|---|---|
| ignition | 29 | 16 (0.55) | 17 (0.59) | 25 (0.86) | 29 (1.00) | 0 | 24 |
| regulator | 32 | 22 (0.69) | 22 (0.69) | 29 (0.91) | 32 (1.00) | 0 | 26 |
| textiles | 29 | 12 (0.41) | 14 (0.48) | 15 (0.52) | 18 (0.62) | 11 | 24 |

How to read it:
- **Live union** is what some live run reached; no single run reached it.
- **+ every rejection fixed** assumes each held proposal was right as proposed. Several are correct holds by the contracts (see the notes), so it is an upper bound.
- **+ every model-side miss fixed** also assumes the model proposes the right role and subject. Only a request change, measured live, can show that.
- **The rest** needs Liam: roles the schema lacks, and contracts the frozen targets contradict.
