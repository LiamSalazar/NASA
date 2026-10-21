# Milestone 13: diagnosis of each missed target (ignition, regulator, textiles)

Built from the milestone 12 evaluation B runs at `0a5a860` (r1 and r2) and their
offline replays at milestone 13 code (0 model calls). Each accessible frozen v4 target
that the run's adjudication (`milestone12/evaluation_b.json`) did not count correct
gets one class:

- **window lost**: no finished model request carried the target's printed words;
- **not proposed**: no record of the target's kind overlaps the target span;
- **proposed and rejected**: records of the kind overlap it, none SOURCE_SUPPORTED
  (the most frequent first reason code is shown);
- **accepted, graded wrong**: a SOURCE_SUPPORTED record overlaps it, but the
  adjudication did not count it correct (wrong subject, value, role or type).

Overlap is by evidence span, so a rejected record that only shares the sentence
counts as a proposal for the target. This is a diagnosis aid, not a scorer, and does
not change any frozen target or adjudication.
The milestone 13 replay of the same inputs gives the same class for every target,
since corrections 2 and 3 only remove records.

## Summary (target-run pairs, live milestone 12)

| source | correct r1 / r2 | not proposed | proposed and rejected | accepted, graded wrong | window lost |
|---|---|---|---|---|---|
| ignition | 11/29 / 14/29 | 3 | 19 | 11 | 0 |
| regulator | 14/32 / 17/32 | 3 | 25 | 5 | 0 |
| textiles | 10/29 / 10/29 | 7 | 25 | 6 | 0 |

## Rejection codes (target-run pairs)

| code | kind | pairs |
|---|---|---|
| `QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT` | quantities | 10 |
| `STATEMENT_REQUIRES_EXPERIMENTAL_SCOPE` | statements | 8 |
| `QUANTITY_UNIT_NOT_BOUND_TO_EXPRESSION` | quantities | 5 |
| `RELATION_SUBJECT_OBJECT_NOT_IN_APPLICABLE_SOURCE` | relations | 5 |
| `STATEMENT_SUBJECT_APPLICABILITY_UNRESOLVED` | statements | 4 |
| `STATEMENT_INCLUDES_A_RUNNING_PAGE_HEADER` | statements | 4 |
| `DERIVED_IS_NOT_OBSERVATION` | statements | 3 |
| `OPEN_QUESTION_NOT_EXPLICIT_IN_SOURCE` | statements | 3 |
| `CONFIGURATION_ROLE_NOT_ESTABLISHED_IN_ORIGINAL_PASSAGE` | statements | 3 |
| `CONFIGURATION_OR_DERIVED_IS_NOT_MEASUREMENT` | quantities | 3 |
| `CHANGING_OBSERVATION_IS_NOT_ESTABLISHED_CONFIGURATION` | statements | 2 |
| `OBSERVATION_DESCRIBES_A_PROCEDURE` | statements | 2 |
| `CONFLICTING_ROLE_PROPOSALS_FOR_SAME_SOURCE_SPAN` | statements | 2 |
| `NORMATIVE_ROLE_NOT_EXPLICIT_IN_SOURCE` | statements | 2 |
| `SOURCE_GOAL_IS_NOT_ESTABLISHED_RESULT` | statements | 2 |
| `CONFLICTING_ROLE_PROPOSALS_FOR_SAME_SOURCE_SPAN` | quantities | 1 |
| `EXPLICIT_DERIVATION_IS_NOT_REPORTED_MEASUREMENT` | quantities | 1 |
| `QUANTITY_VALUE_OR_UNIT_IS_NOT_A_QUANTITY_NAME` | quantities | 1 |
| `CURRENT_OR_CITED_STUDY_UNRESOLVED` | statements | 1 |
| `INTERPRETATION_DESCRIBES_A_PROCEDURE` | statements | 1 |
| `UNCERTAINTY_CANNOT_BECOME_CONFIRMED` | statements | 1 |
| `QUANTITY_SEMANTICS_OR_UNIT_UNRESOLVED` | quantities | 1 |
| `AUTHOR_ROLE_REQUIRES_CONTEXT_REVIEW` | statements | 1 |
| `QUANTITY_NOT_ORIGINAL_NUMERIC_EXPRESSION` | quantities | 1 |
| `GUIDANCE_NOT_EXPLICIT_IN_SOURCE` | statements | 1 |
| `LOCAL_SUBJECT_BINDING_UNRESOLVED` | relations | 1 |

## ignition

| target | kind | printed words | r1 | r2 |
|---|---|---|---|---|
| quantities-06 | quantities | chamber that could provide continuous operation at 57 kPa. | rejected: `CONFLICTING_ROLE_PROPOSALS_FOR_SAME_SOURCE_SPAN` | correct |
| quantities-07 | quantities | where the 5.2 cm by 14.0 cm samples were tested. | accepted, graded wrong (experimental_configuration) | accepted, graded wrong (experimental_configuration, experimental_configuration) |
| quantities-08 | quantities | where the 5.2 cm by 14.0 cm samples were tested. | accepted, graded wrong (experimental_configuration) | accepted, graded wrong (experimental_configuration, experimental_configuration) |
| quantities-09 | quantities | The igniter was a retractable 2.2 mm OD ceramic rod | accepted, graded wrong (experimental_configuration) | accepted, graded wrong (experimental_configuration) |
| quantities-13 | quantities | The chamber is 299 l in volume with an I.D. of 81.2 cm and an internal height if 30.5 cm. | accepted, graded wrong (experimental_configuration, experimental_configuration) | accepted, graded wrong (experimental_configuration, experimental_configuration) |
| quantities-14 | quantities | the chamber was rotated at 20.4 RPM for several minutes before the drop | rejected: `QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT` | rejected: `QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT` |
| quantities-15 | quantities | The ignition region of the sample was exposed to a slow flow (~30 cm/s) of gas | rejected: `QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT` | correct |
| quantities-16 | quantities | The 1-g buoyant velocity was estimated by Takahashi16 to be 35 cm/s, but the lunar gravity | rejected: `EXPLICIT_DERIVATION_IS_NOT_REPORTED_MEASUREMENT` | not proposed (proposed as entities/statements) |
| quantities-17 | quantities | The worst-case delta for these materials can be seen to be 2.3%. | not proposed (proposed as statements) | not proposed (proposed as entities/statements) |
| quantities-28 | quantities | 1190 | rejected: `QUANTITY_UNIT_NOT_BOUND_TO_EXPRESSION` | rejected: `QUANTITY_UNIT_NOT_BOUND_TO_EXPRESSION` |
| quantities-29 | quantities | 2.3 | rejected: `QUANTITY_UNIT_NOT_BOUND_TO_EXPRESSION` | rejected: `QUANTITY_UNIT_NOT_BOUND_TO_EXPRESSION` |
| relations-26 | relations | The WSTF testing was conducted using a WSTF 1.4 m3 (50 ft3) chamber that could provide con | accepted, graded wrong (hasCondition) | accepted, graded wrong (hasCondition) |
| statements-18 | statements | To increase the number of tests for repeatability, two samples were ignited and tested in  | rejected: `CHANGING_OBSERVATION_IS_NOT_ESTABLISHED_CONFIGURATION` | rejected: `CHANGING_OBSERVATION_IS_NOT_ESTABLISHED_CONFIGURATION` |
| statements-19 | statements | Five materials were tested in both facilities. | rejected: `OBSERVATION_DESCRIBES_A_PROCEDURE` | rejected: `OBSERVATION_DESCRIBES_A_PROCEDURE` |
| statements-20 | statements | the actual velocity (induced by the simulated gravity) is not known. | rejected: `DERIVED_IS_NOT_OBSERVATION` | rejected: `DERIVED_IS_NOT_OBSERVATION` |
| statements-21 | statements | In figures 7, 8 and 9, the lunar-g buoyant limit was found to be less than the extrapolate | accepted, graded wrong (Publication) | rejected: `DERIVED_IS_NOT_OBSERVATION` |
| statements-22 | statements | Various differences in the test methods have been considered (turbulence at high flow rate | rejected: `OPEN_QUESTION_NOT_EXPLICIT_IN_SOURCE` | correct |
| statements-25 | statements | This suggests that increased flammability at lunar conditions may not be a universal issue | rejected: `OPEN_QUESTION_NOT_EXPLICIT_IN_SOURCE` | rejected: `OPEN_QUESTION_NOT_EXPLICIT_IN_SOURCE` |

## regulator

| target | kind | printed words | r1 | r2 |
|---|---|---|---|---|
| quantities-07 | quantities | Maximum gas temperature = 580-674F | rejected: `QUANTITY_VALUE_OR_UNIT_IS_NOT_A_QUANTITY_NAME` | rejected: `QUANTITY_SEMANTICS_OR_UNIT_UNRESOLVED` |
| quantities-09 | quantities | 20uL was injected | rejected: `QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT` | not proposed (proposed as entities/statements) |
| quantities-10 | quantities | seeking to achieve ~100 mg/ft2 film coating | rejected: `QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT` | not proposed (proposed as entities/statements) |
| quantities-12 | quantities | maintained its 4.05 psid setpoint with approximately 1 pph demand | accepted, graded wrong (reported_quantity) | accepted, graded wrong (reported_quantity) |
| relations-30 | relations | For the dodecane runs, 20uL was injected at the insterstage port using a syringe | rejected: `RELATION_SUBJECT_OBJECT_NOT_IN_APPLICABLE_SOURCE` | not proposed (proposed as entities/statements) |
| relations-31 | relations | Five impacts were then executed with the dodecane load in the POR interstage port. | rejected: `RELATION_SUBJECT_OBJECT_NOT_IN_APPLICABLE_SOURCE` | rejected: `RELATION_SUBJECT_OBJECT_NOT_IN_APPLICABLE_SOURCE` |
| relations-32 | relations | A final series of 5 wet impacts was executed after the test cell was adjusted to further r | rejected: `RELATION_SUBJECT_OBJECT_NOT_IN_APPLICABLE_SOURCE` | rejected: `RELATION_SUBJECT_OBJECT_NOT_IN_APPLICABLE_SOURCE` |
| statements-15 | statements | A partial test at WSTF at 1500 psia and 100% O2 (9) seems to indicate an AIT around 400F a | rejected: `CURRENT_OR_CITED_STUDY_UNRESOLVED` | rejected: `STATEMENT_REQUIRES_EXPERIMENTAL_SCOPE` |
| statements-16 | statements | pure dodecane was used instead so that the materials properties would be known and the com | rejected: `INTERPRETATION_DESCRIBES_A_PROCEDURE` | rejected: `STATEMENT_REQUIRES_EXPERIMENTAL_SCOPE` |
| statements-18 | statements | Nitrogen functional testing performed after the dry impact testing showed nominal POR perf | accepted, graded wrong (ReportedObservation, ReportedObservation) | accepted, graded wrong (ReportedObservation) |
| statements-19 | statements | Impact times of 80-93 msec were measured after adjustments and prior to re-connecting the  | rejected: `STATEMENT_SUBJECT_APPLICABILITY_UNRESOLVED` | rejected: `STATEMENT_REQUIRES_EXPERIMENTAL_SCOPE` |
| statements-20 | statements | appeared to have softened the seal resulting in a leak. | rejected: `UNCERTAINTY_CANNOT_BECOME_CONFIRMED` | correct |
| statements-21 | statements | the CHDS was adjusted to reduce POR body temperatures for the remaining three test runs. | correct | rejected: `CONFIGURATION_ROLE_NOT_ESTABLISHED_IN_ORIGINAL_PASSAGE` |
| statements-22 | statements | Functional testing performed after the initial wet impact testing demonstrated nominal POR | rejected: `STATEMENT_INCLUDES_A_RUNNING_PAGE_HEADER` | rejected: `STATEMENT_INCLUDES_A_RUNNING_PAGE_HEADER` |
| statements-24 | statements | Upon impact, a small, brief flame was generated from the impact demonstrating that the adi | rejected: `CONFLICTING_ROLE_PROPOSALS_FOR_SAME_SOURCE_SPAN` | correct |
| statements-25 | statements | SEM analysis could not verify this as the quantity was too small. | rejected: `STATEMENT_SUBJECT_APPLICABILITY_UNRESOLVED` | correct |
| statements-26 | statements | SEM of the filter found carbon | rejected: `STATEMENT_INCLUDES_A_RUNNING_PAGE_HEADER` | rejected: `STATEMENT_INCLUDES_A_RUNNING_PAGE_HEADER` |
| statements-27 | statements | The model confirmed that for both the 150 msec and 60 msec pressurization cases tested, th | accepted, graded wrong (Measurement) | rejected: `AUTHOR_ROLE_REQUIRES_CONTEXT_REVIEW` |
| statements-28 | statements | evidence of dodecane combustion was found in the regulator but did not result in any funct | rejected: `CONFLICTING_ROLE_PROPOSALS_FOR_SAME_SOURCE_SPAN` | correct |

## textiles

| target | kind | printed words | r1 | r2 |
|---|---|---|---|---|
| entities-02 | entities | PBI | accepted, graded wrong (Material) | accepted, graded wrong (Material) |
| quantities-05 | quantities | The proposed Artemis IV+ atmosphere is 8.2 psia and 34±2% O2 (testing at 37% O2 for contin | rejected: `CONFIGURATION_OR_DERIVED_IS_NOT_MEASUREMENT` | rejected: `QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT` |
| quantities-06 | quantities | The proposed Artemis IV+ atmosphere is 8.2 psia and 34±2% O2 (testing at 37% O2 for contin | rejected: `CONFIGURATION_OR_DERIVED_IS_NOT_MEASUREMENT` | rejected: `QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT` |
| quantities-07 | quantities | The proposed Artemis IV+ atmosphere is 8.2 psia and 34±2% O2 (testing at 37% O2 for contin | rejected: `CONFIGURATION_OR_DERIVED_IS_NOT_MEASUREMENT` | rejected: `QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT` |
| quantities-08 | quantities | Apollo (100% O2) and Skylab (70% O2) | not proposed (proposed as statements) | not proposed (proposed as statements) |
| quantities-09 | quantities | Apollo (100% O2) and Skylab (70% O2) | not proposed (proposed as statements) | not proposed (proposed as statements) |
| quantities-10 | quantities | Burn length < 6” | rejected: `QUANTITY_NOT_ORIGINAL_NUMERIC_EXPRESSION` | rejected: `QUANTITY_UNIT_NOT_BOUND_TO_EXPRESSION` |
| quantities-11 | quantities | 100% PBI knit fabric coupons tested at 48% O2 and 8.2 psia | accepted, graded wrong (experimental_configuration, experimental_configuration) | accepted, graded wrong (experimental_configuration, experimental_configuration) |
| quantities-16 | quantities | a minimum of 37% O2 at 8.2 psia | not proposed (proposed as statements) | rejected: `QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT` |
| quantities-17 | quantities | a minimum of 37% O2 at 8.2 psia | not proposed (proposed as statements) | rejected: `QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT` |
| relations-28 | relations | 100% PBI knit fabric for crew clothing next-to-skin shirt | rejected: `LOCAL_SUBJECT_BINDING_UNRESOLVED` | not proposed (proposed as entities/statements) |
| relations-29 | relations | Custom fire-resistant patches sewn to outer jacket fabric tested at 37% O2 and 8.2 psia | accepted, graded wrong (madeOf) | accepted, graded wrong (madeOf) |
| statements-18 | statements | Very limited existing Commercial Off-The-Shelf (COTS) textiles can be certified for use in | rejected: `STATEMENT_REQUIRES_EXPERIMENTAL_SCOPE` | rejected: `STATEMENT_REQUIRES_EXPERIMENTAL_SCOPE` |
| statements-19 | statements | No transfer of burning debris (melt / drip) | rejected: `NORMATIVE_ROLE_NOT_EXPLICIT_IN_SOURCE` | rejected: `NORMATIVE_ROLE_NOT_EXPLICIT_IN_SOURCE` |
| statements-21 | statements | Metal fixture can be used to shield the vertical raw edges | rejected: `CONFIGURATION_ROLE_NOT_ESTABLISHED_IN_ORIGINAL_PASSAGE` | rejected: `CONFIGURATION_ROLE_NOT_ESTABLISHED_IN_ORIGINAL_PASSAGE` |
| statements-22 | statements | Coupon-level flammability testing at 37% O2 shows increased propagation with configuration | rejected: `STATEMENT_REQUIRES_EXPERIMENTAL_SCOPE` | rejected: `STATEMENT_REQUIRES_EXPERIMENTAL_SCOPE` |
| statements-23 | statements | NASA’s textile engineering and development team has been sourcing existing COTS textile pr | rejected: `STATEMENT_SUBJECT_APPLICABILITY_UNRESOLVED` | rejected: `STATEMENT_SUBJECT_APPLICABILITY_UNRESOLVED` |
| statements-24 | statements | Certification testing will be performed at White Sands Test Facility (WSTF) | rejected: `GUIDANCE_NOT_EXPLICIT_IN_SOURCE` | rejected: `STATEMENT_REQUIRES_EXPERIMENTAL_SCOPE` |
| statements-27 | statements | Goal to systematically mature materials that enable safer and more sustainable human explo | rejected: `SOURCE_GOAL_IS_NOT_ESTABLISHED_RESULT` | rejected: `SOURCE_GOAL_IS_NOT_ESTABLISHED_RESULT` |
