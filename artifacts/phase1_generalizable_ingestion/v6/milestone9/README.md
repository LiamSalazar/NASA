# Phase 1 v6, milestone 9: evaluation B on the four development investigations

**Status: `PHASE1_COMPLETE=NO`.** The development readiness gate (mandate §13) is not met, and the registered holdout (NTRS 20170004702) was not acquired.

## What was run

One new live run per development source with frozen code `1850be3`, the three milestone 8 commits on `2f343b8`. The receipts commit `39b57bc` changes no code; the run directories carry its short hash, the git head the runs started from. Budget: 3,600 s per run, 0 approvals, model `nvidia/nemotron-3.5-super-vl-120b-a12b`. All four runs are reported and none was repeated or selected. Milestone 8's third commit changes every stage's cache key, so every window was a fresh call (`cached_segments` 0). The originals match the v4 sha256.

| Run | Source | Calls / time |
| --- | --- | --- |
| `textiles_live_39b57bc/` | Textiles slide deck, NTRS 20260005493 | 4 / 146 s |
| `regulator_live_39b57bc/` | Oxygen regulator, NTRS 20170003941 | 15 / 441 s |
| `ignition_live_39b57bc/` | Lunar ignition, NTRS 20250002114 | 22 / 1,960 s |
| `ptfe_live_39b57bc/` | PTFE, NTRS 20090043050 | 15 / 1,094 s |

## Result: evaluation B next to evaluation A

Evaluation A is the milestone 8 replay of saved outputs at the same code, with 0 model calls. Evaluation B is this milestone's fresh inference. Each B target was adjudicated by the branch author against the run's active records (`development_target_outcomes.json`). PTFE was scored with the official scorer (`ptfe_live_39b57bc/review/`).

| Source | Recall, A | Recall, B | Precision, B | Critical |
| --- | --- | --- | --- | --- |
| Lunar ignition | 12/29 | **10/29** | 72/95 = 0.758 | 0 |
| Oxygen regulator | 19/32 | **12/32** | 33/40 = 0.825 | 0 |
| Textiles (slides) | 11/29 | **10/29** | 19/21 = 0.905 | 0 |
| PTFE | 27–28/34 (12 runs) | **23/34** | 74/75 = 0.987 (official scorer) | 0 |

Precision on ignition, regulator and textiles is the record-by-record review in `record_precision_review.json`: every active record was judged against the printed page. Every error is non-critical:
- ignition, 23 errors: 9 duplicates, 11 fragments or roles, 1 study label (the Test 1 'chemical igniter' typed as current), 2 quantity label or subject errors;
- regulator, 7 errors;
- textiles, 2 errors.

B gained no target over A on any source.

## Cause of each variation (B against A)

| Source | Lost target | Cause |
| --- | --- | --- |
| Ignition | statements-22 | model: the tentative interpretation was proposed without a subject |
| Ignition | statements-25 | model: typed as a confirmed conclusion or open question; correctly rejected |
| Regulator | entities-06 | entity linking: the model's second wet series entity was rejected (`ENTITY_LABEL_ABSENT_FROM_SUPPORT`, its support span lacks its label) |
| Regulator | quantities-14, relations-32 | cascade of entities-06. The 46–49 msec value went to the first series and was **correctly held** (`QUANTITY_SUBJECT_NOT_IN_APPLICABLE_SOURCE`), so no false attribution resulted |
| Regulator | relations-31 | model: hasMaterial not proposed |
| Regulator | statements-20, 23, 25 | model: proposed without a subject, or a tentative explanation typed as an observation (correct rejection) |
| Textiles | entities-02 | model: only "100% PBI knit fabric" was proposed as the Material, not "PBI" |
| PTFE | statements-26, 27, 28 | **provider**: the propositions window covering pp. 9–12 and 18 (10 members, 14,618 characters, about 61.6k context tokens) was lost; details below |
| PTFE | statements-19, 21 | model: proposed in other windows of earlier runs; not proposed, or unresolved, in this run |

### Provider failures (corrected after the first version of this README)

`attempts.json.gz` records every call. A window counts as lost when none of its attempts returned.

| Run | Window | Attempts | Result |
| --- | --- | --- | --- |
| PTFE | propositions `…538ee243`, pp. 9–12 and 18 | primary model hit the 600 s per-request deadline; 4 retries on the fallback model `nvidia/nemotron-3-super-120b-a12b` returned HTTP 404 "function not found for account" | **lost**: no other window covers these members |
| Regulator | propositions `…57031586`, pp. 1 and 4 | 3 HTTP 500 on the primary model, then 4 × 404 on the fallback | **lost**: only quantities-07, statements-15 and entities-01 lie inside, and entities-01 came from the identity stage. None was correct in A, so this loss does not change recall |
| Regulator | identity `…dfc90a48` | 2 network errors, then success | recovered |
| Ignition | identity and propositions `…02c5fb0e` | HTTP 500 and one stream error, then success | recovered |
| Textiles | none | | |

- No call ended on `length`, and no response was truncated or repaired. The schema errors (ignition 25, the others 0) are per-item rejections inside completed responses.
- The low statement count on PTFE (50 against 224 in run 1's input) is mostly the lost window. It is not the model proposing less.
- **The configured fallback model is not available to this NVIDIA account**: every fallback call returns 404. So when the primary model fails 3 times, the window is lost.
- This is a configuration finding. No code or configuration was changed in this milestone.

Retrieval and postprocessing caused no variation. The rest comes from the model's proposals, plus one entity-linking failure that follows from a model support span.

The candidate inventory moves with the model's entities, because candidates attach to entities the run already has:
- **Regulator:** identical to A.
- **Ignition:** 10 candidate records against 12 in A. The candidate relations GRC hasCondition "slow flow (~30 cm/s)" and "P-213 Tape sample" madeOf "P-213 Tape" are missing because this run's model did not propose those entities.
- **Textiles:** the candidate patch specimen is absent because the model proposed the same specimen itself.

No frozen target depended on the two missing ignition relations.

## What the model proposed versus what printed-structure candidates added (B)

Accepted / proposed (`rejection_audit_1850be3.json`):

| Source | Entities | Quantities | Relations | Statements |
| --- | --- | --- | --- | --- |
| Ignition | model 30/52 | model 3/99; candidates 5/5 | model 1/5; candidates 1/4 | model 55/363 |
| Regulator | model 11/18 | model 3/30; candidates 1/1 | model 0/7; candidates 1/1 | model 24/104 |
| Textiles | model 6/11 | model 0/13; candidates 4/4 | model 1/2; candidates 0/4 | model 10/46 |
| PTFE | model 18/33; candidates 1/1 | model 5/23; candidates 24/27 | model 9/26; candidates 5/5 | model 13/50 |

What milestone 8's third commit changed, read from these runs:
- On ignition the model now proposes WSTF hasCondition "10 cm/s primer flow" by itself. In A only a candidate made that relation.
- On textiles the model now proposes the patch specimen (ent-04) by itself.
- The model's quantity proposals still mostly fail validation (ignition 3/99, regulator 3/30, textiles 0/13). Accepted quantities still come mainly from printed-structure candidates (PTFE 24 of 29), so the rule layer cannot be retired yet.

## Reading

- **B is below A on every source.** On ignition, regulator and textiles the losses come from what the model proposed in this one run. On PTFE most of the loss is a provider failure that the fallback could not cover.
- **The gate is not met.** §13 needs recall ≥ 0.80, stable across sources, precision ≥ 0.95 and 0 critical errors. Recall is 0.34–0.68. Precision is 0.76–0.99, and only PTFE reaches 0.95. There are 0 critical errors everywhere.
- **The largest precision cost on the development sources is duplication:** the same assertion accepted from two windows, or from the model and a candidate.
- **A single B run per source measures the level, not the spread.** Estimating the spread needs repeated predetermined runs per source.

## Next

1. Deduplication gaps seen in B: the same assertion accepted twice, from the model and from a candidate, or from two windows.
2. The rejected model quantity proposals (`QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT`, `QUANTITY_UNIT_NOT_BOUND_TO_EXPRESSION`), from the rejection audit, under the addendum's rules: audit the family before any new rule.
3. The fallback model is unavailable to the account, so a window whose primary call fails is lost; this needs a configuration decision.
4. Repeated predetermined B runs to measure variance, then leave-one-source-out, then the §13 gate, then the frozen holdout.

## Redaction (after publication)

The HTTP 404 provider messages of the PTFE and regulator runs named the NVIDIA account that owns the API key. That identifier is replaced by `[REDACTED]` in:
- `summary.json`, `attempts.json.gz` and `prepared.json.gz` of `ptfe_live_39b57bc/` and `regulator_live_39b57bc/`.

Nothing else changed in these files. The `digest` they store was computed by the run before the redaction, so it no longer matches a recomputation.

The provider adapter, the live-run receipt writer and the offline replay writer now redact any `account '<identifier>'` along with the key (`redact_provider_text`, `tests/test_receipt_redaction.py`).
