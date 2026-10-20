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
| Lunar ignition | 12/29 | **10/29** | about 0.81 (first pass, 95 records) | 0 |
| Oxygen regulator | 19/32 | **12/32** | about 0.85 (first pass, 40 records) | 0 |
| Textiles (slides) | 11/29 | **10/29** | about 0.90 (21 records) | 0 |
| PTFE | 27–28/34 (12 runs) | **23/34** | 74/75 = 0.987 (official scorer) | 0 |

Precision on ignition, regulator and textiles comes from a first pass over every active record. It is not yet the final record-by-record review, and every error it found is non-critical: duplicates, fragments and role errors (listed in `development_target_outcomes.json`). B gained no target over A on any source.

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
| PTFE | statements-19, 21, 26, 27, 28 | model: 50 statement proposals in this run against 224 in run 1's input; these were never proposed or stayed unresolved |

No variation came from the provider (every window ended `COMPLETE`), from retrieval or from postprocessing. All of it comes from the model's proposals, plus one entity-linking failure that follows from a model support span.

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

- **Run-to-run model variability is larger than the gains of milestone 8.** B is below A on every source, and the losses come from what the model proposed in this one run.
- **The gate is not met.** §13 needs recall ≥ 0.80, stable across sources, precision ≥ 0.95 and 0 critical errors. Recall is 0.34–0.68 and first-pass precision 0.81–0.99, with 0 critical errors everywhere.
- **A single B run per source measures the level, not the spread.** Estimating the spread needs repeated predetermined runs per source.

## Next

1. Record-by-record precision review of these B runs (ignition and regulator first), so the first-pass figures become judged figures.
2. Deduplication gaps seen in B: the same assertion accepted twice, from the model and from a candidate, or from two windows.
3. The rejected model quantity proposals (`QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT`, `QUANTITY_UNIT_NOT_BOUND_TO_EXPRESSION`), from the rejection audit, under the addendum's rules: audit the family before any new rule.
4. Repeated predetermined B runs to measure variance, then leave-one-source-out, then the §13 gate, then the frozen holdout.
