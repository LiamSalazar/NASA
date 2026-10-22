# Continuation checkpoint

Updated at the end of every work package. A new session reads `CLAUDE.md`, then this file, then the canonical record `artifacts/phase1_generalizable_ingestion/v6/milestone13/phase1_plan.md`.

- **Branch:** `diego/research` (never `main`).
- **Last package closed:** 5, the main report with the nine §11 metrics and intervals (evaluation A, point A).
- **Next package:** package 4, one live Sonnet round on the four sources with 2.1b. **Blocked until Diego authorizes** (the coordinator recommended one round now, about $3–4 USD, and the second when the code is frozen for the gate). After it, rerun `milestone13/tools/phase1_metrics.py` with the new adjudication.
- **Open worktrees:** `../nasa-p21` (idle). Run the full pytest in the main checkout: the worktree lacks ignored local data (`artifacts/phase3c_*`, sqlite), and 36 tests fail there for that reason only.
- **Runs in progress:** none.
- **Spend:** Anthropic pilot $3.68 of the monthly $100; next monthly credit on 2026-11-02.
- **Waiting on:**
  - Liam: Sonnet as the primary model.
  - Diego: authorization before any live round (package 4).
