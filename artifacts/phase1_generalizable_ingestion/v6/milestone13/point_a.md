# Measurement point A (end of block 3)

**Kind:** evaluation A only. Saved inputs revalidated offline at HEAD (block 3 rules plus the `4b189de` dedupe). 0 model calls, no cost, about 5 minutes. No new inference.

## Set

- 50 saved inputs replayed by `phase1_offline_replay.py`, all completed:
  - the A set and evaluation B outputs of milestones 4–12;
  - the four round B packages (`*_live_b4be17d_r1`).
- The 29 historical negatives (`review_tools/exposed_compare.py`).

## Results

| check | result | gate |
|---|---|---|
| historical negatives | 29: 0 critical regressions, 1 known non-critical (unchanged) | pass |
| PTFE round B, official scorer | recall 28/34, precision 134/136, 0 critical | ≥ 27/34: pass |
| PTFE m12 r1 / r2, official scorer | 27/34 (96/104) and 28/34 (126/127), 0 critical | pass |
| critical errors, all sources | 0 | pass |

## Round B packages replayed against their own adjudication

Records keep their ids across replays. Fixed and lost come from the adjudication in `adjudication.json`. Newly supported records were judged by the branch author against the printed source. Target recall counts a target as gained only when a newly supported record carries it correctly.

| source | recall before → after | precision before → after | changes |
|---|---|---|---|
| textiles | 7/29 → **8/29** | 17/22 (0.773) → 19/23 (0.826) | 1 error fixed. statements-22 recovered (3.2 deck rule). New Publication record for the title slide and paper number, judged correct. |
| regulator | 10/32 → 10/32 | 16/30 (0.533) → 17/27 (0.630) | 5 errors fixed (3.4 mention hold). New conclusion "performed nominally ... entire impact series", judged correct. New GN2 set-up sentence typed as an observation, judged incorrect. |
| ignition | 15/29 → **16/29** | 86/115 (0.748) → 85/112 (0.759) | 3 errors fixed. quantities-14 recovered (3.1, "rotated at 20.4 RPM"). The cited/current dedupe holds the Nomex and Kevlar pairs, 2 correct cited records with them (no target lost). New "Figures 11 and 12 present ..." typed Publication, judged incorrect. |

## What point A shows

- Block 3 raises precision on every source and recovers 2 targets without losing any.
- The §13 gate is still not met:
  - only PTFE reaches recall ≥ 0.80;
  - textiles, regulator and ignition stay at 0.28–0.55.
- The remaining misses are mostly decisions the validator cannot make from saved proposals:
  - unlisted vocabulary (2.1b);
  - omitted narrative values (3.5);
  - group equivalence (3.4).
  All three need the model request to change, so only a live round can measure them (package 4).

## A rule withdrawn at point A

The count rule from package 3.4 ("Sixty test runs" is not a group name) was withdrawn. Its only occurrence is the subject of a correct statement (regulator statements-17), and holding it lost that target.

While checking this, an asymmetry showed up: when a proposed group subject is held, the statement falls back to the investigation scope. When the group is SOURCE_SUPPORTED but does not apply to the passage, the statement is held instead. With the group held, 8 regulator statements became supported (statements-22 and -24 among them), while statements-17 was lost and statements-28 went to a role conflict. This is recorded as package 3.2b, to be designed and measured on its own.

## After 3.2b and the procedure-step fix (re-measured, same set, 0 model calls)

### Changes

- **3.2b.** A statement whose proposed group subject is SOURCE_SUPPORTED but not shown to apply to the passage is scoped to the study, as a held group already was. The group stays a proposed subject only and is never distributed to members.
  - A supported individual run is never rescoped. This keeps the existing contract `test_literal_article_identity_does_not_invent_execution_or_override_cited_scope` unchanged.
  - Classification: document structure. Motivating source: regulator.
- **Procedure steps (general language).** Set-up steps ("was set up", "were performed", "injected", "adjusted") and a planned step ("was to perform 60 tests") are procedures, not observations, unless the passage prints an outcome. "Performed nominally" still counts as an outcome. This holds 3 regulator procedure sentences that 3.2b would otherwise have accepted.

### Results

| check | result |
|---|---|
| inputs replayed | 50/50 |
| historical negatives | 29: 0 critical regressions, 1 known non-critical |
| PTFE round B, official scorer | 28/34, 134/136, 0 critical |
| PTFE m12 r1 / r2 | 27/34 (96/104) and 28/34 (127/128), 0 critical |
| PTFE m12 r2, new record | "Two additional batches ... zero reactions" at study scope, judged correct |
| textiles | 8/29, 19/23 (0.826) |
| regulator | 10 → **11/32**, 16/30 (0.533) → **21/30 (0.700)** |
| ignition | 16/29, 86/114 (0.754) |
| critical errors | 0 |
| pytest | 878 passed |

Regulator details:
- Targets 22 and 24 recovered. Target 28 goes to a genuine role conflict: its observation reading now also has valid scope, so both readings are held.
- 6 newly supported observations, all judged correct.

Ignition: the study-scope fallback adds 2 condition statements:
- "This required a test program ..." is judged incorrect;
- "The igniter was a ceramic igniter ..." is judged correct.

### Recall after block 3 and 3.2b

| source | recall |
|---|---|
| PTFE | 28/34 (0.82) |
| ignition | 16/29 (0.55) |
| regulator | 11/32 (0.34) |
| textiles | 8/29 (0.28) |

The §13 gate is not met.
