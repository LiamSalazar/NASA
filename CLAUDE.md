# NASA FIRE AI: instructions for development agents

Read this file, then `AGENTS.md` (immutable rules, which prevail), before changing anything. Then open the canonical record `artifacts/phase1_generalizable_ingestion/v6/milestone13/phase1_plan.md` and `CONTINUATION.md`, and continue at the first work package not done. Do not replan what is already decided.

## What NASA FIRE AI is

An end-to-end platform that turns official NASA research on microgravity combustion, flame behaviour, fire safety, materials, experimental conditions, suppression and *Flame in Freefall* into versioned, evidence-grounded scientific knowledge, and lets scientists consult it. It is not a generic document chatbot.

**Sources.** Only official NASA material and collaborations with verifiable NASA participation in this domain, with relevant terrestrial comparisons. The catalogue cutoff is October 2026.

**Two subsystems:**
- **Knowledge creation:** acquire and preserve originals; understand document structure; interpret experiments, measurements, observations and conclusions; reuse the ontology; stage justified extensions; validate independently; ask the scientist only when necessary.
- **Knowledge consultation:** natural-language questions over the KG and the original documents, DIRECT versus RELATED evidence, comparisons that keep conditions apart, historical and refuted status, and the original source always reachable.

## Six phases

Phases are functional milestones, not rigid walls.
1. **Generalizable scientific ingestion (current priority).** Heterogeneous NASA sources become isolated, evidence-anchored curation packages, with entities, relations, quantities, scope, uncertainty and staged semantic extensions.
2. **Autonomous curation and ontology evolution.** Reuse, compatible extension, minimal closed-form scientist questions, previews and corrections, and local confirmation.
3. **Workspaces, history and versioning.** Git-like baseline plus isolated deltas, attribution, rollback, and promotion by authorized developers only.
4. **NASA scientific library.** An inventoried 2026 corpus, processed incrementally with coverage denominators. Unexposed sources are reserved for evaluation.
5. **Research and consultation.** Evidence-grounded answers, comparison, dashboards, and the original viewer. System analysis is never presented as a NASA finding.
6. **Integrated product release.** Security, recovery, performance and an end-to-end demonstration, independent of NASA institutional infrastructure.

**Boundary between phases 1 and 2.** Phase 1 autonomously discovers, interprets, maps, validates and *stages* knowledge and the semantic extensions it needs. Phase 2 provides the scientist-facing clarification, correction and approval. Phase 1 must not stop at a concept Phase 2 will later review, and its outputs must not need remodelling for Phase 2.

## Strict science, adaptive knowledge

- **Immutable integrity contracts.** Never weaken these to raise recall: source identity, original bytes and expressions, experiment identity and applicability, values, units and qualifiers, epistemic roles, attribution, uncertainty, historical status, authorization, transactional integrity and version compatibility.
- **Adaptive semantic contracts:** classes, properties, quantities, relations, composition, configurations and new concepts. The approved ontology is the foundation, not a closed vocabulary.
  - Reuse what is equivalent (case A).
  - Propose a minimal compatible addition when knowledge is partly represented (case B).
  - Stage a validated extension proposal for genuinely new knowledge (case C).
  - Preserve real ambiguity and ask one precise scientific question (case D).
  - Never discard a source-supported concept only because the registry lacks it.
  - Never auto-publish an extension into the approved baseline.
- **Five states, never interchangeable:** structurally well formed, source-supported, proposed ontology extension, scientifically reviewed, authorized published change.

## Limits of the LLM

The LLM may interpret language, compare concepts, construct candidate relations, propose extensions, recover context, flag uncertainty and draft questions.

It may not:
- invent NASA findings, values or conditions;
- turn hypotheses into observations, or calculations into measurements;
- invent causality, or change the scope of a conclusion;
- erase superseded knowledge, or treat model confidence as truth.

Every statement stays traceable to NASA evidence.

**The scientist** decides genuine scientific ambiguity and authorizes versions. Do not ask them about routine extraction, parsing or RDF/SHACL.

## No overfitting

Metrics measure implementation quality; they are not the objective. The targets are precision ≥ 0.95, fully correct recall ≥ 0.80, and 0 known critical false attributions in the adjudicated set.
- **Forbidden:**
  - paper-specific mappings, identifiers or answer dictionaries;
  - vocabulary tuned to one source;
  - validators that recognize benchmark values;
  - scorer or frozen-target changes.
- **Every new rule** is classified as general science, document structure or semantic with evidence. Record the source that motivated it and its effect on the other development sources, and add metamorphic and negative tests.
- **Development sources** (PTFE, LUCI, ignition, regulator, textiles) are regression material, not evidence of generalization.
- **Reporting:** distinguish revalidated saved outputs (replay) from fresh inference (live runs), report every predetermined run, and never pick the best generation.
- **Phase 1 closes** only on frozen, independent, heterogeneous evaluation (`docs/PHASE1_MASTER_DIRECTIVE.md` §19).

## How to work

- **Inspect before implementing.** Read the real code, contracts, tests and commits; reuse and repair at the real boundary. Do not duplicate parsers, registries, extraction engines, graph stores or orchestration.
- **Development assistants are not runtime dependencies.** NASA FIRE AI calls its own configured scientific providers.
  - NVIDIA is the default provider and stays available.
  - `SCIENCE_PROVIDER=anthropic` with `claude-sonnet-5-5` is the development model chosen by the October 2026 pilot.
  - Do not change the production model or provider without authorization.
- **Runs cost time and credits.** Do not launch live runs unless they are truly necessary and authorized. Prefer pytest, unit, metamorphic and negative tests, and quick replays of saved outputs. Full replays and live rounds happen only at agreed measurement points.
  - The per-run `--max-total-tokens` ceiling is a spending brake: a call that would pass it is not sent and is recorded as deferred. It never truncates scientific content inside a request.
  - **No more live runs until the replay meets the threshold** (Diego, 2026-10-22): recall ≥ 0.80 and precision ≥ 0.95 per source, with 0 critical errors. Until then everything is measured by replay and tests. A live run is proposed only once the replay passes, and always needs Diego's written authorization.
- **Branch and commits.** Work only on `diego/research`; never `main`, no PR without request.
  - Commits as Diegomed11, with no assistant trailers.
  - LF endings, no Windows-only fixes.
  - Secrets only in `.env`, never printed or committed (receipts are scanned for `nvapi-` and `sk-ant-`). `ClaudeDiego/` is never committed.
  - Never modify the evaluator, frozen targets, global ontology baseline or source PDFs.
- **Work in small packages.** One logical commit each, tests and ruff green, pushed, and the canonical record plus `CONTINUATION.md` updated. A cut session then loses at most one package.

## Authoritative documents

- `AGENTS.md`: immutable repository rules.
- `docs/PHASE1_MASTER_DIRECTIVE.md`: Phase 1 master directive and its addendum (October 2026).
- `docs/NASA_FIRE_AI_MASTER_PLAN_2026-10-14.pdf`: six-phase master plan. Its commits, models and status are historical; verify the real HEAD.
- `docs/architecture.md` and `docs/PHASE1_GENERALIZABLE_SCIENTIFIC_INGESTION.md`: architecture and the Phase 1 report.
- `artifacts/phase1_generalizable_ingestion/v6/milestone13/phase1_plan.md`: **the single canonical record** of requirements, state, evidence and next action.
- `CONTINUATION.md`: where the last session stopped.
