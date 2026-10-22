# Package 4: diagnosis of each missed target (Sonnet at `a6d967b`, rounds 2 and 3)

Built with the milestone 13 tool (`../tools/miss_diag.py . - target_miss_diagnosis.json milestone13/package4 a6d967b r1,r2`, receipt `target_miss_diagnosis.json`).
- **Runs:** the two package 4 rounds on frozen `a6d967b`, named `r1` and `r2` here.
- **Adjudication:** `evaluation_b.json`.
- **Cost:** none. No model call was made, and no target, scorer or judgment was changed.

**Classes,** as in milestone 13. Overlap is by evidence span, so a rejected record that only shares the sentence counts as a proposal.
- **window lost:** no finished request carried the target's words.
- **not proposed:** no record of the target's kind overlaps it.
- **proposed and rejected:** overlapping records of the kind exist, none SOURCE_SUPPORTED.
- **accepted, graded wrong:** a SOURCE_SUPPORTED record overlaps it, but the adjudication did not count it correct.

## Summary against NVIDIA (milestone 13 diagnosis of the milestone 12 rounds)

Target-run pairs, two runs per source.

| source | model | correct r1 / r2 | not proposed | proposed and rejected | accepted, graded wrong | window lost |
|---|---|---|---|---|---|---|
| ignition | Sonnet `a6d967b` | 13 / 12 | 9 | 16 | 8 | 0 |
| ignition | NVIDIA `0a5a860` | 11 / 14 | 3 | 19 | 11 | 0 |
| regulator | Sonnet | 9 / 8 | 5 | 38 | 4 | 0 |
| regulator | NVIDIA | 14 / 17 | 3 | 25 | 5 | 0 |
| textiles | Sonnet | 10 / 10 | 14 | 11 | 13 | 0 |
| textiles | NVIDIA | 10 / 10 | 7 | 25 | 6 | 0 |
| **total** | Sonnet | 62 | 28 (24 %) | 65 (55 %) | 25 (21 %) | 0 |
| **total** | NVIDIA | 76 | 13 (12 %) | 69 (66 %) | 22 (21 %) | 0 |

By category (target-run pairs):

| category | model | not proposed | rejected | graded wrong | missed |
|---|---|---|---|---|---|
| entities | Sonnet | 2 | 0 | 4 | 6 |
| entities | NVIDIA | 0 | 0 | 2 | 2 |
| quantities | Sonnet | 17 | 24 | 10 | 51 |
| quantities | NVIDIA | 11 | 23 | 12 | 46 |
| statements | Sonnet | 6 | 37 | 8 | 51 |
| statements | NVIDIA | 0 | 40 | 4 | 44 |
| relations | Sonnet | 3 | 4 | 3 | 10 |
| relations | NVIDIA | 2 | 6 | 4 | 12 |

**What changed with Sonnet:**
- **Regulator** is where Sonnet falls behind NVIDIA (17 against 31 correct pairs).
  - NVIDIA proposed the printed test series as groups: "Sixty test runs", "First Dodecane Wetted POR Interstage Impact Test Series" and the second series.
  - Sonnet proposes only the test article (`Primary Oxygen Regulator (POR) 2.0, s/n 003`) and one dry group, so its values and statements hang on the specimen. The specimen applicability contract holds them: a Sample is applicable only on its own evidence page.
  - So 38 of the 47 regulator misses are rejections, mostly `STATEMENT_SUBJECT_APPLICABILITY_UNRESOLVED` and `QUANTITY_SUBJECT_NOT_IN_APPLICABLE_SOURCE`.
- **Textiles:** Sonnet proposes fewer records for the historical and assessment values (14 not proposed) and types more slide bullets as documentary context or publication (13 graded wrong).
- **Ignition:** the not-proposed pairs come mostly from r2, where one propositions window was deferred by the token brake after two network failures (statements-23, -25; package 4 README).
- **The leading rejection code changed.** NVIDIA's was `QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT` (10 pairs), which block 3 addressed. Sonnet's codes:

| code | pairs | sources |
|---|---|---|
| `STATEMENT_SUBJECT_APPLICABILITY_UNRESOLVED` | 18 | ignition, regulator, textiles |
| `QUANTITY_SEMANTICS_OR_UNIT_UNRESOLVED` | 10 | ignition, regulator, textiles |
| `QUANTITY_SUBJECT_NOT_IN_APPLICABLE_SOURCE` | 9 | regulator, textiles |
| `RELATION_SUBJECT_OBJECT_NOT_IN_APPLICABLE_SOURCE` | 4 | regulator |
| `AUTHOR_ROLE_REQUIRES_CONTEXT_REVIEW` | 3 | ignition |
| others (≤ 2 each) | 21 | |

## Misses that should stay missed (correct holds by an immutable contract)

These are not recall to be recovered. A rule that turned them into recall would weaken experiment identity, applicability, roles or values.

| target | why the hold is right |
|---|---|
| ignition quantities-13 | the source prints "an internal height if 30.5 cm"; the typo leaves the value unnamed, and the frozen expectation preserves it |
| ignition quantities-16 | a cited estimate (Takahashi) proposed as a current reported quantity |
| ignition quantities-17 | a derived worst-case delta with no eligible subject |
| ignition statements-20, -22 | discussion sentences typed as author conclusions; the expectation is explicit uncertainty or a tentative non-causal statement |
| regulator statements-15 | a cited partial test typed as an observation |
| regulator statements-19 | the 80–93 msec times were measured before the POR was reconnected; attaching them to the POR would be a false attribution |
| regulator quantities-07, statements-27 | Thermal Desktop model results; held as not observed |
| regulator quantities-12 | the deliberate test-article alias hold (`TEST_ARTICLE_ALIAS_…`) |
| textiles statements-18 | held on the Background slide (3.2) |
| textiles statements-19 | the pass-criterion role would come from knowing NASA-STD-6001, not from the slide (3.3) |
| textiles quantities-05 to -07 | the proposed Artemis atmosphere has no eligible experimental subject (3.5) |

That is 15 of the 61 targets missed in at least one of the two runs (counting targets, not pairs).

## General fixes, ranked by the targets they would recover

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
- **Historical and assessment values without an eligible subject** (textiles quantities-05 to -09, -16, -17). They need a staged class for that context. 2.1b offers one in the request, but the model never chose it in 12 runs.
- **Run-to-run model variability:** the same code gave ignition 13 and 12, regulator 9 and 8, and merged the wet series in r2.

## Open point for Liam: 2.1b

2.1b stays as it is: staging only, never approved, no effect on any record when unused. In 12 live Sonnet runs the model never used the `PROPOSE_NEW_CLASS` or `PROPOSE_NEW_RELATION` sentinels, even with a valid schema in 8 of them. The targets it was meant to reach (above) remain missed.

**Decision for Liam:** keep it inert, change how the request offers it, or remove it. The validator side (`adopt_proposed_term`, staging with an approved parent) is tested and does no harm.
