# Proposal for Liam: decisions the Phase 1 gate now depends on

Branch `diego/research`, after package 4 and block 3b (2026-10-22). Everything below is measured with 0 model calls unless stated otherwise.

**Evidence:**
- `../README.md`: three live rounds;
- `../target_miss_diagnosis.md`: corrected miss diagnosis;
- `../fixes.md`: block 3b, by replay;
- `../feasibility/feasibility.md`: every target's best state over all graded runs.

## Why these decisions matter now

The table below combines all graded live runs: NVIDIA milestones 10–13, the pilot and the package 4 Sonnet rounds. No single run reached the union.

| source | reached in some live run | with replay | if every rejection were fixed | if every model-side miss were fixed too | needs a schema or contract decision |
|---|---|---|---|---|---|
| ignition | 16/29 | 17 | 25 | 29 | 0 |
| regulator | 22/32 | 22 | 29 | 32 | 0 |
| textiles | 12/29 | 14 | 15 | 18 | 11 |

- **Textiles** cannot reach 0.80 (24/29) whatever the rules or the model do until (a), (c) and (d) are decided.
- **Ignition and regulator** have the room, but only by combining validator and request changes.

**Statistical note.** The gate asks for recall ≥ 0.80 in stable runs. With 29 targets, a source whose true recall is 0.80 passes two independent rounds only about 22 % of the time. Passing both with about 80 % confidence needs a true recall of about 0.88; with 32 targets, about 0.87.

## (a) Roles the schema lacks, and how staged records count

**Proposal:**
- A statement role for plans and goals, for example `planned_activity` and `stated_goal`. These would cover textiles statements-24 ("Certification testing will be performed ...") and -27 ("Goal to systematically mature ..."). Today they can only be mistyped as documentary context.
- A quantity role for criterion and target values, staged as `fs:TestCriterion` (acceptance limits such as burn length < 6") and `fs:DesignCriterion` (assessment targets such as "a minimum of 37% O2 at 8.2 psia"). These would cover textiles quantities-10, -16 and -17. Quantities now admit only reported, derived and configuration values.

**Question:** does a record that is correct but staged (an unapproved class, role or property) count as recovered for recall? `scorer_review.md` found that staged properties already count; the same answer for staged roles and classes would make (a) usable without publishing anything.

## (b) The test article named by its acronym (proposal only, not implemented)

The regulator prints one test article, "Primary Oxygen Regulator (POR) 2.0, s/n 003", and its text says "the POR" or "the regulator". The specimen applicability contract holds a statement about it unless the passage is on the article's own evidence page. Many regulator misses come from that hold.

**Proposal:** when a document defines exactly one specimen of its kind with an acronym in its label, a passage printing that acronym identifies it.

**Risk measured:** it would also attach "Impact times of 80–93 msec were measured ... prior to re-connecting the POR" (statements-19) to the POR. That is a false attribution, and a guard for "before connecting the test article" would be needed. We did not change the contract.

## (c) A documentary record for a target whose role does not exist

Several targets expect a role the schema lacks: a plan, a goal, a current-activity claim. The model's best answer is then `documentary_context`, which the adjudication has judged incorrect so far (textiles statements-23, -24, -26, -27).

**Question:** until (a) exists, does a `documentary_context` record with the exact sentence and the right study scope satisfy such a target, or is it a miss?

## (d) Three contracts the frozen targets contradict

| target | what the target expects | the contract that holds it |
|---|---|---|
| textiles statements-18 | a qualified state-of-the-art claim | it is printed on the Background slide, and background support is not the study's own research (3.2) |
| textiles statements-19 | a normative Test 1 pass criterion | the slide never prints that its bullets are pass criteria, so the role would come from knowing NASA-STD-6001, not from the source (3.3) |
| textiles quantities-05 to -07 | the proposed Artemis atmosphere and the contingency test concentration | no eligible experimental subject exists for a proposed environment (3.5); a staged class for it would be needed |

**Decision needed:** relax the contract, change the target, or accept these as known misses.

## (e) Target finders for ignition, regulator and textiles

PTFE is scored by the official scorer with record finders (`review_tools/build_review_generic.py`). The other three sources are scored by the branch author's target-by-target adjudication.

**Draft:** `finders_draft.json`, built by `make_finder_draft.py` only from each target's frozen quote, page and kind, never from a run's records.
- Entities match by label, statements by a printed fragment, quantities by a printed value on the page.
- 29 targets need your decision (ignition 9, regulator 6, textiles 14): a quote printing several values, or a relation whose endpoints the quote does not print.

Please review, correct and freeze them. We will not change the scorer or the targets.

## (f) Anthropic request size (a change being made, not a question)

Anthropic requests ran under the NVIDIA envelope (65,536 context tokens). Large windows were therefore split or deferred, and ignition r2 lost two propositions windows.
- Diego decided at 17:18 UTC to raise it within a low spend.
- It will be a separate Anthropic envelope that leaves NVIDIA's defaults untouched.
- The values come from the receipts of the nine Sonnet runs and will be recorded with the change.

## (g) Notice B8: a request example near a frozen quote

From `18b73d9` (2026-10-21) until `8801aa2`, the request carried the example "the chamber was rotated at 20 RPM". It nearly copies the frozen ignition quote "the chamber was rotated at 20.4 RPM" (quantities-14).
- Ignition runs from 2026-10-21 (the pilot and package 4) carry this caveat.
- quantities-14 was never recovered live from it: it was held in every package 4 run, and recovered only by a validator fix in replay.
- The example is now invented, and `tests/test_prompt_has_no_source_phrases.py` guards the prompt and schema text against any three-word phrase of a frozen quote.

## (h) Pending items

- **`hasComponent`:** a relation staged in every PTFE run by the composition module. It needs your review as an ontology extension.
- **"was set to":** the 3.1 setting-verb rule deliberately excludes it. Should it name a value as other setting verbs do?
- **Sonnet as the primary model:** `claude-sonnet-5-5` is the development model; NVIDIA stays the default provider until you decide.
- **2.1b (new-term proposals):** in 12 live Sonnet runs the model never used the `PROPOSE_NEW_CLASS` or `PROPOSE_NEW_RELATION` sentinels, even with a valid schema in 8 of them. It is inert: staging only, never approved, no effect when unused. Keep it inert, redesign how the request offers it, or remove it.
