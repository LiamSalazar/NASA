# Pilot: Claude Sonnet 5.5 against NVIDIA 120b (outside evaluation B)

The pilot runs fresh live runs at code `0a88478`: `ee5082c` plus a per-run token ceiling and a cost receipt.
- **Model:** `claude-sonnet-5-5`, selected by `SCIENCE_PROVIDER=anthropic`, at effort `high`, with adaptive thinking, structured output and the server-side refusal fallback on.
- **Ceiling:** 500,000 tokens per run.
- **Scoring:** the same frozen v4 targets and the same record-by-record adjudication as evaluation B; carried judgments for identical records, new records judged one by one (`pilot_results.json`).
- **Baseline:** the evaluation B round at `b4be17d` (NVIDIA `nemotron-3.5-super-vl-120b`, old orchestration).

Per Diego, no new NVIDIA run was made. Opus 5.5 is planned for a later comparison. Every run is kept, and none was repeated to pick a better one.

## 1. Comparable results by model

| run | recall | precision | critical | calls | failed attempts |
|---|---|---|---|---|---|
| textiles, NVIDIA (round B) | 7/29 | 17/22 (0.77) | 0 | 5 | 1 deadline; 1 window answered by the 30b fallback |
| textiles, Sonnet, concurrency 3 | 9/29 | 16/19 (0.84) | 0 | 5 | 0 |
| textiles, Sonnet, concurrency 1 | 9/29 | 14/20 (0.70) | 0 | 5 | 0 |
| ignition, NVIDIA (round B) | 15/29 | 86/115 (0.75) | 0 | 16 | 0 |
| ignition, Sonnet, concurrency 3 | 14/29 | 68/83 (0.82) | 0 | 14 | 0 |

**Textiles:** both Sonnet runs recover the four printed test settings of the two specimens (48 % and 8.2 psia for the PBI coupons, 37 % and 8.2 psia for the patches). NVIDIA lost these in round B by typing the patches as a Material. The two Sonnet runs agree on recall; their precision differs because the second run typed three strategy phases as interventions. That is model variability, since the two runs are equal in everything else.

**Ignition:** Sonnet and NVIDIA end one target apart.
- Sonnet gains the tentative conclusion with its call for further research (statements-25).
- Sonnet misses the WSTF chamber pressure (quantities-06) and the authors' non-causal statement (statements-22).
- Sonnet's precision is higher (0.82 against 0.75).

The quality differences come from the model only: the orchestration changes give identical output by construction (section 4).

## 2. Real cost and duration

| run | total time | model | local | after extraction | input / output tokens | cache read / written | cost (list price) |
|---|---|---|---|---|---|---|---|
| textiles, NVIDIA (round B) | 331 s + 1,390 s after | 285 s | 46 s | 1,390 s | 31,390 / 11,052 | n/a | 0 |
| textiles, Sonnet c3 | 70 s | 51 s | 15 s | 3 s | 69,877 / 5,046 | 0 / 8,237 | $0.19 |
| textiles, Sonnet c1 | 64 s | 47 s | 14 s | 4 s | 69,808 / 4,959 | 1,530 / 6,711 | $0.19 |
| ignition, NVIDIA (round B) | 1,683 s + 77 s after | 500 s | 1,183 s | 77 s | 248,020 / 54,953 | n/a | 0 |
| ignition, Sonnet c3 | 280 s | 167 s | 95 s | 17 s | 308,475 / 22,286 | 6,120 / 18,122 | $0.84 |

- Pilot total, including the key check: **$1.22**.
- Seconds per Sonnet call (p50 / p90 / max): textiles 7 / 24 / 24, ignition 7 / 35 / 41. NVIDIA's ignition calls this round were 22 / 55 / 123.
- No Sonnet call failed or was repeated: `repeated_identical_requests` is 0 in every run.

## 3. Persistent scientific deficiencies (seen with both models)

- **Unprinted quantity names.** The model's label is not printed, and the validator rejects the value (`QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT`). Example: "the chamber was rotated at 20.4 RPM" is still missed. The model almost never fills `printed_name`: 0 to 2 proposals per run. A general rule for a configuration's own printed verb is drafted in the paused batch 2, without a replay yet.
- **Role and type errors** in accepted records:
  - planned strategy phases typed as executed groups or interventions;
  - author claims typed as documentary context;
  - method descriptions typed as observations;
  - materials only mentioned (cited, background, considered and not used) typed as materials of the study.
- **Duplicates.** An offline check of round B found identical active records with the same identity or overlapping supports: Nomex and Kevlar twice each, and the same 98 J impact energy three times in PTFE. These predate the orchestration changes.
- **Gate.** Ignition, regulator and textiles remain below recall 0.80. Most misses are proposals rejected by a rule (`../target_miss_diagnosis.md`).

## 4. Orchestration improvements implemented

These are general, and none changes a criterion, prompt, scorer, ontology or target.

- **Measurement** (`ae642ed`, `0a88478`). Each run's `summary.json` now has a `timing` block:
  - provider seconds, with overlapping calls counted once; local, setup and post-extraction seconds;
  - per call: time to first token, generation, input, output and cache tokens, estimated cost;
  - failures by cause and repeated identical requests.
- **Local recomputation** (`ae420ab`). Values derived from a document's own structure are computed once per document, and text normalization is cached.
  - Before: `validate_output` spent 508 of 538 s of a replay recomputing running headers (8,336 calls), page titles and sections for every record.
  - Local pipeline per source now: textiles 6 s, regulator 7 s, ignition 14 s, PTFE 42 s.
  - The full 46-input replay went from about 40 min to 4 min 18 s.
- **Window prefetch** (`3e746b1`). `SCIENCE_WINDOW_CONCURRENCY`, default 3.
  - Each stage's first requests are computed exactly as the sequential loop would compute them and sent ahead.
  - The sequential loop is unchanged and merges in window order. An answer is used only for a byte-identical request.
  - A rate limit stops sending ahead.
  - Simulated on round B's recorded calls, the saving is 0 to 5 min per run. It is small because textiles and regulator have one or two windows per stage, and the recovery calls depend on each other.
  - Live, Sonnet on textiles took 51 s at concurrency 3 and 47 s at concurrency 1 (no gain); ignition saved 11 s.
- **Prefix cache.** The stable stage instructions carry `cache_control`. They are read back only when a stage repeats within the cache lifetime, so reads were 0 to 6,120 tokens per run: no meaningful saving at this scale.
- **Proof:**
  - **Scientific equivalence:** the 46 saved inputs give a whole package identical to before after every change (46/46).
  - **Idempotence:** two passes over the same saved inputs give identical packages (4/4).
  - **Metamorphic:** concurrency 1 and 3 send the same requests and yield the same records.
  - **Tests:** a 429 stops prefetching; the token ceiling and cost receipt are tested. The full pytest passes.
- **Dependency graph** (unchanged).
  - identity (windows independent) → propositions (windows independent; known entities come from identity) → targeted quantity recovery (sequential, each round depends on the coverage left by the last) → relationships (windows independent) → subsection recovery and deferred retries (sequential).
  - Only the independent passes are prefetched.

## 5. Model recommendation

**Recommendation:** use `claude-sonnet-5-5` as the development model for the remaining Phase 1 batches; changing the primary model is Liam's decision.

- **Speed:** runs are 4 to 6 times faster.
- **Reliability:** no failed or repeated calls; the NVIDIA runs depended on deadlines, network errors and a 30b fallback.
- **Quality:** precision 0.82–0.84 on its first runs against 0.75–0.77 for NVIDIA; recall equal or better on textiles and one target behind on ignition.
- **Cost:** about $1 per run on ignition, so a round of the four sources is about $3–5. The rule-checking replays stay free.
- **Not established:** Sonnet does not fix the rejected-proposal deficiencies, and two runs per source are too few to state its variability. Opus 5.5 is to be compared on the same plan before choosing a final model.

**Attribution of the time saved:**
- **Textiles** (331 s to 66 s of extraction): the orchestration accounts for about 40 s (local 46 s to 15 s); the model accounts for about 235 s (model wait 285 s to 51 s).
- **Ignition** (1,683 s to 262 s): the orchestration accounts for about 1,100 s (local 1,183 s to 95 s, plus a small prefetch gain); the model accounts for about 330 s (model wait 500 s to 167 s).
- **Caveats:**
  - No NVIDIA run was made with the new orchestration, so the orchestration's share is estimated from the measured local times and the prefetch simulation, not from a fresh NVIDIA run.
  - The 1,390 s textiles spent after its NVIDIA extraction is not counted on either side. The same steps take 11 s when reproduced, so it was a stalled process, not a measurement of either model.

**Attribution of quality:** the model alone, since the orchestration changes are output-identical by construction.

## Opus 5.5 comparison (same plan, same code)

Each source was run once with `claude-opus-5-5`, at concurrency 3 and under the same 500,000-token ceiling, at `5ebec7b`; its source code is identical to `0a88478`. Scoring uses the same frozen targets and the same adjudication, and no run was repeated.

| run | recall | precision | critical | total time | model / local | input / output tokens | cost |
|---|---|---|---|---|---|---|---|
| textiles, Sonnet | 9/29 | 16/19 (0.84) | 0 | 70 s | 51 s / 15 s | 69,877 / 5,046 | $0.19 |
| textiles, Opus | 9/29 | 22/28 (0.79) | 0 | 140 s | 82 s / 54 s | 70,154 / 7,908 | $0.45 |
| ignition, Sonnet | 14/29 | 68/83 (0.82) | 0 | 280 s | 167 s / 95 s | 308,475 / 22,286 | $0.84 |
| ignition, Opus | 15/29 | 99/116 (0.85) | 0 | 484 s | 321 s / 141 s | 308,559 / 38,908 | $2.01 |

- **Textiles:** Opus finds the same 9 targets as Sonnet. It adds the PBI material and the upward flame propagation, but also three Apollo-era historical materials typed as materials of the study.
- **Ignition:** Opus adds the WSTF chamber pressure (quantities-06). It proposes more records (116 against 83), many of them cited-study entities correctly marked as cited, with higher precision.
- **Reliability:** neither model had a failed or repeated call.
- **Cost and time:** Opus's calls are about three times slower (p50 21 s against 7 s on ignition), and it costs 2.3 to 2.4 times as much.

**Decision rule, agreed before the runs:** Opus becomes the development model only if it gains 3 or more targets over the two sources without lower precision than Sonnet.
- Result: it gains 1 target (textiles 0, ignition +1), with lower precision on textiles and higher on ignition.
- **Sonnet 5.5 stays the development model.** Opus remains an option for a final confirmation run.

**Cost:** the Opus comparison cost $2.45; the whole pilot cost $3.68.
