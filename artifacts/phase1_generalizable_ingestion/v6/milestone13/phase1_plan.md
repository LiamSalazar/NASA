# Phase 1: what remains, how metrics rise, and how the phase closes

Written on 2026-10-22 from the milestone 7 to 13 READMEs, the target miss diagnosis, the precision breakdown of round B, the Sonnet/Opus pilot and the paused batch 2. Every item below was planned or found and is not yet done. Each line names where it came from.

## Where Phase 1 stands

- §13 gate: recall ≥ 0.80 stable across several sources, precision ≥ 0.95 and 0 critical errors. It is **not met**.
- Latest live recall (Sonnet pilot and round B):
  - PTFE 28/34 (0.82);
  - ignition 14–15/29 (0.48–0.52);
  - regulator 10/32 (0.31, NVIDIA only);
  - textiles 9/29 (0.31).
- Precision: 0.70–0.99. Critical errors: 0 in every run.
- Development model: `claude-sonnet-5-5` (pilot decision; making it the primary model waits for Liam).
- The frozen holdout (NTRS 20170004702) stays unacquired until the gate is met.

## How metrics rise: the misses by cause

Round B diagnosis (`target_miss_diagnosis.md`, and the same tool for round B): 66 % of missed targets were proposed by the model and rejected by a rule, 21 % were accepted but graded wrong, 12 % were not proposed, and 0 % were lost windows. So most of the gain is in general criteria, measured for free by replay; only "not proposed" needs model calls.

### A. Rejected proposals: general criteria, measured by replay (free)

1. `QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT`, the leading code. Example: "the chamber was rotated at 20.4 RPM".
   - The model almost never fills `printed_name` (0–2 proposals per run).
   - The rule `PRINTED_SETTING_VERB_NAMES_VALUE` is written with 8 tests in batch 2 (worktree `nasa-batch14`, commit `2a94309`, paused); its replay was not completed.
   - Origin: milestone 9 Next, milestone 13 Pending, batch 2.
2. `STATEMENT_SUBJECT_APPLICABILITY_UNRESOLVED` (7 target-run pairs in round B) and `STATEMENT_REQUIRES_EXPERIMENTAL_SCOPE`. Origin: miss diagnosis.
3. `QUANTITY_UNIT_NOT_BOUND_TO_EXPRESSION` and `QUANTITY_SEMANTICS_OR_UNIT_UNRESOLVED`. Origin: milestone 9 Next, miss diagnosis.
4. `RELATION_SUBJECT_OBJECT_NOT_IN_APPLICABLE_SOURCE`. Origin: miss diagnosis.
5. `STATEMENT_INCLUDES_A_RUNNING_PAGE_HEADER`: slide footers inside statements. Origin: miss diagnosis, milestone 7 Next (slide decks).

### B. Accepted but graded wrong: precision by structure (free, by replay)

6. A Material with no measurement, condition or configuration of its own in the current study is not an entity of the study.
   - 10 of 48 errors in round B: Nomex, Kevlar, WD-40, Fomblin, Sebacate, Apollo-era fibres.
   - Origin: precision breakdown, coordinator note of 2026-10-21 23:54.
7. A count before "tests" or "runs" ("Sixty test runs") does not name a group. The current rule `PRINTED_NAME_OF_SEVERAL_TESTS_IS_A_GROUP` accepts it. Origin: same breakdown.
8. Statement roles (observation, conclusion, experimental condition) require their printed signal; planned strategy phases are neither executed groups nor interventions.
   - About 25 of 48 errors, plus the strategy phases Sonnet typed in textiles.
   - Origin: breakdown and pilot.
9. Group restatements ("1-g testing", "lunar-g testing") duplicating a named group. Origin: breakdown.

### C. Not proposed: directed model calls (costs API, small)

10. Subsection- and slide-directed calls for groups whose subsection prints values the model did not propose. Origin: milestone 8 Next (items 1–2), milestone 7 Next (items 1–2).

### D. Verifications pending (deferred by Diego; run only when asked)

11. The 29 historical negatives and the full 46-input replay with the duplicate change (`4b189de`).
12. A live measurement of the validation reuse (`24f09e3`).
13. Record-by-record precision review on regulator with Sonnet: regulator has never run on Sonnet. Origin: milestone 7–8 Next.

## How Phase 1 closes

1. **Batches of general criteria, one commit each.** Each rule is classified under the addendum, with its motivating source and its effect on the other three sources, plus metamorphic and negative tests.
   - Measured by the 46-input replay: free, about 5 minutes since `ae420ab`.
   - Guards: 29 negatives with 0 critical, PTFE not below 27/34.
   - Order: A1 (batch 2), A2, B6–B8, then A3–A5.
2. **After each batch, one Sonnet evaluation B round** on the four sources: about $3–5, about 15 minutes in pairs. All runs are reported, with the causes of variation.
3. **When a round reaches the gate on the four sources,** a second round confirms stability, so the result does not rest on one good generation. Then the leave-one-source-out check (milestone 8–9 Next).
4. **Freeze the code**, then acquire and run the holdout NTRS 20170004702 once, with Opus optionally as a confirmation.

Budget: about $5 per batch round. Three to five batches plus confirmation and holdout come to about $30–40 of the monthly $100, with $96 left today.

## Decisions waiting on someone

- **Liam:**
  - Sonnet 5.5 as the primary model. The pilot recommends it: faster, no failures, higher precision.
  - Whether a rule family needs his review before it lands.
- **Diego:**
  - when to resume batch 2;
  - when to run the deferred verifications (D11–D13).
