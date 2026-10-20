# Phase 1 v6, milestone 8: candidates from document structure, under the generalization addendum

**Status: `PHASE1_COMPLETE=NO`.** The development readiness gate (mandate §13) is not met and the registered holdout (NTRS 20170004702, `../holdout_registration/`) was not acquired. Code: `d7c4732` on `diego/research` (parent `2f343b8`).

This milestone was built in a cloud container without the NVIDIA key or the PDFs, so every number below is **evaluation A** in the sense of Liam's generalization addendum (§5): offline revalidation of saved live outputs with the current implementation, 0 model calls. Nothing here is fresh inference, and nothing here measures run-to-run stability of the model.

## What was run

- `scripts/phase1_offline_replay.py` on the three development live outputs of frozen code `1dffc83` (`../milestone7/*_live_1dffc83/prepared.json.gz`) → `replay_d7c4732/{ignition,regulator,textiles}/`.
- The same replay on the 12 reviewed PTFE runs (inputs as in `../milestone4/rescored_c314286/ptfe_run*/replay.json` and `../milestone5/ptfe_live_*/`). Their outputs are not copied; `accepted_record_diff_2f343b8_d7c4732.json` records every accepted record added or removed per run.
- `rejection_audit_d7c4732.json`: every record of the three sources by kind, origin (model proposal vs printed-structure candidate), status and first reason.

## Mechanisms, classified per addendum §2

| Mechanism | Class (§2) | Motivated by | Effect on the other sources (evaluation A) |
| --- | --- | --- | --- |
| A condition printed as a *setting* inside a group's own subsection ("exposed to a 10 cm/s primer flow", "to achieve lunar gravity", "at …") is that group's `hasCondition`, unless the sentence names another group. The validator binds it by the subject's heading certificate or a printed "<subject> tested at" clause. | reusable document-structure mechanism | ignition (rel-26, rel-27) | regulator 0, textiles 0, PTFE 0 (no change). Without the setting cue the same reader also gave GRC → "1-g", "buoyant flow", "microgravity" from incidental mentions; the cue (a prepositional setting phrase) removes them. |
| A configuration value printed in a method section outside every group's subsection configures the document's investigation. | reusable document-structure mechanism | ignition (q-05, "lunar habitat pressure 56.5 kPa") | regulator +1 (q-08, "supply pressure 3750 psia"); PTFE +2 accepted records in runs 1, 4, 5, 6 ("energy 72 ft-lbs", "rate 9 °F/min": model proposals previously unresolved, now at investigation scope; **to be adjudicated**, they duplicate the Test 13A impact-energy rows); textiles 0. |
| "<thing> tested at <settings>" proposes the thing as a `Sample`, with each setting as a pressure, temperature or O2 configuration value (the dimension of the unit decides). | document-structure mechanism plus a dimensional rule | textiles (ent-04, q-14, q-15) | ignition 0, regulator 0, PTFE 0. **Flagged as suspicious under Diego's rule 2**: it lifts only its motivating source. The convention is general (test matrices and slide decks print specimens this way), but only one development source exercises it. |

None of the three names a source, a material, an expected value or a target. No scorer, denominator, ontology or evaluation population changed.

## Result (evaluation A)

| Source | Accepted records `2f343b8` → `d7c4732` | Removed | Frozen targets provisionally reached (author's adjudication pending) |
| --- | --- | --- | --- |
| Lunar ignition (NTRS 20250002114) | 105 → 109 | 0 | q-05, rel-26, rel-27 (10/29 → 13/29 if confirmed) |
| Oxygen regulator (NTRS 20170003941) | 74 → 75 | 0 | q-08 (18/32 → 19/32 if confirmed) |
| Textiles slide deck (NTRS 20260005493) | 23 → 27 | 0 | ent-04, q-14, q-15 (8/29 → 11/29 if confirmed; two records carry the same 37 % value, "O2" from the candidate and "oxygen concentration" from the model, once the specimen existed) |
| PTFE (NTRS 20090043050), 12 reviewed runs | +2 in runs 1, 4, 5, 6; unchanged in the other 8 | 0 | no target change; the 2 records per run are a precision question for the author |

Provisional target matches come from `../review_tools/match_targets.py` against the frozen v4 `source_review.json` of each source; they are not an adjudication.

## What the model proposed versus what printed-structure candidates added (`d7c4732`)

Accepted / proposed, per source and kind:

| Source | Entities | Quantities | Relations | Statements |
| --- | --- | --- | --- | --- |
| Ignition | model 36/60 | model 6/128; candidates 5/5 | model 0/35; candidates 4/7 | model 76/353 |
| Regulator | model 13/21 | model 4/71; candidates 1/1 | model 2/16; candidates 1/1 | model 55/190 |
| Textiles | model 7/16; candidates 1/1 | model 3/12; candidates 4/4 | model 1/7; candidates 0/4 | model 13/35 |

Reading: on the ignition paper the model's 128 quantity proposals yield 6 accepted records and its 35 relation proposals yield none; the main rejection families are `QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT` (37), `QUANTITY_UNIT_NOT_BOUND_TO_EXPRESSION` (30), `QUANTITY_SEMANTICS_OR_UNIT_UNRESOLVED` (24), `RELATION_ENDPOINT_CLASS_CONTRADICTION` (16) and `RELATION_SUBJECT_OBJECT_NOT_IN_APPLICABLE_SOURCE` (15). The model attributed "10 cm/s primer flow", "slow flow (~30 cm/s)" and "buoyant flow" to the whole investigation instead of to the group whose subsection prints them: it never saw the subsection scope. On the slide deck the model proposed 12 quantities in total. The printed-structure readers of this milestone recover a few of these, but they are the rule layer the addendum asks to stop growing.

## Metamorphic and negative tests (addendum §4), on the production readers

`tests/test_phase1_closure.py`:
- rewrapping a "tested at" line at three widths gives the same specimen, settings and relation;
- a different specimen name or qualifier on the line gives a different reading;
- rewrapping a subsection's lines gives the same conditions; the same sentence under another heading gives that group the condition; a changed gravity condition gives a different condition; an incidental mention ("to the normal gravity vertical force") and a sentence naming another group give nothing;
- values in a method section outside every group's subsection go to the investigation, values under a group's heading stay with the group.

Quality at `d7c4732`: `ruff format --check`, `ruff check`; `pytest` with the same failing set as `2f343b8` in the cloud (only tests that need the local index files), 724 tests with them.

## Next, in the order the addendum and Diego's rules require

1. **Start from the rejection audit, not from new readers.** Give the model each entity's class and the subsection scope of every passage (and resolve current vs cited by structure), so that it proposes "GRC hasCondition lunar gravity" and the group's own values itself; measure, on the next live runs, what the model then proposes versus what candidates still add.
2. **Slide decks**: subsection- and table-directed model calls with the spare budget, instead of a slide reader.
3. **Record-by-record precision review** on ignition and regulator (the new records above included).
4. **Fresh live runs (evaluation B)** on all four sources with frozen code, all predetermined runs reported, variability causes logged per run.
5. Leave-one-source-out check, then the §13 gate, then the frozen holdout.

## Addendum (third commit): the model gets the subsection scope and the relation signatures

Built from the rejection audit above (rules C2 and C3), not from new readers. It is not measurable by replay: every number in this README is unchanged by it except the table guard below. Its effect must be read on fresh live runs (evaluation B) with frozen code on the four development sources, as the next milestone's `rejection_audit` and `accepted_record_diff`.

| Mechanism | Class (§2) | What it changes for a new document |
| --- | --- | --- |
| Every source anchor in a model request carries `heading`, the printed heading it sits under, and `group`, the known entity key when that heading names a current ExperimentFamily; the relationship and proposition instructions say that what is printed under a group's own heading belongs to that group, the narrowest explicit subject. | reusable document-structure mechanism (request context, no extraction rule) | A condition or configuration printed in any group's subsection is proposed with that group as subject instead of the whole investigation (the `RELATION_SUBJECT_OBJECT_NOT_IN_APPLICABLE_SOURCE` family). |
| `relation_signatures`: the endpoint classes each approved relation admits, taken from the same table the validator enforces (`RELATION_ENDPOINTS`). | general ontology contract stated to the model | Relations with an endpoint of the wrong class are not proposed (the `RELATION_ENDPOINT_CLASS_CONTRADICTION` family, 16 on the ignition paper). |
| One request directed at a group's subsection, with the group as the only allowed subject, when that subsection prints a current condition, material, sample or intervention and no accepted relation links the group yet. Ordinary recovery (split on truncation) applies; the budget ceilings apply. | directed, general use of the spare budget (rule C3) | A group the ordinary pass left unlinked gets one more look at its own subsection; a group already linked costs nothing. |
| A configuration value printed in a method section is not attributed to the investigation when the document's own tables print the same value under a column named by its unit or variable (`table_column_prints_value`): the rows are the narrower printed subjects. | reusable document-structure mechanism (validator, precision) | Removes the duplicate method-level record where per-row values already carry it. |

Replay at this commit versus `d7c4732`: PTFE runs 1, 4, 5, 6 no longer accept "energy 72 ft-lbs" at investigation scope (the Test 13A rows print "72 ft-lbs (98J)"); "rate 9 °F/min" stays, since no table prints it; the three development sources are unchanged (the ignition tables do not print 56.5 kPa per row). Tests: request context (heading, group, signatures) and the directed request are checked with the controlled stage adapter; the table guard with a synthetic table and a column of another variable.

Live-run caveat: the request now carries more fields, so every stage's cache key changes and the next live run makes fresh calls for every window; replays of saved outputs are unaffected.
