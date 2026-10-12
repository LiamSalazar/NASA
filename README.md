# NASA FIRE AI — Phase 3C evidence assistant

NASA FIRE AI retrieves source-backed spacecraft fire-safety evidence. It preserves reported values, units, experimental identity, context and epistemic class. Scientists make new scientific inferences. Microgravity is a research and presentation preference; unspecified conditions never become mandatory filters.

## Architecture

`Phase3AssistantService` orchestrates the existing `QueryIntentV2` interpreter, SemanticRegistry and native RDF executor. V1 remains available with `NATIVE_V2_QUERY_ENABLED=false`. There is one scientific graph and one evidence registry. SQLite stores passages, source versions, FTS5, caches, locators and review receipts. RDF stores domain entities and relationships. Raw sources and historical canonical inputs are immutable.

V2 follows question → constraints → retrieval → requirement coverage → optional adaptive investigation → claim selection → support verification → eligible extractive answer. `services/investigation.py` rebuilds alternatives from current evidence and unresolved requirements after each action. Necessary topic checks are conservative guards, not independent semantic entailment judgments. Full semantic sufficiency and observation-to-conclusion attribution remain partially validated.

`services/scientific_synthesis.py` selects supplied statements and quantities; `services/claim_verification.py` checks source spans and applicability before emission. All V2 flag combinations use the final bundle. Conceptual and bibliographic responses use exact documentary span contracts. DIRECT satisfies explicit constraints; RELATED preserves useful alternatives with differences disclosed. Missing corpus evidence is never a NASA-identified research gap.

Nemotron proposes actions through `llm/research.py`. Tool, relation, entity and budget validation precedes execution; model proposals create no scientific facts. Jev remains optional advisory processing. FTS5 and graph retrieval work without credentials. Vector retrieval remains experimental and is not globally enabled. Scientific precision without independent labels is **NOT MEASURABLE**.

## Ordinary operation

```bash
uv sync --group dev
uv run python scripts/research.py ask "What did NASA observe about PMMA combustion?"
uv run python scripts/research.py ask "Which conditions applied to Saffire-I S1 and S2?" --json
uv run python scripts/research.py ask "Does acrylic mean PMMA?" --planner
uv run python scripts/research.py review "depressurization"
uv run python scripts/research.py status
uv run streamlit run app/streamlit_app.py
```

These commands have no Codex runtime dependency. Corpus questions require a populated registry. Reconstruction scripts include `fetch_seed_corpus.py`, `build_canonical.py`, `build_graph.py`, `build_index.py` and `ingest_psi.py`. Reconstruct audits in a separate workspace; do not rebuild over frozen historical inputs.

Existing `.env` loads with `override=False`; explicit process values win. NVIDIA uses `NVIDIA_BASE_URL`, `NVIDIA_MODEL` (or `NVIDIA_PHASE3_MODEL`) and `NVIDIA_API_KEY`. Jev uses `TYPESAFE_API_KEY`. Credentials stay local. Deterministic research, extraction proposals and extractive answers work without keys.

## Controlled maintenance and publication

```bash
uv run python scripts/maintain_knowledge.py discover --query "spacecraft fire suppression"
uv run python scripts/maintain_knowledge.py dry-run --nasa-id 20260003546
uv run python scripts/maintain_knowledge.py cycle --execute --offline --nasa-id 20260003546 --max-sources 1 --extract --max-model-calls 1 --receipt /tmp/nasa-maintenance-first.json
uv run python scripts/maintain_knowledge.py validation-only
uv run python scripts/maintain_knowledge.py review-pending
```

Repeat with a new receipt filename for idempotence. Unchanged source/span/model/contract keys reuse successful extraction receipts. Deterministic extraction stages exact source statements; `--extract` permits model assistance. Source count, model calls, retries and elapsed budget are bounded by `--max-sources`, `--max-model-calls`, `--retries` and `--timeout-seconds`. A lease prevents overlapping cycles. Per-cycle SQLite/reference/FTS checks and available maintenance regressions run. Budgets are checked between operations; in-flight provider calls have their own timeouts, so a cycle can exceed its nominal elapsed budget.

The automatic source contract atomically publishes verified public NASA document identity and original PDF pages. Publication tiers distinguish contract-eligible, provisional, review-required and rejected knowledge. Previously reviewed canonical statements can satisfy exact replay eligibility; this creates no new fact. Existing approved PSI and condition projection contracts remain operative. New experimental prose requires approved scope and epistemic extraction contracts; it remains in the existing review registry and noncanonical RDF projection. Model self-approval cannot grant authority. Observation/conclusion co-occurrence remains review-required.

`rollback --source-id <active-version>` archives an acquired version and restores its predecessor where available. Raw files and historical citations are retained.

## Flags and scheduling

V2 is opt-in through `NATIVE_V2_QUERY_ENABLED`. `SCIENTIFIC_CONTEXT_RESOLUTION_ENABLED`, `SOURCE_KNOWLEDGE_ENRICHMENT_ENABLED` and `ONTOLOGY_GRAPH_ENRICHMENT_ENABLED` control existing projections. `AUTONOMOUS_RESEARCH_ENABLED` enables additional retrieval; `NEMOTRON_RESEARCH_PLANNING_ENABLED` separately enables planning. The final V2 gate is mandatory even with `SCIENTIFIC_SYNTHESIS_ENABLED=false`. Configure investigation with `RESEARCH_MAX_ROUNDS`, `RESEARCH_MAX_ACTIONS`, `RESEARCH_MAX_CANDIDATES` and `RESEARCH_TIMEOUT_SECONDS`; these are operational limits, not scientific necessities.

The service/timer examples under `ops/` support bounded discovery, acquisition and staged extraction with one model call. They are **not installed**. Verify user, workspace, absolute `uv` path and an offline cycle first. For user-mode deployment, copy both examples to `~/.config/systemd/user/` without `.example`, remove `User=` from the service, run `systemctl --user daemon-reload`, then deliberately enable `nasa-knowledge-maintenance.timer` with `systemctl --user enable --now`. Inspect `journalctl --user -u nasa-knowledge-maintenance.service`. Persistent scheduling requires explicit operator authorization.

## Validation and audit export

```bash
uv run ruff format --check .
uv run ruff check .
uv run pytest -q
uv run python scripts/phase3c_closure.py freeze --directory artifacts/phase3c_closure_NEW
uv run python scripts/phase3c_closure.py evaluate --directory artifacts/phase3c_closure_NEW
uv run python scripts/phase3c_closure.py supplement --directory artifacts/phase3c_closure_NEW
uv run python scripts/phase3c_closure.py export --directory artifacts/phase3c_closure_NEW
```

Audit commands create exclusive versioned files, compare the frozen previous service in a separate interpreter, copy the runtime registry, execute real NASA requests, distinguish fresh inference from replay and check SHACL/integrity. The sanitized ZIP excludes credentials and private caches. Its manifest explicitly identifies tests reproducible alone and those requiring the verified corpus or credentials; corpus reproducibility is partial when data is excluded.

Historical metrics remain historical. See [PHASE3C_REASONING_CLOSURE_V1.md](docs/PHASE3C_REASONING_CLOSURE_V1.md) for the current campaign. V2 remains experimental, independent scientific relevance requires review, and Phase 4 has not begun.

## Scientific incorporation and review

The existing Streamlit app now includes **Incorporate research**: upload a text-backed research package, review grouped scientific clarifications and correction previews, inspect scoped relationships, and authorize an exact version. Publication activates immutable approved RDF through the existing KG, Evidence Registry, FTS and Phase3AssistantService. Original source files and prior approved versions are retained.

Development demonstrations require an isolated workspace; public publication stays disabled:

```bash
uv run python scripts/curate_research.py --workspace /tmp/nasa-curation-demo initialize
NASA_CURATION_DEVELOPMENT=true NASA_CURATION_WORKSPACE=/tmp/nasa-curation-demo NATIVE_V2_QUERY_ENABLED=true uv run streamlit run app/streamlit_app.py
```

See [PHASE3C_CURATION_V1.md](docs/PHASE3C_CURATION_V1.md) and `artifacts/phase3c_curation_v1/` for actual PSI-98/NTRS publication, correction, rollback, query and validation receipts. Compatible quantity additions and guided review work; general prose preparation, unrestricted natural-language correction and general ontology evolution remain partial. Test-principal approval is not NASA institutional authorization.
