# Continuation checkpoint

Updated at the end of every work package. A new session reads `CLAUDE.md`, then this file, then the canonical record `artifacts/phase1_generalizable_ingestion/v6/milestone13/phase1_plan.md`.

- **Branch:** `diego/research` (never `main`).
- **Last package closed:** 2.1b implemented offline (`PROPOSE_NEW_CLASS` / `PROPOSE_NEW_RELATION` in the request; staged with an approved parent).
- **Next package:** 3.5 offline design (a targeted recovery call for narrative values the model omitted), then package 4: one live Sonnet round on the four sources, only after Diego authorizes (estimate about $3–4 USD per round).
- **Open worktrees:** `../nasa-p21` (idle). Run the full pytest in the main checkout: the worktree lacks ignored local data (`artifacts/phase3c_*`, sqlite), and 36 tests fail there for that reason only.
- **Runs in progress:** none.
- **Spend:** Anthropic pilot $3.68 of the monthly $100; next monthly credit on 2026-11-02.
- **Waiting on:**
  - Liam: Sonnet as the primary model.
  - Diego: authorization before any live round (package 4).
