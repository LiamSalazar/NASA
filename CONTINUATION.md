# Continuation checkpoint

Updated at the end of every work package. A new session reads `CLAUDE.md`, then this file, then the canonical record `artifacts/phase1_generalizable_ingestion/v6/milestone13/phase1_plan.md`.

- **Branch:** `diego/research` (never `main`).
- **Last package closed:** 3.4; 3.5 recorded as blocked (needs a model request change, measured with 2.1b in package 4).
- **Next package:** measurement point A: free offline replay of the 46 saved inputs and the 29 historical negatives at the current HEAD, PTFE scored officially (≥ 27/34, 0 critical), the other sources compared with the round B adjudication.
- **Open worktrees:** `../nasa-p21` (idle). Run the full pytest in the main checkout: the worktree lacks ignored local data (`artifacts/phase3c_*`, sqlite), and 36 tests fail there for that reason only.
- **Runs in progress:** none.
- **Spend:** Anthropic pilot $3.68 of the monthly $100; next monthly credit on 2026-11-02.
- **Waiting on:**
  - Liam: Sonnet as the primary model.
  - Diego: authorization before any live round (package 4).
