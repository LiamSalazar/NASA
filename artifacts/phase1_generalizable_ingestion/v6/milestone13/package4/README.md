# Package 4: live Sonnet rounds on the four development sources (evaluation B)

**Kind:** evaluation B, i.e. fresh live inference, not a replay. Every predetermined run is reported, and none was repeated to pick a better one.
- **Model:** `claude-sonnet-5-5` (`SCIENCE_PROVIDER=anthropic`), window concurrency 3.
- **Limits:** 500,000 tokens per run and 3,600 s per run.
- **Isolation:** each run had its own workspace, SQLite cache and receipt directory, so no run reused another run's cache.
- **Authorization:** Diego authorized two rounds at 14:36 UTC. After the defect below, he chose to fix the code and run two new rounds (15:10 UTC), and confirmed the launch himself at 15:26 UTC.
- **Spending cap:** 12 USD in total, with a stop if a round passed 6 USD.

## Three rounds, reported apart

| round | code | started (UTC) | cost | sources |
|---|---|---|---|---|
| 1 | `dc6f342` (frozen; carries the schema defect) | 14:59 | 1.66 USD | 4 |
| 2 | `a6d967b` (frozen; defect fixed) | 15:26 | 2.28 USD | 4 |
| 3 | `a6d967b` (same code as round 2) | 15:37 | 2.17 USD | 4 |

Total: **6.12 USD** (list price, from the per-call usage in each `summary.json`). Receipt directories are named `{source}_sonnet_{commit}_r{n}`. Rounds 2 and 3 are `a6d967b_r1` and `a6d967b_r2`.

### The defect found in round 1 (fixed in `a6d967b`)

1. **Invalid stage schema.** The 2.1b fields `proposed_class` and `proposed_relation` reference `ProposedTerm` inside Entity and Relation. `stage_schema`, and the focused variant of a stage request, kept only the top-level definitions.
   - Anthropic refused the first attempt of every identity window with HTTP 400 ("Reference to non-existent definition"): 14 refusals in the round (PTFE 6, ignition 4, regulator 2, textiles 2).
   - The retry went out without structured output, so no 2.1b proposal could be made.
2. **Refusals charged to the token brake.** Each refusal kept its full reservation against the token ceiling. Ignition reserved 436k tokens against 207k really used, and PTFE 478k against 212k.
   - The windows needing a context split, and the relationship windows, were then `DEFERRED_BUDGET` and never sent.
   - Ignition finished with no relationship call and 42 active records; the pilot had 83.

**Fix (`a6d967b`):**
- `referenced_definitions` closes `$defs` over nested references, and `focused_schema` is the extracted focused variant.
- A request refused before processing (`request_rejected`, no usage) releases its reservation. Any other failure keeps it.
- Tests: `tests/test_request_schema_references.py` (7). 4 of them fail on `dc6f342`.
- Full pytest: 891 passed, 0 failed.

## Results by round and source

**Recall** is strict against the frozen v4 targets.
- PTFE is scored by the official scorer (`scripts/score_scientific_review.py`, review built by `review_tools/build_review_generic.py`).
- The other sources use the branch author's target adjudication (`review/*_round*_targets.json`).

**Precision** is record by record over every active SOURCE_SUPPORTED record.
- An identical record (same content signature) carries its earlier judgment from milestones 11–13, the pilot and earlier package 4 runs. Signatures judged both ways are not carried.
- Every other record is judged against the printed source (`review/*_manual.json`).
- A manual judgment of a record id overrides a carried one when the run's context differs. The one case is a group merging both regulator wet series.

| source | round 1 (`dc6f342`) | round 2 (`a6d967b`) | round 3 (`a6d967b`) |
|---|---|---|---|
| PTFE recall | 25/34 | 28/34 | 28/34 |
| PTFE precision | 90/92 | 100/101 | 117/119 |
| ignition recall | 10/29 | 13/29 | 12/29 |
| ignition precision | 32/42 | 71/85 | 63/76 |
| regulator recall | 9/32 | 9/32 | 8/32 |
| regulator precision | 32/33 | 31/34 | 29/36 |
| textiles recall | 10/29 | 10/29 | 10/29 |
| textiles precision | 17/24 | 20/22 | 20/27 |
| critical | 0 | 0 | 0 |

| run | cost (USD) | wall (s) | failed attempts | reserved / used tokens |
|---|---|---|---|---|
| PTFE r1 / r2 / r3 | 0.52 / 0.72 / 0.74 | 165 / 175 / 360 | 6 refused / 0 / 1 network | 478k/212k · 283k/283k · 356k/284k |
| ignition r1 / r2 / r3 | 0.48 / 0.91 / 0.77 | 113 / 267 / 250 | 4 refused / 0 / 2 network | 436k/207k · 353k/353k · 436k/320k |
| regulator r1 / r2 / r3 | 0.48 / 0.46 / 0.48 | 109 / 87 / 115 | 2 refused / 0 / 0 | 369k/189k · 189k/189k · 192k/192k |
| textiles r1 / r2 / r3 | 0.19 / 0.20 / 0.19 | 62 / 67 / 52 | 2 refused / 0 / 0 | 148k/75k · 77k/77k · 77k/77k |

Per-round detail (incorrect records with reasons, timing): `review/{commit}_round{n}_results.json`.

### 2.1b new-term proposals

Rounds 2 and 3 offered the `PROPOSE_NEW_CLASS` and `PROPOSE_NEW_RELATION` sentinels in a valid schema. Round 1 offered them in a schema the provider refused.
- **Result:** in all 12 runs, **0** model responses used a sentinel and 0 filled `proposed_class` or `proposed_relation`. So 0 records became `PROPOSED_ONTOLOGY_EXTENSION` through 2.1b, and nothing was staged from it (`tools/proposals21b.py`).
- **Only staged extension:** a `hasComponent` relation in every PTFE run, which comes from the composition module, not from 2.1b.
- **Reading:** when the sentinel is optional and the instruction prefers a listed term, the model always picks a listed term on these sources. The misses that 2.1b was meant to reach stay missed:
  - textiles' historical and assessment values;
  - ignition's statements without an eligible subject.

## The nine §11 metrics per round

Built by `milestone13/tools/phase1_metrics.py --round`, whose point A output is byte-identical to before:
- inputs: the round's results, its per-target outcomes (`review/*_targets_round*.json`, point A rule for non-correct targets) and the PTFE scorer metrics;
- outputs: `phase1_metrics_{commit}_r{n}.json`.

| round | pooled recall | pooled precision | evidence retention | omissions | critical |
|---|---|---|---|---|---|
| 1 `dc6f342` | 54/124 = 0.435 [0.35, 0.52] | 171/191 = 0.90 [0.84, 0.93] | 80/124 = 0.65 [0.56, 0.72] | 31/124 = 0.25 [0.18, 0.33] | 0 |
| 2 `a6d967b` | 60/124 = 0.48 [0.40, 0.57] | 222/242 = 0.92 [0.88, 0.95] | 100/124 = 0.81 [0.73, 0.87] | 14/124 = 0.11 [0.07, 0.18] | 0 |
| 3 `a6d967b` | 58/124 = 0.47 [0.38, 0.56] | 229/258 = 0.89 [0.84, 0.92] | 87/124 = 0.70 [0.62, 0.78] | 16/124 = 0.13 [0.08, 0.20] | 0 |

Recall by category (round 2 / round 3):
- entities 19/22 / 19/22;
- quantities 17/46 / 18/46;
- statements 18/44 / 15/44;
- relations 6/12 / 6/12.

The per-source tables with every interval are in the JSON files.

## Causes of each variation

**Round 1 → round 2 (code change).** The schema fix restored structured identity output and released the brake.
- **PTFE +3 targets** (25 → 28): the split and deferred windows were sent.
- **Ignition +3 targets** (10 → 13): the discussion and conclusion windows were sent (statements-23, -25). The igniter OD and the GRC slow flow were also recovered, but those come from the model labelling them better this time (round 1 had a fragment label and a condition as its own subject), not from the fix.
- **Regulator:** unchanged at 9.
- **Textiles:** unchanged at 10, with only 5 windows and no splits.

**Round 2 → round 3 (same code: model and network).**
- **Ignition −1** (13 → 12).
  - Two identity calls failed on the network (38 s each). As non-refusals they kept their reservation, correctly.
  - The ceiling was then reached (436k reserved), so one propositions window was `DEFERRED_BUDGET`.
  - The discussion window that needed a split was not recovered, so statements-23 and -25 were lost.
  - quantities-05 was gained: in round 2 the habitat pressure was held on a condition-as-subject binding.
- **Regulator −1** (9 → 8).
  - The model omitted the post-wet functional observation (statements-22).
  - It merged the first and second dodecane wet series into one group, which costs precision on four records, none critical.
- **Textiles:** the same 10 targets. Precision fell from 20/22 to 20/27 because the model typed more slide bullets as documentary context or publication (fragment, footer, a planned certification).
- **PTFE:** the same 28 targets. Round 3 proposed more table rows (119 records against 101), with 2 errors.

**Against point A** (a replay of round B packages, evaluation A):
- ignition 16, regulator 11 and textiles 8 at point A, against 12–13, 8–9 and 10 here.
- The live rounds are separate inferences and must not be compared as gains or losses of the rules.
- Ignition's live recall is below its replay because of the brake (round 3) and the model's own omissions.

**Gate (§13):** not met. Only PTFE reaches recall ≥ 0.80 (0.82 in both rounds on `a6d967b`); 0 critical errors in every run.

## Reproduce

Run from the repo root, with the run directories under `../nasa-live/pkg4-{commit}/`.
- `tools/driver_{commit}.py`: the launcher.
- `tools/carry.py SOURCE PREPARED OUT`: carries earlier judgments.
- `tools/verdicts.py COMMIT SOURCE N`: writes a run's final verdicts.
- `tools/targets.py SOURCE N` (with `PKG_COMMIT`): per-target listing.
- `tools/score_ptfe.sh N`: the official PTFE scorer.
- `tools/results.py`, `tools/target_outcomes.py`, `tools/proposals21b.py`.

Receipts were scanned before commit: no `sk-ant-` or `nvapi-` and no account identifiers. The provider request ids printed in the 14 refusal messages of round 1 (`req_...`) are replaced by `req_[REDACTED]` in the committed copies only; the originals stay outside the repository. `organizationId` fields are NTRS publication metadata, and the e-mail addresses are the authors' as printed in the public sources.
