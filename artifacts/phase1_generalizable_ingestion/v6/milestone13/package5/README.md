# Package 5: two live Sonnet rounds with the new request (evaluation B)

**Kind:** fresh live inference with `claude-sonnet-5-5`, on frozen `07709c0`. It is reported apart from every replay, both rounds are reported, and neither is selected.
- **Authorization:** Diego, in his own words: "corre las dos rondas", 18:12 UTC. The coordinator had reviewed the commit first.
- **Code since package 4** (`a6d967b`):
  - block 3b fixes 1, 2, 3 and 5;
  - the B8 example;
  - the statement role card (on); the admissible-subject menu stays off;
  - the Anthropic request-size limit (96,000) and `max_tokens` floor (32,768);
  - discarded prefetches recorded.
- **Limits:** 500,000 tokens per run, 3,600 s per run, 6 USD in total for both rounds. Each run had its own workspace and cache.
- **Receipts:** `{source}_sonnet_07709c0_r{1,2}/`; `review/` holds judgments, verdicts, results, targets, the PTFE scorer and status.

## Results (live)

**Method:**
- **Recall** is strict against the frozen v4 targets. PTFE uses the official scorer; the other sources use the branch author's target adjudication.
- **Precision** is record by record: judgments are carried for identical records, and new ones are judged against the printed source (`review/07709c0_*_manual.json`).

| source | round 1 recall | round 1 precision | round 2 recall | round 2 precision | critical |
|---|---|---|---|---|---|
| PTFE | 28/34 (0.82) | 121/122 | 28/34 (0.82) | 109/111 | 0 |
| ignition | 9/29 (0.31) | 75/90 | **16/29 (0.55)** | 84/95 | 0 |
| regulator | **15/32 (0.47)** | 31/34 | **15/32 (0.47)** | 29/31 | 0 |
| textiles | 11/29 (0.38) | 18/19 | 12/29 (0.41) | 20/21 | 0 |
| pooled recall | 63/124 = 0.51 [0.42, 0.59] | | 71/124 = 0.57 [0.49, 0.66] | | |
| pooled precision | | 0.925 [0.89, 0.95] | | 0.938 [0.90, 0.96] | |

| run | cost (USD) | wall (s) | calls | failed | context splits | deferred by the brake | brake counter peak |
|---|---|---|---|---|---|---|---|
| PTFE r1 / r2 | 0.66 / 0.66 | 98 / 119 | 11 / 11 | 0 / 0 | 0 / 0 | 0 / 0 | 257k / 257k |
| ignition r1 / r2 | 0.76 / 0.86 | 122 / 150 | 11 / 12 | 0 / 0 | 0 / 0 | 0 / 0 | 309k / 346k |
| regulator r1 / r2 | 0.48 / 0.44 | 57 / 70 | 6 / 5 | 0 / 0 | 0 / 0 | 0 / 0 | 221k / 186k |
| textiles r1 / r2 | 0.20 / 0.17 | 56 / 47 | 5 / 4 | 0 / 0 | 0 / 0 | 0 / 0 | 78k / 78k |

**Total: 4.23 USD** (round 1 2.10, round 2 2.13).

The nine §11 metrics per round are in `phase1_metrics_07709c0_r{1,2}.json`. Recall by category:
- round 1: entities 0.91, quantities 0.37, statements 0.45, relations 0.50;
- round 2: entities 0.95, quantities 0.48, statements 0.50, relations 0.50.

## What changed in the requests that used to be split

Under `a6d967b`, eight windows per round needed a context split: PTFE 1–2, ignition 2–3, regulator 2. Some splits were not recovered, and ignition r2 deferred a window under the brake.

Under `07709c0` the same windows, estimated at 71k–78k tokens, went whole under the 96,000 limit:
- 0 splits and 0 deferrals in all 8 runs;
- calls per run fell (PTFE 13–14 → 11, ignition 14–15 → 11–12, regulator 7 → 5–6);
- the brake counter peaked at 346k of 500k;
- the other requests are byte-identical in construction.

**No request was paid twice.** Every top-level propositions window of the 8 runs ended `COMPLETE` or `COMPLETE_WITH_REJECTIONS`. None ended `RECOVERED_BY_SPLIT`, `SPLIT_TRUNCATED_TASK`, `EMPTY_WITH_SOURCE_CANDIDATES` or `PARTIAL_*`, so no whole request was paid and then its halves (0 of 12 windows).

**Hardening after the review:**
- `ANTHROPIC_SCIENCE_REQUEST_CONTEXT_TOKENS` is refused outside 4,096–131,072.
- The frozen-configuration check of `run_phase1_scientific_validation.py` also covers, for Anthropic only, the request limit and the `max_tokens` floor. NVIDIA's dictionary is unchanged.
- The live launcher uses a 500,000-token brake for Anthropic when none is given.
- `tests/test_request_context_limit.py` no longer depends on the environment, and includes the negative case: an Anthropic request over the limit is still split.

## Causes of the variation

**Between the rounds (same code, so the model):**
- **Ignition, 9 → 16.** In round 1 the model proposed the GRC group with the outline letter of its heading, "B. NASA Glenn Research Center (GRC) Partial Gravity Testing". Validation rejected it (`ENTITY_LABEL_ABSENT_FROM_SUPPORT`).
  - The GRC chamber values were then put on the whole investigation and judged incorrect.
  - entities-02, quantities-11, -12, -15 and relations-27 were lost.
  - In round 2 the group came without the letter, and those targets, plus quantities-14 (the setting-verb fix, live for the first time), were reached.
- **Regulator.** 15 in both rounds, with a different statement each time (statements-17 in round 2, relations-32 in round 1).
- **Textiles, 11 → 12.** statements-26 was typed an author conclusion in round 2.

**Against package 4** (`a6d967b`: ignition 13/12, regulator 9/8, textiles 10/10, PTFE 28/28):
- **Regulator** gains about 6 targets: the printed test series from captions (fix 1) and their impact times, now live.
- **Ignition** round 2 gains its first live statements-20, typed `open_question` under the role card, and quantities-14.
- **Textiles** gains statements-22 (the footer, fix 2).
- **PTFE:** unchanged.
- Without a control round we cannot split the gain between the fixes, the role card and the request size.

**2.1b:** 0 sentinels in all 8 runs again.

## Detected, not addressed

An entity label that carries its heading's outline letter ("B. NASA Glenn …") is rejected although the heading prints it. That is a document-structure candidate (a heading's own outline marker is not part of its name), motivated by ignition round 1.

## Gate

**Not met.**
- PTFE recall is 0.82 in both rounds, with precision 0.98–0.99.
- Ignition is at 0.31–0.55, regulator at 0.47, textiles at 0.38–0.41.
- 0 critical errors in every run.

Receipts were scanned before commit: no `sk-ant-`, `nvapi-`, `req_` or account identifiers, and all text is LF.
