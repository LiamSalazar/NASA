# Phase 1 v6, milestone 10: provider fallback and quantity validation mechanisms

**Status: `PHASE1_COMPLETE=NO`.** No live run was made in this milestone. The §13 gate is not met and the holdout has not been acquired.

## Provider fallback

**Why it changed.** In evaluation B (`../milestone9/`), one propositions window was lost on PTFE (pp. 9–12 and 18) and one on the regulator (pp. 1 and 4). The primary model failed: the 600 s deadline on PTFE, HTTP 500 three times on the regulator. Every call to the configured fallback `nvidia/nemotron-3-super-120b-a12b` then returned HTTP 404 "function not found for account". The model is listed by `GET /v1/models`, but the key cannot call it.

**How the replacement was chosen** (2026-10-20, key from `.env`, never printed):

| Model | Minimal call | Call with the adapter's request shape (`chat_template_kwargs.enable_thinking`, `reasoning_budget`, JSON response) |
| --- | --- | --- |
| `nvidia/nemotron-3-ultra-550b-a55b` | 200 | **400**: the server rejects `reasoning_budget` ("thinking_token_budget is not yet supported"). It would fail as a fallback. |
| `nvidia/nemotron-3.5-lightning-30b-a3b` | 200 | **200**, valid JSON |

Four calls in total, with no scientific content.

**Decision.** `NVIDIA_SCIENCE_FALLBACK_MODELS=nvidia/nemotron-3.5-lightning-30b-a3b`, set in `.env.example` and in the local `.env`, which is not committed.
- It is the same Nemotron 3.5 generation as the primary model and accepts the same request.
- It is a smaller model. Any record from a window it answers stays traceable through the run's `served_models` and `requested_model` per call.
- The primary model is unchanged. Retry counts and budgets are unchanged.

## Quantity validation mechanisms (from `../milestone9/quantity_rejection_audit.md`)

Each mechanism is one commit. Its effect is measured by offline replay (evaluation A, 0 model calls) of 26 inputs:
- the 5 exposed v4 packages;
- the 2 PTFE runs with historical negatives;
- the 12 reviewed PTFE runs;
- the 3 milestone 7 development runs;
- the 4 evaluation B runs of milestone 9.

The baseline is code `b19f3c6`, which is the same validation code as `1850be3`.

### (a) Units the unit inventory already interprets (`numeric_expressions.UNIT_LITERAL`)

| | |
| --- | --- |
| Class (addendum §2) | general dimensional rule |
| Motivated by | ignition: "299 l", "1.4 m3 (50 ft3)" rejected as `QUANTITY_NOT_ORIGINAL_NUMERIC_EXPRESSION` |
| Change | The recognition grammar now reads the lowercase litre (`l`, `ml` …) and the cubic or square foot (`ft3`, `ft^3`, `ft²`), which `normalization.units` already interprets. A bare `l` is ambiguous: it is split only against an identical declared unit, never with no unit, and case stays significant (`l` ≠ `L`). |
| Tests | `tests/test_numeric_expressions.py`. Metamorphic: spacing ("299 l" / "299l"), caret and superscript forms. Negative: undeclared `l`; `l` against `L`; `lbs`, `lm` and `ft` are not litres. |
| Effect (replay) | 0 accepted records added or removed on all 26 inputs. On ignition (B and A), 6 rejections move from `QUANTITY_NOT_ORIGINAL_NUMERIC_EXPRESSION` to the name check (`QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT`, 5) or to a hold (`QUANTITY_SEMANTICS_OR_UNIT_UNRESOLVED`, 1). The other three sources do not change. |

### (b) A name printed after the value, separate from the model's label (`printed_value_name`)

| | |
| --- | --- |
| Class (addendum §2) | document structure (post-value name) plus a general dimensional rule |
| Motivated by | ignition: "a WSTF 1.4 m3 (50 ft3) chamber", "a 7.4 cm ID by 30 cm long quartz tube duct", "299 l in volume" (`QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT`, 41 in B) |
| Change | The words printed right after the value (after an author equivalent in parentheses, or after "in") name it. The model's label is accepted when at least one of its words is printed there. Each other label word must be printed in the same sentence, or be a noun of the unit's own dimension ("volume" for m3, "concentration" for %). The printed name is recorded (`quantity_name_support.printed_name`); the label stays the model's. |
| Exclusions | One value of a printed pair ("5.2 cm by 14.0 cm samples") is never given a dimension. A percentage before a constituent ("made up of 90% Copper") is a composition whose owner the words do not settle, so a fraction is named this way only as a configuration ("tested at 48% O2"). |
| Duplicate rule (same commit) | The same printed value (same span), subject, unit and role is one quantity, whatever each proposal called it. Before, the label was part of the key, so "O2" and "oxygen concentration" for one "37% O2" were two records. |
| Tests | `tests/test_quantity_printed_names.py`. Metamorphic: with and without the author equivalent, and the "in <name>" form. Negative: a label word neither printed nor of the unit's dimension; both values of a "by" pair; a constituent percentage; the same number printed twice stays two values. |
| Effect (replay) | **Ignition A:** +2 correct configuration records (WSTF chamber volume 1.4 m3, duct ID 7.4 cm). Neither is a frozen target. **Merges:** ignition GRC 299 l (A and B) and 57 kPa (B); textiles 37 % (A); PTFE 10,000 psia (runs 8, 12). **Unchanged:** regulator; PTFE recall 27–28/34 in all 12 runs, precision ≥ 0.981 (run 5, 103/105), 0 critical; PTFE B 23/34, 74/75. The 29 historical negatives: 0 critical regressions. |
| Flag | **Suspicious under rule 2** for its name part: new records appear only on the motivating source (ignition). The duplicate rule acts on three sources. |

The first version, without the composition exclusion, gave Salox-M "Copper percentage 90 %" and "Tin percentage 8 %" on six PTFE replays. Those are the bronze component's composition, so it was a critical false attribution. It was caught in replay, before commit, and became the negative test.

### Correction to the milestone 8 and 9 adjudications

Ignition targets quantities-11 (GRC chamber volume 299 l) and quantities-12 (GRC chamber I.D. 81.2 cm) were already reached by printed-structure candidates in both A and B. The earlier adjudications missed them.

| Ignition recall | Was | Corrected |
| --- | --- | --- |
| A, milestone 8 | 12/29 | **14/29** |
| B, milestone 9 | 10/29 | **12/29** |

quantities-09 (igniter OD 2.2 mm) stays not counted, because its record is labelled "OD ceramic rod".

### (d) An explicit setting cue next to the value makes it a configuration

| | |
| --- | --- |
| Class (addendum §2) | semantic with printed evidence |
| Motivated by | regulator: "maintained its 4.05 psid setpoint with approximately 1 pph demand", "maintained the ~4.05 psid set-point at the ~1 pph demand" (`CONFIGURATION_OR_DERIVED_IS_NOT_MEASUREMENT`) |
| Change | A prose value the model typed `reported_quantity` is re-typed `experimental_configuration` (`role_recovery.basis = EXPLICIT_SETTING_CUE_IN_VALUE_SENTENCE`, with the printed cue) instead of being rejected. Two conditions: a held-setting cue ("maintained", "set point") is printed within 90 characters before or 60 after the value, and the value's sentence carries no requirement, plan or derivation cue ("specified", "required", "will", "shall", "simulating", "predicted", "derived", "fit", "standard deviation"). Table cells keep their header-based rule. |
| Tests | `tests/test_quantity_setting_role.py`. Metamorphic: three wordings and positions of the cue. Negative: a requirement ("required … specified and maintained"), a plan ("will be maintained"), a simulation, a cue far from the value, an "initial" column, a measured value with no cue. |
| Effect (replay) | 0 accepted records added or removed on all 26 inputs. On the regulator (A and B), the two ~1 pph demand values move from rejected to held (`TEST_ARTICLE_ALIAS…`, the test-article subject), ready for (c). PTFE, ignition and textiles do not change. A first version also matched "initial" anywhere on a table page and re-typed measured AIT values on PTFE (held, never accepted). It was narrowed before commit, and those cases became the negative tests. |
| Contract kept | A value the sentence itself says "was set to" stays rejected when the model calls it a measurement (`test_epistemic_upgrades_rejected`), so the model's role error stays visible. Whether that contract should become a role repair too is **a decision for Diego/Liam**. It is not changed here. |

### (c) A value inside one group's own subsection is revalidated with that group

| | |
| --- | --- |
| Class (addendum §2) | document structure |
| Motivated by | regulator: settings of a test series that the model gave to the test article (`TEST_ARTICLE_ALIAS_EXPERIMENTAL_GROUP_SCOPE_REQUIRES_REVIEW`, 7 in B) |
| Change | When the proposed subject fails or is held (test-article alias hold, subject rejection, scope hold), and every support span lies under one printed heading that names exactly one current `ExperimentFamily`, that group is revalidated with the full validator. It is adopted only if the validator certifies the group's own subsection (`EXACT_ORIGINAL_GROUP_SUBSECTION`, which already refuses a span naming another group). The proposed subject is kept as `subject_recovery.proposed_subject`. |
| Tests | `tests/test_quantity_subsection_group.py`. Metamorphic: the same sentence under each of two headings goes to that heading's group. Negative: a sentence under group A that names group B; a value in the method section outside every subsection. |
| Effect (replay) | **Ignition A:** +1 correct configuration record (WSTF duct length 30 cm; not a frozen target), and the 7.4 cm duct ID is kept under the label "quartz tube duct ID". No other input changes. The regulator's ~1 pph demand values stay held: their sentences are not under a group heading. **PTFE:** unchanged (27–28/34, precision ≥ 0.981, 0 critical). The 29 historical negatives: 0 critical regressions. |
| Flag | **Suspicious under rule 2**: it lifts only ignition, and it did not lift its motivating source. |

## Result at `80682e7` (all four mechanisms; evaluation A, 0 model calls)

Recall on frozen targets. The milestone 9 B runs are replayed at this code. Ignition includes the quantities-11 and quantities-12 correction above.

| Source | A (milestone 7 outputs) | B (milestone 9 outputs) | Change from the mechanisms |
| --- | --- | --- | --- |
| Lunar ignition | 14/29 | 12/29 | no target change; +3 correct non-target configuration records in A (WSTF chamber volume, duct ID, duct length); duplicates merged in A and B |
| Oxygen regulator | 19/32 | 12/32 | none; the two ~1 pph demand values go from rejected to held |
| Textiles | 11/29 | 10/29 | no target change; the duplicate 37 % merged in A |
| PTFE (official scorer) | 27–28/34 over 12 runs, precision 0.981–1.000 | 23/34, 74/75 | none |

Critical errors: 0 on every input. The 29 historical negatives: 0 critical regressions, 1 known non-critical record still supported (`rescored_80682e7/`).

**Reading.** The four mechanisms are safe and general, but they do not move recall on frozen targets. They mostly turn rejections into correct non-target records or holds, and they remove duplicates. The recall gap is still what the model does not propose, plus the provider failures of milestone 9. Two mechanisms, (b) and (c), add records only on ignition and are flagged under rule 2.

## Evaluation B, round 1 (fresh live runs at frozen code `96a2fa2`)

One run per source, one source at a time, 3,600 s budget, 0 approvals. All four runs are reported (`evaluation_b_round1.json`). Recall is on frozen targets. Precision is record by record (PTFE by the official scorer).

| Run | Calls / time | Recall | Precision | Critical | Provider |
| --- | --- | --- | --- | --- | --- |
| `textiles_live_96a2fa2_r1/` | 6 / 545 s | 11/29 | 21/24 = 0.875 | 0 | primary deadline after 425 s on one window, answered by the fallback |
| `regulator_live_96a2fa2_r1/` | 10 / 442 s | 16/32 | 44/59 = 0.746 | 1 | one HTTP 500, recovered by the primary |
| `ignition_live_96a2fa2_r1/` | 21 / 2,023 s | 14/29 | 84/117 = 0.718 | 1 | none |
| `ptfe_live_96a2fa2_r1/` | 16 / 1,738 s | 28/34 | 116/117 = 0.991 | 0 | three HTTP 500 and one 600 s deadline, both windows answered by the fallback |

No window was lost: the new fallback answered every window the primary did not.

Causes against milestone 9 B (`evaluation_b_round1.json` gives per-target causes):
- **Textiles** +1 (relations-29): model generation. The model proposed each specimen's "37% O2 and 8.2 psia" condition itself.
- **Regulator** +4: entity linking. The second wet series entity was accepted this time, so its 46–49 msec and both hasMaterial relations follow.
- **Ignition** +2 (quantities-15, statements-22): model generation.
- **PTFE** +5: provider. The window lost in milestone 9 was answered here.

Two critical errors, both through paths older than milestone 10 and closed in milestone 11 (`../milestone11/`):
- **Regulator:** "nominal operating pressure ~200 psia" given to the condition entity "3750 psia supply pressure".
- **Ignition:** "1% lower in oxygen concentration than" accepted as an absolute "oxygen concentration 1 %".

Round 2 of this milestone was not run. After round 1, Diego chose to close the two critical paths first and to restart evaluation B on milestone 11's frozen code.
