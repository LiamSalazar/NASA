# Phase 1 v6, milestone 5: precision rules, printed-structure recall, and what the frozen-code runs show

**Status: `PHASE1_COMPLETE=NO`.**

Exposed development source only (PTFE, NTRS 20090043050, 36 frozen targets, 34 accessible). Reviews are the branch author's adjudications from full records, not expert gold. No holdout has been consumed.

**Stability check, not closure.** As decided on 2026-10-20, consecutive satisfactory runs on PTFE are a stability check and are **not** the criterion for closing the phase. The source was exposed during development. Closure requires:
- stable recovery over several development investigations;
- then a prospective, independent evaluation with frozen code and contracts on an unexposed NASA lineage (§14 criteria unchanged).

## What changed (`diego/research`, main untouched at `54445d0`)

| Commit | Change |
| --- | --- |
| `fe4f1bb` | Run-9 error families. A substance named only as the test medium ("pressurized with GOX", "submerged in LOX") is not a tested material. "The same / These same …" after cited work (citation, reference author, prior work or a cited table within three sentences, across page breaks) is that cited work. An interpretation that only reports a test or examination step is a procedure. "The indication of X was the …" is a detection criterion. |
| `a2c5a28` | Scope recovery. A cited family name inside a current variant's name ("E2 Algoflon®") no longer blocks the study scope. Specimen statements that name the specimens or their material are scoped to the study. A conclusion held only for context that reports an outcome is revalidated as an observation. |
| `368830d` | A name printed in a table's Material column proposed as an ExperimentFamily is revalidated as a Material. Values bind to subjects only within their own contrast clause (", whereas / while / but"). This fixed a critical attribution in run 10, where a model gave Fluorel® Teflon's 1,500 psia. Test methods or measured properties are not conditions. A documentary statement that reports what a picture shows is revalidated as an observation. |
| `160d73f` | Printed relations (batch madeOf material, row conditions) are proposed beside the model's own, and identical relations are consolidated. A recording rule held for a specimen subject is recovered at the study's scope. |
| `ca2f172` | A tentative interpretation must hedge or infer. |
| `8c20561`, `134b543` | Specimen set-up steps are the study's procedure. A statement carrying the document's running page header beside its page number is not a whole sentence. `8c20561` was committed with two failing tests, which `134b543` fixed. |
| `160a931` | Printed batch row groups of a tested material are proposed as specimen groups. Generic specimen descriptions ("reacting sample"), conditions named only in cited work and instrument readouts are held. Subject recovery never gives a value to an entity its own passage does not name. |
| `a191b56` | A tested material's own numeric table cells, under a header that prints a unit, are proposed for the validator. Identical row-bound values are consolidated. Material-named samples are retyped to Material. A held conclusion that states a rule, a data source or a procedure is revalidated with that role at study scope. |
| `77828b9` | A candidate identical to a model proposal is skipped instead of validated twice under one id. The official scorer refused that duplication. |

Every rule above is general: it uses the document's own wording, structure, tables or references, with no rule for a material name. Quality at `77828b9`: `ruff format --check`, `ruff check`, `pytest` (695 tests).

## Live runs this milestone

All runs used a 3,600 s budget and produced 0 approvals.

| Run | Code at run time | Calls / time | At its own code | At `77828b9` (raw proposals replayed) |
| --- | --- | --- | --- | --- |
| 10 (`ptfe_live_fe4f1bb/`) | `fe4f1bb`, edited during the run (`uncommitted_src_changes: true`) | 14 / 1,563 s | — | 28/34, 104/104 |
| 11 (`ptfe_live_160d73f/`) | `160d73f` | 21 / 2,738 s | — | 28/34, 132/133 |
| 12 (`ptfe_live_134b543/`) | `134b543` frozen | 15 / 1,488 s | **24/34, 85/91 = 0.934**, 0 critical | 28/34, 114/115 |
| 13 (`ptfe_live_160a931/`) | `160a931` frozen | 18 / 2,154 s | **18/34, 90/100 = 0.900**, 0 critical | 26/34, 133/136 |

A 14th run did not start: the PC went offline, and the empty directory was removed.

**The frozen-code confirmations failed** (`frozen_code_confirmation/`):
- Run 12: the model did not propose the batch groups.
- Run 13: the model omitted most table quantities and typed procedures, rules and data sources as conclusions.

The later rules recover much of this, but the same model calls on the same document still produce different results.

## All reviewed runs at `77828b9` (`rescored_77828b9/`, official scorer)

Twelve runs, 0 critical in every one:

| Recall | Runs | Precision |
| --- | --- | --- |
| 28/34 = 0.82 | 1, 2, 4, 6, 8, 9, 10, 11, 12 | 0.982–1.000 |
| 27/34 | 7 | 0.989 |
| 26/34 | 13 | 0.978 |
| 25/34 | 5 | 0.979 |

- **Correct in every run:** 24 targets.
- **Never correct:** 14 and 17 (relative percentages against cited data), 18 and 33 (Salox-M® composition, now milestone 6), 24 (a cited result), 25 (a correct hold), plus the two figure targets, which are inaccessible.

**Other sources and negatives** (`exposed_sources_comparison.json`, `historical_negatives_receipt.json`), against the c314286 replays:

| Source | Change |
| --- | --- |
| LUCI | Unchanged. |
| Textiles | 1 title-slide statement held. |
| Regulator | 9 set-up statements on its one tested unit scoped to the study; 2 held. |
| Ignition | 3 caption-named materials retyped from Sample to Material. |
| Historical negatives (29) | 0 critical regressions. |

The branch author read every new SOURCE_SUPPORTED record outside PTFE; none is critical.

## What remains

1. **Milestone 6: material composition.** Generic component relation in staging; component role and proportions with documented basis; explanations generated from the structured relations; no global ontology change.
2. **Stability over several development investigations.** The run-to-run variance comes from what the model proposes. Printed-structure candidates and role recovery reduce it, but the frozen-code runs show it is not yet stable.
3. **Readiness gate (§13), then the independent prospective evaluation** on an unexposed NASA lineage with frozen code and contracts.
