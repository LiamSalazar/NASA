# Phase 1 v6, milestone 6: material composition, staged from the source's own wording

**Status: `PHASE1_COMPLETE=NO`.** Nothing in this milestone is published to the ontology, the approved baseline or the graph.

This milestone implements the composition decision of 2026-10-20 (Liam's approval, relayed by Diego).

## What already existed, and what was missing

**The approved ontology** (`ontology/fire_safety.ttl`) and **SemanticRegistry** (`domain/semantic_registry.yaml`):
- `madeOf` relates a sample, run or experiment family to its material (endpoint contract in `validate_output`).
- No approved relation links a material to its constituents.
- No class distinguishes a formulation from a material.
- No property records a component's share or role.

**The model can only propose registered relations** (its schema enum is `semantic.relations`), so it cannot state a composition at all.

**Existing machinery that is reused** rather than duplicated:
- staged proposals with `activation: NONE` (`property_proposal`, `STAGED_FOR_ONTOLOGY_REVIEW`);
- the semantic staging table (`EvidenceRegistry.stage_semantic_candidate`, which can never write canonical records);
- validated entity records.

## What was implemented (`src/nasa_fire_ai/ingestion/composition.py`)

**A generic reader of composition wording.** It contains no rule for any material name. It recognizes:
- "the composition of X is 40% A and 60% B";
- "X is made up of / composed of / consists of …";
- "X uses A filler in B";
- "a formulation of B with A filler";
- a printed name "A-filled B";
- "the A component of X is made up of …" (nested);
- "the percentage of A in X is not known".

**One staged component assertion per constituent**, with:
- **the relation candidate** `hasComponent` (Material → Material);
- **the role**: the component's documented function (here `filler`). It is a characteristic of that one assertion, never a global `hasFiller` property, and it is set only when the word is in the source;
- **the proportion**: the value, `%`, and the basis (MASS, VOLUME or MOLAR) only when the source states it, otherwise `UNSPECIFIED_IN_SOURCE`. A documented unknown is kept as `NOT_KNOWN_PER_SOURCE`, and the listed components' sum is recorded, never used to infer anything;
- **the context**: the material in which a nested component is described ("the bronze of Salox-M®", not bronze in general);
- **the source descriptor**: the source's own words for the material ("metal filled PTFE compound"). No ontology class is asserted;
- **the evidence**: the literal sentences and pages.

**Distinctions kept:**
- The material (a validated `Material` entity) is the subject.
- A component that is not yet an entity is proposed as one (`STAGED_ENTITY_PROPOSAL`).
- Specimens and batches remain `Sample` entities related by `madeOf`.
- The role and the share belong to the component assertion.

**Subjects must be validated materials**, or a component of one. "The composition of the cabin air was 21% O2 …" is not taken as a material composition.

**The missing relation is proposed as vocabulary** (`ontology_extension_proposals`):
- domain, range and definition;
- the role, share and context characteristics;
- the approved relations it examined, and why `madeOf` does not fit;
- `activation: NONE`, `STAGED_FOR_ONTOLOGY_REVIEW`.

**Integration.** `validate_output` emits `composition_proposals` and `ontology_extension_proposals`, which the live run, the offline replay and curation re-validation all use. `CurationService.prepare_scientific` stages them in `semantic_staging` as `CANDIDATE_RELATION`, `PENDING`.

**Lifecycle:** `PROPOSED` → `SOURCE_SUPPORTED_PENDING_REVIEW` (what the code sets) → `VALIDATED` → `APPROVED`. The last two are a scientist's decision.

**Explanations** are rendered by `explain()` from each structured assertion, so a sentence cannot claim more than its record.

## PTFE result (`staged_composition_ptfe.json`)

The same seven assertions come out of all twelve reviewed PTFE runs, because they depend on the text, not on the model. The other four exposed sources produce none.

Rendered from the records:
- The source describes Salox-M® as a metal filled PTFE compound.
- Salox-M® contains Bronze as a component. Bronze acts as the filler of Salox-M®, in PTFE. The reported share of Bronze in Salox-M® is 40% on a basis the source does not state.
- Salox-M® contains PTFE as a component. The reported share of PTFE in Salox-M® is 60% on a basis the source does not state.
- Bronze (as used in Salox-M®) contains Copper, Tin and Zinc as components: 90%, 8% and 2%, basis not stated.
- Brass-filled PTFE contains Brass as a component. Brass acts as the filler of Brass-filled PTFE, in polytetrafluoroethylene. The source states that the share of Brass in Brass-filled PTFE is not known.
- Brass-filled PTFE contains PTFE as a component.

All seven are `SOURCE_SUPPORTED_PENDING_REVIEW`, and `hasComponent` is a staged proposal, not approved vocabulary.

Source sentences (NTRS 20090043050):
- **p10:** "a similar metal filled PTFE compound named Salox-M® uses Bronze filler in PTFE instead of Brass." "The composition of Salox-M® is 40% Bronze and 60% PTFE." "The Bronze component of Salox-M® is made up of 90% Copper, 8% Tin, and 2% Zinc." "the percentage of Brass in the Brass-filled PTFE is not known"
- **p2:** "a new formulation of polytetrafluoroethylene (PTFE) with Brass filler"

## Evaluation is unchanged

The scorer, the frozen targets and their finders are unchanged. Targets 18 and 33 look for quantity and relation records of the reviewed extraction. The composition now lives in staged component assertions, which the scorer does not read, so it does not credit them, and the recall figures of milestone 5 stand. Crediting them would require approving the vocabulary and representing the assertions as reviewed records: a scientist's decision, not an evaluator change.

Quality at `6734bd1`: `ruff format --check`, `ruff check`, `pytest` (702 tests, 7 for composition).
