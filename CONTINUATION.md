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
- **Done:** package 5 (`milestone13/package5/README.md`), two live Sonnet rounds at `07709c0`, 4.23 USD.
  - Pooled recall 0.51 and 0.57, precision 0.925 and 0.938, 0 critical.
  - The gate is still not met: only PTFE reaches recall ≥ 0.80.
- **Done after package 5** (no runs): the heading outline letter (`65acb94`); the Anthropic size hardening (`effcb21`); the spending brake with requests sent ahead (`824af5f`, `4ba8a23`, `10692ba`, `package4/fixes.md`): concurrency 3 now decides as concurrency 1 under a brake that fits the run. pytest 954.
- **Handoff for a new agent:** `HANDOFF_CODEX.md` summarizes everything since 2026-10-18.
- **Next:** wait for the coordinator and Diego. Candidates:
  - Liam's decisions (`package4/liam/`);
  - the role-dependent subject menu.
  No live runs without Diego's written authorization, and do not start package 6.
- **Open point for Liam:** 2.1b stays as it is (staging only); the model never chooses the sentinel.
- **Open worktrees:** `../nasa-p21` (idle). Run the full pytest in the main checkout: the worktree lacks ignored local data (`artifacts/phase3c_*`, sqlite), and 36 tests fail there for that reason only.
- **Runs in progress:** none. Live run workspaces are in `../nasa-live/pkg4-dc6f342` and `../nasa-live/pkg4-a6d967b` (not in the repo).
- **Spend:** Anthropic pilot $3.68 + package 4 $6.12 + package 5 $4.23 = $14.03 of the monthly $100; next monthly credit on 2026-11-02.
- **Waiting on:**
  - Liam: Sonnet as the primary model.
  - Diego: any further live round needs his authorization.
