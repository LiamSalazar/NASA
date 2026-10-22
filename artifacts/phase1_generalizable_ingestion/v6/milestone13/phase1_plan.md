# Phase 1: canonical record (requirements, state, evidence, next action)

This is the single canonical record of Phase 1 work. Do not create competing plans: update this file and `CONTINUATION.md` (repo root) at the end of every work package. The requirements come from `docs/PHASE1_MASTER_DIRECTIVE.md` (master directive and addendum) and `docs/NASA_FIRE_AI_MASTER_PLAN_2026-10-14.pdf`. Repository rules are in `CLAUDE.md` and `AGENTS.md`.

**States:** `implemented-verified`, `in progress`, `blocked` (reason given), `pending`.

**Protocol per package:**
1. Tests and ruff green.
2. One commit as Diegomed11, without trailers.
3. Push to `diego/research`.
4. Update this table and `CONTINUATION.md`.
5. Short report to Diego.

A cut session resumes at the first package not done.

**Cost policy:**
- No live runs unless truly necessary and authorized.
- The free full replay (46 saved inputs, 29 historical negatives) runs only at measurement point A, at the end of block 3, not per rule.

## Where Phase 1 stands (2026-10-22, HEAD `c780d00`)

- §13 gate: recall ≥ 0.80 stable across several sources, precision ≥ 0.95 and 0 critical errors. It is **not met**.
- Latest live recall:
  - PTFE 28/34 (0.82);
  - ignition 14–15/29;
  - regulator 10/32 (NVIDIA only);
  - textiles 9/29.
- Precision: 0.70–0.99. Critical errors: 0 in every run.
- Development model: `claude-sonnet-5-5` (pilot, `pilot_anthropic/README.md`). NVIDIA stays the default provider; changing the primary model waits for Liam.
- Holdout NTRS 20170004702 stays unacquired.
- Round B miss causes (104 target-run pairs, `target_miss_diagnosis.md`):
  - rejected by a rule: 69 (66 %);
  - accepted but graded wrong: 22 (21 %);
  - not proposed: 13 (12 %);
  - lost window: 0.

## Work packages

| id | requirement (directive §) | state | evidence | next action |
|---|---|---|---|---|
| 0.1 | Save the directive and master plan in the repo | implemented-verified | `docs/PHASE1_MASTER_DIRECTIVE.md`, `docs/NASA_FIRE_AI_MASTER_PLAN_2026-10-14.pdf` | — |
| 0.2 | Root `CLAUDE.md`: vision, six phases, F1/F2 boundary, immutable vs adaptive contracts, LLM limits, scientist role, no overfitting, inspect first, assistants not runtime deps, links (§1, addendum §8) | implemented-verified | `CLAUDE.md` | — |
| 0.3 | This file as the single canonical record; `CONTINUATION.md` | implemented-verified | this file, `CONTINUATION.md` | — |
| 1.1 | Capability table against real code: SemanticRegistry, scientific proposals, semantic and composition modules, extension staging, SHACL, resolvers, quantities and units, validators, CurationService, coverage. Each verified, defective, partial, missing or dependent on scientific authority (§6, §8) | implemented-verified | `capabilities.md`: 14 capabilities (5 verified, 7 partial, 1 defective or missing, 1 scientific authority) and 10 rigidities | — |
| 1.2 | Classify the 69 rejected target-run pairs (addendum §1) as A (must stay rejected), B (contract too rigid) or C (valid evidence, incomplete association), from saved receipts | implemented-verified | `rejected_classification.md`/`.json`: A 19, B 20, C 30 pairs (12, 12, 19 targets) | — |
| 1.3 | Does the scorer distinguish complete staged extraction, proposed extension, ambiguity, uninterpreted evidence and publication? If it requires global publication, write a correction proposal for Liam; never change the scorer (addendum §3) | implemented-verified | `scorer_review.md`: no publication requirement; staged properties already count; the rigidity is in validation (unregistered class, unprinted name) | no proposal for Liam needed |
| 2.1a | One proposal state per record; staged class, statement-class and relation extension proposals instead of a bare `UNRESOLVED`, reusing the existing staging of `ontology_extension_proposals` (§5, §6) | implemented-verified | `proposal_states.py`, `tests/test_vocabulary_extension_proposals.py` (4); pytest 811 | Finding: the saved outputs have 0 such records, because the model request restricts `class_id` and `relation` to the approved lists (schema enum). |
| 2.1b | Let the model request carry an explicit new-class or new-relation proposal (an unlisted term with an approved parent and evidence), still validated, instead of forcing an approved term (§9) | pending | the 2.1a finding | This changes the model request and cache keys, so it can only be measured live (package 4). |
| 2.1c | Isolated validation of staged proposals; fix `approve_extension` `StopIteration`; derive `SCIENTIFICALLY_REVIEWED` and `AUTHORIZED_PUBLISHED` from curation | implemented-verified | `proposal_states.structural_validation` (identifier, clash or case-only clash with approved terms, evidence anchors, relation domain and range, no activation, no unsupported definition, placement); `CurationService.proposal_states` (derived from the exact approved and active digest, nothing written into records); `tests/test_proposal_states.py` (10); pytest 821 | SHACL on a staged copy needs a parent, so it waits for placement in review (Phase 2 activation path, `activate_extension`) |
| 2.1d | Entities and statements with unregistered classes kept in the package as proposed-extension items in a Phase 2 shape, not skipped | pending | `capabilities.md` rigidities 2, 3 | after 2.1c |
| 2.2 | Directive §6 distinctions: class vs instance, subclass vs attribute, equivalent vs similar, material vs specimen, component vs formulation, configuration vs observation, measurement vs derived, property vs unit, new relation vs qualified existing one | pending | — | after 1.1 |
| 2.3 | Tests: reuse, partial extension, new concept, with no paper-specific code (§12, deliverable C) | pending | — | with 2.1 and 2.2 |
| 3.1 | Quantity names from the printed clause, not rigid linguistic rules ("was set to" by context). Batch 2 drafted `PRINTED_SETTING_VERB_NAMES_VALUE` with 8 tests (worktree `nasa-batch14`, commits `2a94309` and `1a31301`); review it against addendum §6 (addendum §6) | in progress (paused) | batch 2 commits | review the rule against "no rigid linguistic rules" before landing |
| 3.2 | Experimental scope and missing subjects (category C): `STATEMENT_SUBJECT_APPLICABILITY_UNRESOLVED`, `STATEMENT_REQUIRES_EXPERIMENTAL_SCOPE` (addendum §6) | pending | miss diagnosis | after 1.2 |
| 3.3 | Units disconnected from values; relations needing reconstructed source context; table headers and slide footers inside statements (addendum §6) | pending | miss diagnosis codes | after 1.2 |
| 3.4 | Precision by structure: Materials only mentioned (10 of 48 round B errors); counts read as groups ("Sixty test runs"); planned procedures read as executed groups or interventions; group restatements (addendum §6) | pending | precision breakdown, pilot | after 1.2 |
| 3.5 | Targeted recovery from tables and narrative for source-backed content the model omits (§9, addendum §8) | pending | milestone 7–8 Next | after 3.1–3.4 |
| A | Measurement point A: 46-input replay, 29 negatives, PTFE ≥ 27/34, 0 critical (free) | pending | — | after block 3 |
| 4 | One Sonnet round on the four sources, only if 2.1 or 3.5 change the model request; the cost is announced first (addendum §5) | pending | — | needs authorization |
| 5 | Main Phase 1 report updated with milestones 9–13, pilot and orchestration; metrics with denominators and intervals per investigation and category (addendum §8, §11) | pending | — | after A |
| 6 | Stability, leave-one-source-out, heterogeneous independent evaluation, freeze, holdout, deliverables A–J (§12, §18, §19) | pending | — | later |

## Already done in milestone 13 (evidence)

- Precision by printed structure: background, theory and analysis holds (`527605b`).
- One statement per printed sentence across windows (`4b18bf5`).
- Model-copied `printed_name` (`18b73d9`).
- Orchestration:
  - local recomputation once per document (`ae420ab`);
  - per-call timing and per-run summary (`ae642ed`);
  - window prefetch (`3e746b1`);
  - validation reuse (`24f09e3`).
- Anthropic transport (`09bef51`) and token ceiling as a spending brake (`0a88478`).
- Duplicates: shared printed value and current/cited conflict (`4b189de`).
- Pilot Sonnet against Opus (`5ebec7b`, `2306d58`).
- Receipts: `README.md`, `evaluation_b.json`, `target_miss_diagnosis.md`, `pilot_anthropic/`.

## Detected and not yet addressed (feeds the packages above)

- `QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT` is the leading rejection; the model almost never fills `printed_name`. → 3.1
- Strategy phases and author claims typed as executed groups, interventions or documentary context (Sonnet textiles). → 3.4
- Regulator has never run on Sonnet. → 4
- Not measured live: the validation reuse (`24f09e3`) and the prefetch gain on long sources. → 4

## Pending verifications (only when Diego asks)

- The 29 historical negatives and the full 46-input replay with the duplicate change. → A
