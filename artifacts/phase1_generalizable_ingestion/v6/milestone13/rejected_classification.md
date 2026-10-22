# Package 1.2: the 69 rejected target-run pairs classified A / B / C

These are the milestone 12 live runs (r1 and r2 on ignition, regulator and textiles) whose target was proposed by the model but rejected by a rule (`target_miss_diagnosis.json`). Each target is classified by the branch author against the printed source text, following addendum §1:
- **A:** unsupported as proposed (wrong role, wrong sentence, wrong subject); the rejection is correct and must stay.
- **B:** source-supported, but rejected because a representation, name, unit or role contract is too restrictive; fix with a general mechanism.
- **C:** valid evidence whose association (subject, experimental scope, role between two readings, or a relation's applicable context) is incomplete; recover it through the evidence-grounded workflow.

**Totals (target-run pairs):** A 19, B 20, C 30, of 69 (targets: A 12, B 12, C 19, of 43).

**Package each class feeds:**
- **B →** 3.1 (unprinted names), 3.3 (units in table column headers and glyphs, page headers inside statements, normative role from list structure), and the configuration and comparison role holds (3.2).
- **C →** 3.2 (subject and scope), 3.3 (relation applicable context), and role-conflict resolution.
- **A →** stays rejected. These are model typing errors that a better request or targeted recovery (3.5) may avoid; no rule is relaxed for them.

| source | target | runs | class | governing code | reason |
|---|---|---|---|---|---|
| ignition | quantities-06 | 1 | C | `CONFLICTING_ROLE_PROPOSALS_FOR_SAME_SOURCE_SPAN` | two proposals give the same printed value both roles; the configuration reading is held by the role conflict |
| ignition | quantities-14 | 2 | B | `QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT` | correct configuration and subject; the label is not printed, the clause prints 'rotated at' |
| ignition | quantities-15 | 1 | B | `QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT` | correct value and subject; the printed name is 'slow flow', the label 'ignition flow velocity' is not printed |
| ignition | quantities-16 | 1 | A | `EXPLICIT_DERIVATION_IS_NOT_REPORTED_MEASUREMENT` | a cited 1-g estimate proposed as a reported quantity of the study; rejection correct |
| ignition | statements-18 | 2 | B | `CHANGING_OBSERVATION_IS_NOT_ESTABLISHED_CONFIGURATION` | a printed execution configuration (two samples per drop) held as a changing observation |
| ignition | statements-19 | 2 | C | `STATEMENT_SUBJECT_APPLICABILITY_UNRESOLVED` | experiment coverage sentence; subject and role left open |
| ignition | statements-20 | 2 | A | `DERIVED_IS_NOT_OBSERVATION` | the proposal is another sentence (plot description) typed observation; the target sentence was not proposed as such |
| ignition | statements-22 | 1 | A | `OPEN_QUESTION_NOT_EXPLICIT_IN_SOURCE` | a tentative, non-causal statement proposed as an open question |
| ignition | statements-25 | 2 | C | `STATEMENT_SUBJECT_APPLICABILITY_UNRESOLVED` | tentative conclusion proposed with the right role in one reading; its subject applicability is unresolved |
| ignition | quantities-28 | 2 | B | `QUANTITY_UNIT_NOT_BOUND_TO_EXPRESSION` | table cell whose unit is printed in its column header (rho (kg/m3)); the unit is not bound to the cell value |
| ignition | quantities-29 | 2 | B | `QUANTITY_UNIT_NOT_BOUND_TO_EXPRESSION` | table cell whose unit is printed in its column header; the unit is not bound |
| ignition | statements-21 | 1 | B | `DERIVED_IS_NOT_OBSERVATION` | a reported comparison of a measured limit with an extrapolated one, held as derived rather than observed |
| regulator | quantities-07 | 2 | C | `QUANTITY_SUBJECT_NOT_IN_APPLICABLE_SOURCE` | model prediction proposed as derived with the right role; its subject is not in the applicable source |
| regulator | quantities-09 | 1 | B | `QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT` | correct configuration and subject; the label is not printed, the clause prints 'was injected' |
| regulator | quantities-10 | 1 | C | `QUANTITY_SUBJECT_NOT_IN_APPLICABLE_SOURCE` | printed 'film coating' value preserved; its subject is unresolved |
| regulator | statements-15 | 2 | C | `STATEMENT_REQUIRES_EXPERIMENTAL_SCOPE` | a cited partial test with a tentative reading; current or cited scope unresolved |
| regulator | statements-16 | 2 | C | `STATEMENT_REQUIRES_EXPERIMENTAL_SCOPE` | configuration sentence (dodecane chosen); experimental scope unresolved |
| regulator | statements-19 | 2 | C | `STATEMENT_SUBJECT_APPLICABILITY_UNRESOLVED` | system-only measurement before reconnection; its subject must be the test system, unresolved |
| regulator | statements-20 | 1 | A | `UNCERTAINTY_CANNOT_BECOME_CONFIRMED` | a tentative explanation proposed as a confirmed conclusion or observation; rejection correct |
| regulator | statements-22 | 2 | B | `STATEMENT_INCLUDES_A_RUNNING_PAGE_HEADER` | correct observation sentence held because the running page header and a figure caption were included in the span |
| regulator | statements-24 | 1 | C | `STATEMENT_SUBJECT_APPLICABILITY_UNRESOLVED` | separate demonstration after disconnection; subject and role conflict unresolved |
| regulator | statements-25 | 1 | C | `AUTHOR_ROLE_REQUIRES_CONTEXT_REVIEW` | measurement limitation; author role and subject unresolved |
| regulator | statements-26 | 2 | B | `STATEMENT_INCLUDES_A_RUNNING_PAGE_HEADER` | correct finding held because the running page header was included |
| regulator | statements-28 | 1 | C | `CONFLICTING_ROLE_PROPOSALS_FOR_SAME_SOURCE_SPAN` | author conclusion proposed as both conclusion and observation; held by the role conflict |
| regulator | relations-30 | 1 | C | `RELATION_SUBJECT_OBJECT_NOT_IN_APPLICABLE_SOURCE` | the series hasMaterial dodecane is printed; the applicable source context was not reconstructed |
| regulator | relations-31 | 2 | C | `RELATION_SUBJECT_OBJECT_NOT_IN_APPLICABLE_SOURCE` | first wet series with dodecane; applicable context not reconstructed |
| regulator | relations-32 | 2 | C | `RELATION_SUBJECT_OBJECT_NOT_IN_APPLICABLE_SOURCE` | second wet series with its own injection; applicable context not reconstructed |
| regulator | statements-21 | 1 | B | `CONFIGURATION_ROLE_NOT_ESTABLISHED_IN_ORIGINAL_PASSAGE` | a printed controlled adjustment (configuration change) held because the configuration role is not established |
| regulator | statements-27 | 1 | C | `AUTHOR_ROLE_REQUIRES_CONTEXT_REVIEW` | post-test model result; its author role is unresolved |
| textiles | quantities-05 | 2 | A | `QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT` | a proposed atmosphere proposed as a reported measurement; rejection correct |
| textiles | quantities-06 | 2 | A | `CONFIGURATION_OR_DERIVED_IS_NOT_MEASUREMENT` | a proposed atmosphere proposed as a reported measurement; rejection correct |
| textiles | quantities-07 | 2 | A | `CONFIGURATION_OR_DERIVED_IS_NOT_MEASUREMENT` | a contingency test concentration proposed as a reported measurement; rejection correct |
| textiles | quantities-10 | 2 | B | `QUANTITY_UNIT_NOT_BOUND_TO_EXPRESSION` | normative bound with an inch glyph that the unit reader does not bind |
| textiles | statements-18 | 2 | C | `STATEMENT_REQUIRES_EXPERIMENTAL_SCOPE` | qualified state-of-art claim; scope and subject unresolved |
| textiles | statements-19 | 2 | B | `NORMATIVE_ROLE_NOT_EXPLICIT_IN_SOURCE` | a criterion printed as an item of a test-criteria list; its normative role comes from that list structure, which the rule does not read |
| textiles | statements-21 | 2 | A | `CONFIGURATION_ROLE_NOT_ESTABLISHED_IN_ORIGINAL_PASSAGE` | a permitted method proposed as an experimental condition; rejection correct |
| textiles | statements-22 | 2 | C | `STATEMENT_REQUIRES_EXPERIMENTAL_SCOPE` | author-reported comparison; experimental scope unresolved |
| textiles | statements-23 | 2 | C | `STATEMENT_SUBJECT_APPLICABILITY_UNRESOLVED` | development activity statement; subject unresolved |
| textiles | statements-24 | 2 | A | `GUIDANCE_NOT_EXPLICIT_IN_SOURCE` | a future certification plan proposed as guidance or an experimental condition; rejection correct |
| textiles | statements-27 | 2 | A | `SOURCE_GOAL_IS_NOT_ESTABLISHED_RESULT` | a stated goal proposed as an established conclusion; rejection correct |
| textiles | relations-28 | 1 | A | `LOCAL_SUBJECT_BINDING_UNRESOLVED` | the material relation proposed from the investigation, not from the fabric sample; rejection correct |
| textiles | quantities-16 | 1 | A | `QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT` | a minimum target environment proposed as a reported measurement; rejection correct |
| textiles | quantities-17 | 1 | C | `QUANTITY_SUBJECT_NOT_IN_APPLICABLE_SOURCE` | target pressure preserved; its subject unresolved |
