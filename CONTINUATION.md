# Continuation checkpoint

Updated at the end of every work package. A new session reads `CLAUDE.md`, then this file, then the canonical record `artifacts/phase1_generalizable_ingestion/v6/milestone13/phase1_plan.md`.

- **Branch:** `diego/research` (never `main`).
- **Last package closed:** 4, live Sonnet rounds (`milestone13/package4/README.md`). Three rounds: one at `dc6f342` that exposed the 2.1b schema defect, and two at `a6d967b` with it fixed. Nine metrics per round regenerated.
- **Next package:** 6 (stability, leave-one-source-out, holdout). Before it, Liam and Diego should decide on 2.1b: the sentinel is never chosen live.
- **Open worktrees:** `../nasa-p21` (idle). Run the full pytest in the main checkout: the worktree lacks ignored local data (`artifacts/phase3c_*`, sqlite), and 36 tests fail there for that reason only.
- **Runs in progress:** none. Live run workspaces are in `../nasa-live/pkg4-dc6f342` and `../nasa-live/pkg4-a6d967b` (not in the repo).
- **Spend:** Anthropic pilot $3.68 plus package 4 $6.12 = $9.80 of the monthly $100; next monthly credit on 2026-11-02.
- **Waiting on:**
  - Liam: Sonnet as the primary model.
  - Diego: any further live round needs his authorization.
