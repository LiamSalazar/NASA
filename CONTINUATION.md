# Continuation checkpoint

Updated at the end of every work package. A new session reads `CLAUDE.md`, then this file, then the canonical record `artifacts/phase1_generalizable_ingestion/v6/milestone13/phase1_plan.md`.

- **Branch:** `diego/research` (never `main`).
- **Last package closed:** 4, live Sonnet rounds (`milestone13/package4/README.md`). Three rounds: one at `dc6f342` that exposed the 2.1b schema defect, and two at `a6d967b` with it fixed. Nine metrics per round regenerated.
- **Done after package 4:** the Sonnet miss diagnosis (`milestone13/package4/target_miss_diagnosis.md`), with no runs.
- **Next:** do not start package 6. The holdout stays untouched until the gate is met on the exposed sources, and today only PTFE meets it. Next comes the general fixes ranked in the diagnosis, each with its classification and tests, then a replay.
- **Open point for Liam:** 2.1b stays as it is (staging only); the model never chooses the sentinel.
- **Open worktrees:** `../nasa-p21` (idle). Run the full pytest in the main checkout: the worktree lacks ignored local data (`artifacts/phase3c_*`, sqlite), and 36 tests fail there for that reason only.
- **Runs in progress:** none. Live run workspaces are in `../nasa-live/pkg4-dc6f342` and `../nasa-live/pkg4-a6d967b` (not in the repo).
- **Spend:** Anthropic pilot $3.68 plus package 4 $6.12 = $9.80 of the monthly $100; next monthly credit on 2026-11-02.
- **Waiting on:**
  - Liam: Sonnet as the primary model.
  - Diego: any further live round needs his authorization.
