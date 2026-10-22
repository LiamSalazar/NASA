# Continuation checkpoint

Updated at the end of every work package. A new session reads `CLAUDE.md`, then this file, then the canonical record `artifacts/phase1_generalizable_ingestion/v6/milestone13/phase1_plan.md`.

- **Branch:** `diego/research` (never `main`).
- **Last package closed:** 4, live Sonnet rounds (`milestone13/package4/README.md`). Three rounds: one at `dc6f342` that exposed the 2.1b schema defect, and two at `a6d967b` with it fixed. Nine metrics per round regenerated.
- **Done after package 4:** the Sonnet miss diagnosis (`milestone13/package4/target_miss_diagnosis.md`), with no runs.
- **Done:** block 3b (`milestone13/package4/fixes.md`), fixes 2, 3 (restricted to a label that is the verb), 5 (restricted to a provably unsent request) and 1, measured by replay. B8 example fixed (`8801aa2`).
- **Done after the independent review:**
  - the corrected miss diagnosis (`9af6a50`);
  - the feasibility table (`package4/feasibility/`);
  - the proposal for Liam (`package4/liam/`).
- **Prepared, not run:** the new propositions request (`fff5289`): the role card is on, and the admissible-subject menu is off because it failed the PTFE prejudgment.
- **Next:** two Sonnet rounds on the four sources (about 4.5 USD, 6 USD cap). They are waiting on two things:
  - the coordinator's Anthropic envelope change (Diego decided the request size at 17:18 UTC);
  - Diego's written authorization to run.
  Replay before the rounds; report every run, live apart from replay. Do not start package 6.
- **Open point for Liam:** 2.1b stays as it is (staging only); the model never chooses the sentinel.
- **Open worktrees:** `../nasa-p21` (idle). Run the full pytest in the main checkout: the worktree lacks ignored local data (`artifacts/phase3c_*`, sqlite), and 36 tests fail there for that reason only.
- **Runs in progress:** none. Live run workspaces are in `../nasa-live/pkg4-dc6f342` and `../nasa-live/pkg4-a6d967b` (not in the repo).
- **Spend:** Anthropic pilot $3.68 plus package 4 $6.12 = $9.80 of the monthly $100; next monthly credit on 2026-11-02.
- **Waiting on:**
  - Liam: Sonnet as the primary model.
  - Diego: any further live round needs his authorization.
