# Phase 1 closure on `diego/research`: tables, numeric grammar, scope, lineage, coverage, eligibility

**Status: `PHASE1_COMPLETE=NO`.** The engineering of M1 and M2 is implemented in the
ordinary application and measured on the exposed corpus. On the exposed PTFE
source every known critical error is gone and reviewed precision is 0.98 after
each review's holds (the fourth live run measured 0.92 as produced; the three
non-critical role errors it exposed are held at `0ade8f1`), but recall is
0.41–0.53 against the §11 target of 0.80, so §12 readiness is not demonstrated
and no new holdout was consumed. What still blocks recall needs decisions
outside this branch (see "Blockers for Liam").

PTFE (NTRS 20090043050) is `EXPOSED_DEVELOPMENT_REGRESSION_ONLY`; nothing here
is an independent evaluation. All reviews are by the branch author from full
records; 22 judgments are reused from the earlier two-lens review for
byte-identical records, and the fourth run's review reuses a judgment only when
the proposal id (a hash of the proposal content) is identical to one judged in
the first or second run, listing the record fields that differ.

## Code (commits on `diego/research`, main untouched at `54445d0`)

| Commit | Change |
| --- | --- |
| `4a2f99d`, `2b7d1d6`, `80d8d69`, `118ec71` | Numeric grammar (§5), header-unit binding, first live run and equal-standard review (`../numeric_expression_grammar/`). |
| `e19b7c0` | Continuation tables, row groups, legend-backed markers, row/cell binding; comparator lineage; section-title bug; document-investigation scope; statement integrity; CSV grammar; `LIST`. |
| `7997b58` | Cited-table observations, procedures, value-labelled entities, lower-case page resumption. |
| `ac639df` | Footnote identity in both directions, `madeOf` by printed name, omission recovery through the split path, curation gated to `SOURCE_SUPPORTED`, "prior to" and "was used" cues, per-category precision in the scorer, table-structure receipt. |
| `6ba33aa` | A normalised identity keeps its printed anchor (`grounded_entities`); §8 source eligibility on four questions; the live runner re-judges the citation on file. |
| `adeada4` | Criteria, caveats and pointers typed as observations, glued caption lines, mid-sentence starts, page-end auxiliaries and front matter are held. |
| `63e9bb9` | Omission recovery retried once on the halves only when the request did not fit or was cut short. |
| `0ade8f1` | After the fourth live run's review: a caption with a dash (`Table 3—…`) is not an experiment-family identity; an observation that only says what was done to the specimens is a procedure; a validity caveat typed as an interpretation or conclusion is held. |

Quality at `0ade8f1`: `ruff format --check`, `ruff check` and `pytest` pass (643 tests; 572 before the closure).

## Measurements

### PTFE raw output replayed offline (0 model calls, same 36 frozen targets, 34 accessible)

| Input | Code | Correct | Retained | Precision (by kind) | Critical | Review |
| --- | --- | --- | --- | --- | --- | --- |
| First live run (`2b7d1d6` proposals) | `118ec71` | 15/34 | 25/34 | 57/59 | 0 | `ptfe_live_replay_7997b58/review/` (judged at the equivalent code) |
| First live run | `63e9bb9` | **17/34 = 0.50** | 25/34 = 0.74 | **64/65** (entities 15/15, statements 45/46, relations 4/4) | **0** | `ptfe_live_replay_63e9bb9/review/` |
| Second live run (`e19b7c0` proposals) | `63e9bb9` | **18/34 = 0.53** (17/34 if the p9-anchored specimen is not credited for the p4 target, see `review_errata.json`) | 26/34 = 0.76 | **61/62** (entities 18/18, statements 41/42, relations 2/2) | **0** | `ptfe_live_e19b7c0/revalidated_63e9bb9/review/` |
| Fourth live run (`63e9bb9` proposals), as produced | `63e9bb9` | 14/34 = 0.41 | 24/34 = 0.71 | 61/66 = 0.92 (entities 16/18, statements 45/48) | 0 | `ptfe_live_63e9bb9/review/` |
| Fourth live run | `0ade8f1` | **14/34 = 0.41** | 24/34 = 0.71 | **61/62** (entities 16/16, statements 45/46) | **0** | `ptfe_live_63e9bb9/revalidated_0ade8f1/review/` |

The first and second runs replayed at `0ade8f1` (`ptfe_live_replay_0ade8f1/review/`, `ptfe_live_e19b7c0/revalidated_0ade8f1/review/`) are unchanged: 17/34, 25/34, 64/65 and 18/34, 26/34, 61/62, 0 critical. Targets recovered by the closure code and not before: statements 20, 21, 23, 26, 27, 28 and relations 34 (first run); entities 7, 8, statements 21 and relations 31 (second run). The one remaining incorrect record per run is a non-critical role error (a narrative framing sentence typed as a conclusion; an instrument readout typed as an observation; the same framing sentence again in the fourth run). The fourth run's lower recall is model variance, not validation: it proposed no `madeOf` relation and no p4 specimen entity, typed statements 26 and 28 as conclusions or without subjects (held), and attached all 58 of its quantities to the Investigation, which the subject-applicability rule rejects, so the p7 and p9 narrative values (targets 14–16) were proposed but not retained.

### Live runs through the ordinary application

| Run | Code loaded | Calls / time | Status | Result |
| --- | --- | --- | --- | --- |
| `../numeric_expression_grammar/ptfe_live_2b7d1d6/` | `2b7d1d6` | 19 / 1,066 s | partial coverage | 10/34, 25/34, 25/32, 5 critical (two-lens review) |
| `ptfe_live_e19b7c0/` | `e19b7c0` | 13 / 783 s | partial coverage | as produced 51/56 with 1 critical; revalidated at `63e9bb9`: 18/34, 26/34, 61/62, 0 critical |
| `ptfe_live_6ba33aa/` | `6ba33aa` (its `summary.json.gz` prints `adeada4` because that commit landed while the process ran; the loaded modules were `6ba33aa`) | 39 / 2,078 s | partial coverage, deadline exceeded | 60 supported non-duplicate records, not reviewed; the pages 9–18 window was split for the first time, but 22 calls chased finished empty answers on pages 1–8 and the deadline deferred the halves and the relationships stage, which `63e9bb9` bounds |
| `ptfe_live_63e9bb9/` | `63e9bb9` (its `summary.json.gz` prints `09a9dda` because that docs-only commit landed while the process ran; the loaded modules were `63e9bb9`) | 16 / 1,954 s | partial coverage, within the deadline | as produced 61/66 with 0 critical (14/34, 24/34): one propositions window needed a context split and five recovery windows, its halves among them, were deferred by the remaining budget instead of chased (`DEFERRED_BUDGET`); the three role errors found (two `Table n—…` captions typed as experiment families, a test step typed as an observation, a validity caveat typed as an interpretation) are held at `0ade8f1`: 61/62, 0 critical |

### Five exposed v4 receipts replayed (`exposed_sources_replay/comparison.json`, `118ec71` → `0ade8f1`; identical counts to the `63e9bb9` replay, so the three holds of `0ade8f1` change nothing on these sources)

| Source | Previously supported, now held or rejected | Newly supported |
| --- | --- | --- |
| LUCI | 20: 18 incompatible roles on one span, 2 slide tables | 0 |
| PTFE (v4 run) | 6: 3 comparator lineage, 1 value-labelled entity, 1 procedure, 1 front matter | 35, read one by one; the role errors found were fixed at `adeada4` |
| Regulator | 4: 1 incompatible roles, 3 fragments (caption line, mid-sentence start, page-end auxiliary) | 9, read one by one |
| Textiles | 2: incompatible roles | 0 |
| Ignition | 1: sentence cut at "(e.g." | 0 |

### Other receipts at `0ade8f1`

- `historical_negatives_receipt.json`: the 21 critical false attributions of v4 (ignition 6, regulator 9, textiles 6) and the 5 critical ones of the first live PTFE review are all `REJECTED` or `UNRESOLVED` under the current validators; 0 critical regressions; 2 known non-critical incorrect records remain supported.
- `curation_projection_receipt.json`: on the PTFE package the curation layer now includes 46 `SOURCE_SUPPORTED` statements and holds 137 unresolved ones (41 cited) with `review_status`; 4 `madeOf` relations; 0 values (no vocabulary). Before the closure all 196 contextual statements were included and projected as `APPROVED`.
- `source_eligibility_receipt.json` (§8): the repaired screening applied to the five official citations on file; NTRS 20090043050 and 20170003941, which the old keyword gate rejected, are established by their own metadata (oxygen systems, EMU/PLSS; MSFC and JSC); the other three still pass.
- `table_structure_receipt.json`: layout recovery on the five sources (only PTFE prints continuation tables: pages 13, 16 and 17; 32 row groups; 96 legend-backed rows; 69 cited or external rows).
- `review_errata.json`: corrections to earlier review notes, in both directions, without editing frozen targets or earlier reviews.

## §18 matrix for this branch's part (M1, M2, integration)

Each PASS names its reproducible evidence; FAIL and PARTIAL say why.

| Item | Result | Evidence |
| --- | --- | --- |
| DOCUMENT_STRUCTURE_RECOVERY | PASS on the exposed corpus | continuation tables with inherited headers, row groups across pages, per-table legends (`table_structure_receipt.json`, `tests/test_table_continuity.py`); the section-title bug fixed (`tests/test_phase1_closure.py`) |
| TABLE_AND_BATCH_IDENTITY | PASS | batch cohorts recovered in both PTFE runs with the marker kept as an annotation and the legend recorded; entity ids no longer depend on the marker; a letter without a legend stays in the name; `Alpha-500` is not `Alpha` |
| NUMERIC_EXPRESSION_PARSING | PASS | `../numeric_expression_grammar/`, `tests/test_numeric_expressions.py` (bounds, grouping, ratios, lists, header units, CSV path) |
| QUANTITY_AND_UNIT_ATTRIBUTION | PARTIAL | every table quantity binds to its row group, printed cell and header unit (`UNIQUE` / `GROUP_CONSTANT` / `AMBIGUOUS` held); none can be accepted without property vocabulary, so 0/10 quantity targets are correct and 5/10 are retained |
| EXPERIMENT_AND_GROUP_IDENTITY | PARTIAL | batches, `madeOf` by printed name and specimen-material association recovered; conditions and interventions proposed on a Material are rejected as class contradictions, and the model omits the investigation-to-group relations |
| SCIENTIFIC_SCOPE_RESOLUTION | PASS for the mechanisms, recall-limited | document-investigation scope, cited attribution and cited tables, comparator lineage, local and anaphoric guards; statements 9/12 correct in both runs, the other 3 correctly held (count conflict, cited result, recording rule) |
| OBSERVATION_AND_CONCLUSION_ATTRIBUTION | PASS | the critical Table 3 dump rejected; criteria, caveats, pointers, procedures (including bare test steps), caption identities and incompatible roles held; 0 critical in every review at the closure code; the fourth run's three non-critical role errors held at `0ade8f1`; 1 known non-critical role error remains per run |
| SOURCE_TRACEABILITY | PASS | exact spans, printed-cell spans, original hash `c9de8948…`, SQLite `ok` in every run |
| SEMANTIC_AND_ONTOLOGY_REUSE | PARTIAL | existing ontology relation `madeOf` and existing accessors reused; no vocabulary activated; the property gap is documented, not bypassed |
| SCIENTIFIC_CONTENT_COVERAGE | FAIL | 14–18 of 34 targets correct; 8–10 omitted; quantities and relations are the gap, and the fourth run shows run-to-run variance on entities and relations |
| TARGETED_OMISSION_RECOVERY | PARTIAL | the oversized window is split and retried; retries bounded at `63e9bb9`: the fourth run finished in 16 calls within the deadline, but the halves were deferred by the remaining budget and the run still ended `PARTIAL_MODEL_COVERAGE` |
| HUMAN_REVIEW_REQUIREMENT_PREPARATION | PASS | unresolved records kept with `review_status` and `review_reasons`, grouped review requirements, nothing unresolved projected as approved |
| APPLICATION_END_TO_END_INGESTION | PASS | four live runs through `submit → save → prepare_scientific → validate`, no developer transformation, no credentials, 0 approvals/publications; §8 screening in `submit_ntrs` |
| INDEPENDENT_GENERALIZATION | NOT EVALUATED | §12 readiness not demonstrated (recall 0.41–0.53 on the exposed source); no holdout consumed |
| SCIENTIFIC_PRECISION | PASS on exposed PTFE after each review's holds (0.98, 0 critical; the fourth run measured 0.92 as produced), NOT EVALUATED on a frozen acceptance set | reviews above; by-kind precision in each `scientific_metrics.json` |
| SCIENTIFIC_RECALL | FAIL | 0.41, 0.50 and 0.53 against 0.80 |
| REGRESSION_AND_PRESERVATION | PASS | 643 tests; historical negatives receipt; originals and frozen v1–v4 receipts unchanged; earlier reviews kept beside the new ones, no review overwritten |
| PHASE1_COMPLETE | NO | acceptance needs a frozen holdout after readiness, and readiness needs the blockers below |

## Blockers for Liam

1. **Vocabulary and units.** The semantic registry has 4 properties and `units.py` lacks psi/psia, °C, J, ft-lbf and cal/g; every PTFE quantity target is bound and held for this reason alone. Approving properties (heat of combustion, AIT with the `>425 °C` bound kept, impact energy, test pressure, reaction counts as pairs) is ontology governance.
2. **Scorer semantics.** Targets whose correct handling is `UNRESOLVED` can never count as recovered; a "correctly held" outcome needs a new frozen protocol.
3. **Model omissions and variance** (prompts and stages): relations on the wrong class or not proposed at all (the fourth run has no `madeOf`), batch and specimen entities in one run and not the next, text quantities unbound; 179 vs 20 vs 103 vs 58 quantity proposals across runs of the same paper. In the fourth run all 58 quantities name the Investigation as their subject and the existing subject-applicability rule rejects them (`QUANTITY_SUBJECT_NOT_IN_APPLICABLE_SOURCE`); holding them for review instead would keep the narrative values, which is Liam's rule to change.
4. **Files of Liam's edited by this branch:** `document_extraction.py`, `document_structure.py`, `scientific_scope.py`, `pdf_quantities.py`, `services/curation.py`, `scripts/score_scientific_review.py` (additive) and the NTRS screening test. Saved prepared packages must be regenerated (`validate()` says "regenerate").
5. **Holdout.** Not run on purpose (§12).

## Reproduce

```bash
uv run python scripts/phase1_offline_replay.py artifacts/phase1_generalizable_ingestion/v5/numeric_expression_grammar/ptfe_live_2b7d1d6/prepared.json.gz --output /tmp/replay
```

```bash
uv run python scripts/score_scientific_review.py PREPARED.json REVIEW.json --output METRICS.json
```

```bash
uv run python scripts/phase1_exposed_live_run.py --pdf 20090043050.pdf --provenance-from artifacts/phase1_generalizable_ingestion/v4/independent_ptfe_application/prepared.json.gz --workspace OUTSIDE_REPO --directory OUT --timeout-seconds 1800
```

The scorer reads plain JSON (decompress `prepared.json.gz` first). The NTRS PDF is `c9de8948…`.

## Files

- `ptfe_live_replay_118ec71/`, `ptfe_live_replay_7997b58/`, `ptfe_live_replay_63e9bb9/`, `ptfe_live_replay_0ade8f1/`: the first live run's raw output replayed under the base, the first closure, the recovery bound and the final code; the last three carry `review/`.
- `ptfe_live_e19b7c0/`: second live run as produced, with `revalidated_7997b58/`, `revalidated_63e9bb9/` and `revalidated_0ade8f1/` (review in each).
- `ptfe_live_6ba33aa/`: third live run as produced (not reviewed; its lesson is the retry bound).
- `ptfe_live_63e9bb9/`: fourth live run as produced, with `review/` (judged as produced) and `revalidated_0ade8f1/` (the same raw output under the final code, with its review).
- `exposed_sources_replay/comparison.json`, `historical_negatives_receipt.json`, `curation_projection_receipt.json`, `source_eligibility_receipt.json`, `table_structure_receipt.json`, `review_errata.json`, `CHECKPOINT.md`.
