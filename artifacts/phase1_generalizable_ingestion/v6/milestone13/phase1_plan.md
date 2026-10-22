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
| 2.1d | Entities, statements and relations whose only obstacle is unregistered vocabulary kept in the package as proposed-extension items in a Phase 2 shape, not skipped | implemented-verified | `CurationService.attach_scientific_proposals` → `package.proposed_extension_items` (term, extension proposal id, evidence, state, `included: false`); never projected; idempotent; test in `tests/test_proposal_states.py`; pytest 822 | — |
| 2.2 | Directive §6 distinctions: class vs instance, subclass vs attribute, equivalent vs similar, new relation vs qualified existing one (material vs specimen, configuration vs observation, measurement vs derived and property vs unit were already covered, `capabilities.md` #7) | implemented-verified | `proposal_states.reuse_analysis`: case A reuse of an equivalent approved term (an error, so the term is reused); case B a qualified approved class (parent candidate, subclass or attribute for review) or a relation whose endpoints an approved relation links (new or qualified); case C new; a term naming an instance is an error; `tests/test_reuse_analysis.py` (8); pytest 830 | component vs formulation stays in `composition.py` (partial, `capabilities.md` #6) |
| 2.3 | Tests: reuse, partial extension, new concept, no paper-specific code (deliverable C) | implemented-verified | unit tests in `test_reuse_analysis.py`, `test_vocabulary_extension_proposals.py`, `test_proposal_states.py`; end to end through `prepare_scientific`, staged as `CANDIDATE_NEW_CONCEPT` with the approved vocabulary unchanged (`test_extension_staging_end_to_end.py`); fixed staging status for class proposals (previously always `CANDIDATE_RELATION`); pytest 831 | — |
| 3.1 | Quantity names from the printed clause, not rigid linguistic rules ("was set to" by context) (addendum §6) | implemented-verified (replay at point A) | `PRINTED_SETTING_VERB_NAMES_VALUE` (`cc17ba6`). Classification: semantic with evidence. Motivating source: ignition ("rotated at 20.4 RPM") and regulator ("20uL was injected"), class B in `rejected_classification.md`. Review against §6: provides name evidence only and never decides the role, so it requires a configuration already proposed by the model; no verb list, only a shared stem (≥ 5 letters) with the label plus the verb governing the value; "set to" does not trigger it; conditional clauses, times and percentages excluded. 8 tests (2 positive, 6 negative or metamorphic). | measure at point A with the other block 3 rules |
| 3.2 | Experimental scope and missing subjects (category C): `STATEMENT_SUBJECT_APPLICABILITY_UNRESOLVED`, `STATEMENT_REQUIRES_EXPERIMENTAL_SCOPE` (addendum §6) | implemented-verified (replay at point A) | Diagnosed on the round B saved packages, without model calls. Two rules. (1) `d81098d`, document structure: in a slide deck the slide number printed before a title ("2 Background") was read as an outline number, so "Background" governed slides 3–9. Now a heading governs only its own slide, and a slide without one is the section its title names. A deck slide reports the presenter's own work unless its title names background, prior work or literature, or frames the talk (title slide, agenda, questions). Cited work stays excluded by the existing checks. Detection fix: one short line repeated on every page is a running header, not a slide title, so the laptop paper is no longer taken for a deck. Motivating source: textiles (statements-22 and -23 now get the deck's investigation scope; statements-18 stays held on the Background slide). Effect on the others: decks only (textiles); ignition, PTFE and regulator are papers and unchanged; laptop changes from deck to paper. (2) `b0ad37b`, general science of procedure language: "prior to" followed by a step's verb ("prior to re-connecting") orders a procedure, not earlier research. Motivating source: regulator statements-19. Effect: only passages that say "prior to ...ing". Tests: `test_slide_deck_sections.py` (5, including the metamorphic running-header case and the negatives background, prior work, frame and cited), `test_procedural_prior.py` (6: 3 positive, 3 negative); pytest 851. Not changed, with reason: ignition statements-19 and -25 now fail on role (`OBSERVATION_DESCRIBES_A_PROCEDURE`, uncertainty) rather than scope (→ 3.4); regulator statements-16 is typed as an observation for a configuration sentence, so opening its scope would accept a wrong role; regulator statements-15 cites reference (9) and stays held. | measure at point A |
| 3.3 | Units disconnected from values; relations needing reconstructed source context; table headers and slide footers inside statements (addendum §6) | implemented-verified (replay at point A) | `7815b14`, diagnosed on the saved round B packages and their saved document structure, no model calls. (1) Document structure: a table may print a spanning title row and the column names under it; a column's header now includes every text-only row above the first data row (`pdf_quantities.column_header`). Motivating source: ignition Table 2 (quantities-29, the s/cm slope columns). (2) General notation: a percent sign glued to a quantity symbol ("∆O2%", "wt%") is the column's unit, while a number with a percent sign ("95% interval") stays a value. Motivating source: ignition quantities-29. (3) General notation: the inch mark after a number (`"`, `″`, typeset `”`) is a length unit, except when it closes a quoted number. Motivating source: textiles quantities-10. (4) Document structure: a running page header, page number and caption lines before a whole sentence are cut off the statement and its support (`page_edge_prefix`, recorded as `page_edge_removed`) instead of holding it. Not cut when the rest starts in lowercase, closes a quotation it never opened, is only a caption, or the previous page (without its foot captions) ends mid-sentence. Motivating source: regulator statements-22 and -26; on the saved regulator package it cuts 6 whole sentences and keeps 9 continuations held. Effect on the others: (1) and (2) only for tables with those headers; (3) only units printed as inch marks; (4) only papers with a detected running header. Tests: `test_loose_units.py` (7), `test_page_edge_prefix.py` (4), positive, negative and metamorphic; pytest 862. Not changed, with reason: regulator relations-30/31/32 are already SOURCE_SUPPORTED in round B (`hasMaterial dodecane`). Ignition quantities-28 (ρ [kg/m³]) arrives with unmapped math-font glyphs in the row label, which is detected but not addressed (glyph recovery). Textiles statements-19 stays held: the slide never prints that its bullets are pass criteria, so a normative role would be inferred from knowledge of NASA-STD-6001, not from the source. | measure at point A |
| 3.4 | Precision by structure: Materials only mentioned (10 of 48 round B errors); counts read as groups ("Sixty test runs"); planned procedures read as executed groups or interventions; group restatements (addendum §6) | implemented-verified for materials and counts (replay at point A); restatements and planned procedures pending | `090f7c0`, from the round B adjudicated errors, no model calls. (1) Semantic with evidence: a current Material or Sample whose every support lies in a known section that is not the study's own research (introduction, background, a section such as "Contaminant Selection" or a cited cue), and that no SOURCE_SUPPORTED relation, quantity or statement uses, is held (`MATERIAL_ONLY_MENTIONED_OUTSIDE_OWN_RESEARCH`, never rejected). The study's own analysis counts as research, and a passage under no recognized section is not known to be outside it. Motivating sources: regulator and ignition. Simulated on the saved round B packages: 8 holds, all 8 on records the adjudication marks incorrect (Mobil DTE24, WD-40, Fomblin, Sebacate, SOP regulator S/N 102, Nomex, Kevlar, cellulosic materials), 0 correct records held; textiles and PTFE unchanged. Two narrower drafts were discarded because they held correct records (GN2, Algoflon®, silicone, Vespel). (2) A count-of-tests rule ("Sixty test runs" is not a group name) was added and then withdrawn at point A, because its only occurrence is the subject of a correct statement (regulator statements-17). (3) The 3.2 "prior to" rule, generalized: "prior to X" orders a procedure unless X is a study ("prior to this study"); "prior work" or "prior tests" still point at earlier research. Motivating case: regulator "Prior to initiation of impact sequence". Tests: `test_mentioned_only_materials.py` (4), `test_count_is_not_a_group.py` (2), `test_procedural_prior.py` (now 9); pytest 871. Not addressed, with reason: group restatements ("1-g testing" restating the WSTF group, 5 ignition errors) need semantic equivalence between differently named groups, which is a model decision, so they go to 2.1b/4 or review. Planned procedures typed as executed groups appear only in the Sonnet pilot outputs, not in round B, so they are measured in package 4. | measure at point A |
| 3.5 | Targeted recovery from tables and narrative for source-backed content the model omits (§9, addendum §8) | blocked: changes the model request, so it can only be measured live (with 2.1b in package 4) | Diagnosis from `target_miss_diagnosis.json`: only 13 target-run pairs (12 % of misses) were never proposed, and they vary from run to run. They are narrative values, not table cells: "Apollo (100% O2) and Skylab (70% O2)", "a minimum of 37% O2 at 8.2 psia", "The worst-case delta ... 2.3%", "20uL was injected", "~100 mg/ft2 film coating", and two relations. Table cells are already offered deterministically as review-only proposals (`pdf_table_quantities`), and 3.3 fixed their header units. Recovering a narrative value needs its subject and quantity name, which is an interpretation, so it must come from a targeted model call, not from a rule. No deterministic rule was added, because one would only fit these sentences. | design the targeted recovery call together with 2.1b; one live round in package 4, cost announced first |
| A | Measurement point A: 46-input replay, 29 negatives, PTFE ≥ 27/34, 0 critical (free) | implemented-verified | `point_a.md`: 50 inputs replayed with 0 model calls. 29 negatives: 0 critical regressions. PTFE 28/34, 134/136. Round B against its adjudication: textiles 7→8/29 (precision 0.773→0.826), regulator 10/32 (0.533→0.630), ignition 15→16/29 (0.748→0.759). 0 critical. The §13 gate is not met: recall ≥ 0.80 only on PTFE | 3.2b, then package 4 (needs authorization) |
| 3.2b | Statement scope when the proposed group subject is SOURCE_SUPPORTED but not applicable to the passage: fall back to the investigation scope, as a held group already does (asymmetry found at point A) | pending | `point_a.md` (8 regulator statements, including targets 22 and 24) | design, test, replay regulator and the negatives |
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

- Math-font glyphs in PDF table labels ("𝜌 ሾ𝑘𝑔/𝑚ଷሿ" for ρ [kg/m³]) are not recovered, so units in such row labels cannot bind (ignition Table 1). Not in block 3.

- `QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT` is the leading rejection; the model almost never fills `printed_name`. → 3.1
- Strategy phases and author claims typed as executed groups, interventions or documentary context (Sonnet textiles). → 3.4
- Regulator has never run on Sonnet. → 4
- Not measured live: the validation reuse (`24f09e3`) and the prefetch gain on long sources. → 4

## Pending verifications (only when Diego asks)

- The 29 historical negatives and the full 46-input replay with the duplicate change. → A
