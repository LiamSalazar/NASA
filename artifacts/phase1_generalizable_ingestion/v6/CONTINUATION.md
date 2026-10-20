# Continuing Phase 1 v6 on another machine

**State: `PHASE1_COMPLETE=NO`.** Branch `diego/research` (never `main`, no PR, no release zip until Phase 1 closes). Latest milestone receipts: `milestone8/`. Code after milestone 7:
- `e112fac`: values in a group's own subsection, named by their syntax.
- `6277466`: setpoint, nominal and target values read as settings.
- `d7c4732` (milestone 8): a group's subsection settings, method-section values and "tested at" lines as candidates, with metamorphic and negative tests.

Quality at `d7c4732`: `ruff format --check`, `ruff check` and `pytest` pass on a machine with the local files below (724 tests). Without them, `tests/test_curation_attribution.py` does not collect and 36 of the remaining 696 tests fail; the failing set is identical before and after this milestone.

Liam's generalization addendum (2026-10-20) governs every further change: classify each rule (general scientific/dimensional, document-structure, source-grounded semantic; never an exception for a known investigation), check it on the other development sources, add metamorphic and negative tests, keep replayed (A) and fresh (B) results apart, and report what the model proposed versus what printed-structure candidates added (`milestone8/rejection_audit_d7c4732.json`).

## Not in GitHub: copy or regenerate

| Path (relative to the repo unless noted) | Size (bytes) | sha256 | How to get it |
| --- | ---: | --- | --- |
| `.env` | 1,239 | (secret: never commit or print) | Create it from `.env.example`. It holds `NVIDIA_API_KEY`, which the live runs need; tests and offline replays do not. |
| `data/index/evidence.sqlite` | 365,543,424 | `d51b465619d58f4c3cd4f1e681d48158f959ed2a8b2aa22b7cf06bbcdccc4ee5` | Local application index. Copy it, or rebuild it with the repo's indexing scripts. Tests build their own temporary registries. |
| `data/index/scientific_context_v2.json` | 518,574 | `266b8ad58349b01733fe30b908a215811e799d6bc32995e46c739761430d5c8a` | Generated contextual index; copy it or regenerate it. |
| `artifacts/phase3c_real_context_evidence_v1.sqlite` | 365,543,424 | `b038f8ba09d48419b724f3bd516c6881f46d4c18a7d654a3391691b71e862977` | Phase 3c real-context evidence store; copy it. |
| `artifacts/phase3c_rc_baseline/correction_negative_cases.json` | 5,924 | `a61a35d744f14505c9d13d6384351ec8a082ddcee8bf7e1dfb75e236691154ff` | Copy it. |
| `../nasa-live/originals/20090043050.pdf` (outside the repo) | 6,225,257 | `c9de8948bdf14643e96f5666eba566827eb7842cbe6c085c6e411fe29cd8237a` | https://ntrs.nasa.gov/api/citations/20090043050/downloads/20090043050.pdf |
| `../nasa-live/originals/20170003941.pdf` | 1,765,263 | `c45b7435c9d5f29fcf644b6b570d16b31c6c6f61f93ae2bed79157d0fff19966` | https://ntrs.nasa.gov/api/citations/20170003941/downloads/20170003941.pdf |
| `../nasa-live/originals/20250002114.pdf` | 1,932,969 | `a7beb30e4beb5f5b993253161df7d2b9a286a1525bf97ab0d6bf94250a390474` | https://ntrs.nasa.gov/api/citations/20250002114/downloads/ICES_2025-392-correctedcaptions.pdf |
| `../nasa-live/originals/20260005493.pdf` | 1,679,775 | `9a810110b927990112f955a6f9c7babbc05230b0ec7edf1e911fb1901e6693b6` | https://ntrs.nasa.gov/api/citations/20260005493/downloads/301-ICES_2026-FR-Textiles_Final.pdf |

- Verify every downloaded PDF's sha256 before use; it must equal the v4 receipts and the table above.
- The holdout candidate NTRS 20170004702 (`holdout_registration/registration.json`) has **not** been acquired. Acquire it only after the development readiness gate (mandate §13) holds, with code frozen.
- `ClaudeDiego/`, the local zips and the live-run workspaces (temporary SQLite under the system temp folder) are never pushed and are not needed to continue.

## Start-up

1. Clone the repo and check out `diego/research`.
2. Run `uv sync`.
3. Set `PYTHONUTF8=1`. On Windows, without it tests fail on cp1252 decoding.
4. Keep `core.autocrlf=false` and LF endings: the co-developer works on Linux. Check `git ls-files --eol` before each commit.
5. Create `.env` with `NVIDIA_API_KEY` (for live runs only).
6. Put the originals in `../nasa-live/originals/`.
7. Run `uv run ruff check src tests` and `uv run pytest -q`.
8. Commits are authored as `Diegomed11 <diegomad473@gmail.com>`, with no assistant trailers. Push only to `diego/research`.

## Measuring

- **Live run:**

  ```
  uv run python scripts/phase1_exposed_live_run.py --pdf ../nasa-live/originals/<id>.pdf --provenance-from artifacts/phase1_generalizable_ingestion/v4/independent_<source>/submission.json --workspace <temp dir> --directory artifacts/phase1_generalizable_ingestion/v6/<milestone>/<source>_live_<commit> --timeout-seconds 3600
  ```

  `<source>` is `ptfe`, `ignition`, `regulator` or `textiles`.
- **Offline replay** (0 model calls):

  ```
  uv run python scripts/phase1_offline_replay.py <prepared.json.gz> --output <new dir>
  ```

- **`review_tools/`** holds the branch author's working scripts. Set `NFA_TMP` for their scratch root.
  - `replay_all.sh`: replays every reviewed run and exposed source.
  - `diff_all.py`: active-record changes between two replays.
  - `exposed_compare.py`: other sources and the 29 historical negatives.
  - `assertion_judgments.py` and `build_review_generic.py`: PTFE reviews.
  - `match_targets.py` and `list_active.py`: reviewing the other development sources against their frozen v4 targets.
  - `judgments_ptfe.json`: the accumulated PTFE record judgments.
- **Official scorer:** `scripts/score_scientific_review.py`, which reads plain JSON (decompress `prepared.json.gz` first).

## Next steps

1. More procedure quantities and relations from the paper's own syntax.
2. A slide-deck reader for textiles.
3. Record-by-record precision review on ignition and regulator.
4. New live runs on the four development investigations (a run started at `6277466` was interrupted and produced no receipts).
5. Readiness gate (§13).
6. Only then, the frozen-code prospective holdout on NTRS 20170004702 (§14 criteria unchanged).
