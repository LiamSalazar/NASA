# Package 4: diagnosis of each missed target (Sonnet at `a6d967b`, rounds 2 and 3)

> **Corrected after an independent review.** The version in `a72a0cb` had six errors:
> 1. `miss_diag.py` matched a quantity by its whole supporting sentence, not its printed value. Ignition quantities-07, -08 and -13 (6 pairs) are rejections or holds, not "graded wrong".
> 2. It ignored `pdf_table_quantity_proposals`.
> 3. It checked lost windows only by text sent anywhere. Ignition r2 window `window-8d3ec845` was `DEFERRED_BUDGET` (and `window-6574c939` was split without recovery), so "window lost 0" was false: 6 pairs.
> 4. The "15 misses that should stay missed" are not hits: no target carries `HOLD_IS_THE_CORRECT_OUTCOME`, and the scorer counts them as misses. They are reclassified below.
> 5. In r2 Sonnet did propose a wet-series group (`1c10959b`), but it merged both series.
> 6. Textiles quantities-05 to -07 were listed under two classes; the `basis` field was stale.
>
> The tool now reads value spans, table-cell proposals and the stage's own windows. The NVIDIA milestone 12 runs were rediagnosed with the same tool (`nvidia_m12_rediagnosis.json`), so the comparison stays like for like. `target_miss_diagnosis.json` is regenerated.

Built with `../tools/miss_diag.py . - target_miss_diagnosis.json milestone13/package4 a6d967b r1,r2`.
- **Runs:** the two package 4 rounds on frozen `a6d967b`, named `r1` and `r2` here.
- **Adjudication:** `evaluation_b.json`.
- **Cost:** none; no model call, and no target, scorer or judgment changed.
- **Classes:**
  - **window lost:** the stage's own windows covering the target were deferred, never split or failed, or none of the stage's answered requests carried its words;
  - **not proposed:** no record of the kind overlaps it, a quantity by its printed value;
  - **proposed and rejected:** overlapping records of the kind exist, none SOURCE_SUPPORTED;
  - **accepted, graded wrong:** a SOURCE_SUPPORTED record overlaps it, but the adjudication did not count it correct.

## Summary against NVIDIA (milestone 12 rounds, rediagnosed with the corrected tool)

Target-run pairs, two runs per source.

| source | model | correct r1 / r2 | not proposed | proposed and rejected | accepted, graded wrong | window lost |
|---|---|---|---|---|---|---|
| ignition | Sonnet `a6d967b` | 13 / 12 | 2 | 21 | 4 | 6 |
| ignition | NVIDIA `0a5a860` | 11 / 14 | 3 | 23 | 7 | 0 |
| regulator | Sonnet | 9 / 8 | 5 | 38 | 4 | 0 |
| regulator | NVIDIA | 14 / 17 | 3 | 27 | 3 | 0 |
| textiles | Sonnet | 10 / 10 | 14 | 11 | 13 | 0 |
| textiles | NVIDIA | 10 / 10 | 7 | 25 | 6 | 0 |
| **total** | Sonnet | 62 | 21 (18 %) | 70 (59 %) | 21 (18 %) | 6 (5 %) |
| **total** | NVIDIA | 76 | 13 (12 %) | 75 (72 %) | 16 (15 %) | 0 |

By category (target-run pairs, Sonnet / NVIDIA):

| category | not proposed | rejected | graded wrong | window lost |
|---|---|---|---|---|
| entities | 2 / 0 | 0 / 0 | 4 / 2 | 0 / 0 |
| quantities | 12 / 11 | 30 / 29 | 6 / 6 | 3 / 0 |
| statements | 4 / 0 | 36 / 40 | 8 / 4 | 3 / 0 |
| relations | 3 / 2 | 4 / 6 | 3 / 4 | 0 / 0 |

**What changed with Sonnet:**
- **Regulator.** Sonnet falls behind NVIDIA here, with 17 against 31 correct pairs.
  - NVIDIA proposed the printed test series as groups.
  - Sonnet proposed the test article (`Primary Oxygen Regulator (POR) 2.0, s/n 003`) and one dry group in both runs. In r2 it also proposed a single wet-series group (`1c10959b`) that merges the first and second series.
  - Its values and statements hang on the specimen or on the merged group, so the applicability contract holds them.
- **Textiles.** Sonnet proposes fewer records for the historical and assessment values, and types more slide bullets as documentary context.
- **Ignition.** r2 lost two propositions windows: one deferred by the token brake, one split without recovery.
- **Leading rejection code.** For Sonnet it is `STATEMENT_SUBJECT_APPLICABILITY_UNRESOLVED` (18 pairs, 3 sources), then `QUANTITY_SEMANTICS_OR_UNIT_UNRESOLVED` (15) and `QUANTITY_SUBJECT_NOT_IN_APPLICABLE_SOURCE` (8). For NVIDIA it is `QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT` (16).

## The 15 targets once called "should stay missed", reclassified

They are misses for the scorer, since no frozen target carries `HOLD_IS_THE_CORRECT_OUTCOME`. By what would recover them:

| class | targets | why |
|---|---|---|
| recoverable on the model side (6) | ignition quantities-16, statements-20, -22; regulator statements-15, -27, quantities-07 | The model typed them with the wrong role or study: a cited estimate as current, uncertainty or a non-causal statement as a conclusion, a cited partial test as an observation, model results as conclusions or configuration. The hold is right for what was proposed, and a correct proposal would pass. |
| validator too strict (4) | ignition quantities-13 (the printed typo "internal height if 30.5 cm" leaves the value unnamed), quantities-17 (a derived delta with no eligible subject); regulator statements-19 (the system-only adjustment held rather than scoped to the study), quantities-12 (the test-article alias review hold) | The target is source-supported as written, and the hold comes from a rule that is stricter than the target's expectation. |
| contract against target (3 mechanisms, 5 targets) | textiles statements-18 (held on the Background slide), statements-19 (a pass criterion the slide does not print as one), quantities-05, -06, -07 (the proposed Artemis atmosphere with no eligible subject) | The frozen expectation asks for what an integrity contract forbids as now written. This is for Liam to decide. |

The independent review estimated about 6 recoverable, 6 too strict and 3 clashes. The difference is in how the three textiles atmosphere values are counted: here they are one clash mechanism over three targets.

## General fixes, ranked by the targets they would recover

> The ranking below was made with the uncorrected diagnosis. Fixes 1, 2, 3 and 5 are done (`fixes.md`), and fixes 4, 6 and 7 are not. The miss counts it quotes are superseded by the tables above.

Estimates are made on the saved package 4 records without changing them. Where a figure is "simulated", the existing validator function was called on the saved record. None of these is a per-paper mapping. Each one would still need its classification, motivating source, effect on the other sources, and metamorphic and negative tests before it is written.

| # | fix (classification) | targets recovered (pairs, unique, sources) | evidence and risk |
|---|---|---|---|
| 1 | **Test series named in figure and table captions as group candidates** (document structure). A caption that names a series ("… During the First Dodecane Wetted POR Interstage Impact Test Series") is offered to identity as a printed group candidate, and `group_section_support` accepts the caption's figure passages. | up to 10 pairs, ≈ 6 targets, 1 source (regulator: entities-05, -06; then quantities-13, -14, statements-20, -22 if the model uses the series as subject) | NVIDIA proposed these groups and Sonnet does not. Only the entities are certain; the downstream targets depend on the model's subject choice, so this needs a live check. Risk: a caption naming a cited series; guard it with the existing cited-section checks. |
| 2 | **Running footer, page number and the next slide's labels cut from a statement's end** (document structure; extends 3.3 `page_edge_prefix` to the suffix and to slide decks) | 2 pairs, 1 target (textiles statements-22). Precision: 4 records judged incorrect for a glued footer or running header (textiles 2f8bd3b1, 71823c4e; ignition 070d8288, 93638799), in 2 sources | Deterministic. The footer is the deck's repeated line, already detected for running headers. Risk: a real last sentence that repeats the footer words; use the existing repeated-line detection only. |
| 3 | **A label that is the value's own setting verb passes the staged-name syntax** (semantic with evidence; closes a gap in 3.1, which runs only when the label is not printed) | 2 pairs, 1 target (ignition quantities-14, "rotated at 20.4 RPM"), simulated: `printed_setting_name` returns `PRINTED_SETTING_VERB_NAMES_VALUE` and it is the only reason held, in both runs. Regulator quantities-09 ("20uL was injected") also passes, but stays held by its subject (fix 1). | Sonnet labels these values with the verb itself, so 3.1 never ran. Risk: none new; same rule, other entry point. |
| 4 | **Dimension notation "A × B object"** (general notation): "the 5.2 cm by 14.0 cm samples" prints the object's two dimensions | 4 pairs, 2 targets (ignition quantities-07, -08), 1 source | Today the model labels both values "samples", which names the object, and the combined expression is rejected. Risk: "by" in a non-dimensional sense; require two values with one length unit. |
| 5 | **The token brake releases a network failure that received nothing** (orchestration): no first token, no usage, as for a refusal | 2 pairs, 2 targets (ignition r2 statements-23, -25), 1 source | Same mechanism as the refusal fix in `a6d967b`. A stream that received bytes keeps its reservation, since it may be billed. Alternative: a larger ceiling for long sources (spending decision for Diego). |
| 6 | **Math-font glyphs in PDF table labels** (document structure; already listed as detected) | 1 pair, 1 target (ignition quantities-28), 1 source | Units in row labels such as "𝜌 ሾ𝑘𝑔/𝑚ଷሿ" are not recovered. |
| 7 | **One test article named by its printed acronym** (would touch the applicability contract; not recommended without Liam) | ≤ 5 pairs, ≤ 3 targets (regulator statements-20, -23, -26), 1 source | It would also attach statements-19 to the POR, which is a false attribution. The contract stays as it is; fix 1 is the safe route to the same targets. |

**Total if all of fixes 1–6 worked as estimated:** about 21 pairs, ≈ 13 targets, over 3 sources.
- Mean recall per run would rise from 62/180 to about 83/180 (0.34 → 0.46) on the three non-PTFE sources.
- Only fixes 2–6 are deterministic and checkable offline: about 11 pairs, ≈ 7 targets.
- **The gate (recall ≥ 0.80) would still not be met on ignition, regulator or textiles.**

## What no deterministic fix reaches (model side)

- **Role errors** on the slide deck and in discussion sections:
  - implementation claims, goals and planned work typed as documentary context or publication (textiles statements-23, -24, -26, -27);
  - author conclusions for uncertain discussion (ignition statements-20, -22).
  These are request or prompt matters, or Phase 2 review, not validator rules.
- **Group equivalence across different names** ("Sixty test runs" against "60 dry pneumatic impact tests": regulator statements-17, quantities-11). Point A withdrew the count rule because it held a correct subject. This stays a model decision.
- **Historical and assessment values without an eligible subject** (textiles quantities-08, -09, -16, -17; -05 to -07 are the contract clash above). They need a staged class for that context. 2.1b offers one in the request, but the model never chose it in 12 runs.
- **Run-to-run model variability:** the same code gave ignition 13 and 12, regulator 9 and 8, and merged the wet series in r2.

## Open point for Liam: 2.1b

2.1b stays as it is: staging only, never approved, no effect on any record when unused. In 12 live Sonnet runs the model never used the `PROPOSE_NEW_CLASS` or `PROPOSE_NEW_RELATION` sentinels, even with a valid schema in 8 of them. The targets it was meant to reach (above) remain missed.

**Decision for Liam:** keep it inert, change how the request offers it, or remove it. The validator side (`adopt_proposed_term`, staging with an approved parent) is tested and does no harm.
