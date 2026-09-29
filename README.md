# NASA Fire Safety Evidence Assistant (Day-0 MVP)

An ontology-grounded, evidence-first exploration tool for a small NASA spacecraft fire-safety corpus. It is not an autonomous scientist: it does not infer mechanisms, equivalence, recommendations, or knowledge gaps.

## Run

```bash
uv sync --group dev
uv run python scripts/fetch_seed_corpus.py
uv run python scripts/build_canonical.py
uv run python scripts/build_graph.py
uv run python scripts/build_index.py
uv run pytest -q
uv run streamlit run app/streamlit_app.py
```

No API key is needed for graph/query filtering, FTS5 retrieval, tests, evaluation, or the UI. Add `OPENAI_API_KEY` to `.env` only to enable a future adapter-backed embedding/synthesis run. Copy `.env.example`; model names are environment-configurable.

## Safety contract

`QueryIntent` is Pydantic-validated and converted to SPARQL deterministically. The system labels matching experimental context as Direct, Related (with explicit matches/differences), or No Direct Evidence. The latter is never converted to an open question. Evidence IDs resolve to page-level SQLite passages. Scientific claims without evidence IDs are rejected.

## Current slice

The fetched corpus includes the requested NTRS documents, NASA PSI source records for BASS-II and Saffire-I, and the NASA-STD-6001 entry. The PSI pages fetched as application shells, so they support source-identity records only; no experimental run values or Saffire-I table rows are invented. See [DAY0_RESULTS.md](docs/DAY0_RESULTS.md).

PSI ingestion is now available via `uv run python scripts/ingest_psi.py`; the verified results are in [DAY1_PSI_RESULTS.md](docs/DAY1_PSI_RESULTS.md).
