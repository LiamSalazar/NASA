# Live exposed-regression run: PTFE (NTRS 20090043050)

**Status: development/regression only.** The source has been
`EXPOSED_DEVELOPMENT_REGRESSION_ONLY` since the v4 cycle-7 failure, so this is not
an independent evaluation. `PHASE1_COMPLETE=NO` is unchanged.

## Run

- **Command:** `scripts/phase1_exposed_live_run.py` at `2b7d1d6` (src clean).
  - It calls the ordinary `CurationService.submit/save` with the hash-verified
    official PDF (`c9de8948…`) and the v4 acquisition provenance.
  - It then calls `prepare_scientific` with the model enabled.
- **Models:** `nvidia/nemotron-3.5-super-vl-120b-a12b`, with fallback
  `nvidia/nemotron-3-super-120b-a12b`.
- **Budget:** 1800 s deadline, the same as v4.
- **Usage:** 19 model calls in 1066 s. The run completed inside its deadline;
  the v4 primary run stopped at the 1800 s deadline after 14 attempts.
- **Tokens:** provider-reported usage is 238,317 total tokens (177,059 prompt,
  61,258 completion, 29,157 of them reasoning) over the 15 attempts that report
  usage; 4 attempts report none. The 441,017 in `summary.json.gz` is
  `tokens_consumed_or_reserved`, a budget-accounting figure.
- **Integrity:** no source integrity errors, SQLite `ok`, 0 approvals,
  0 publications. Validation errors are review requirements only.
- **Files:** `prepared.json.gz`, `attempts.json.gz`, `validation.json.gz`,
  `summary.json.gz`, `submission.json`. No credentials are present.

## Equal-standard comparison with v4

`review/` holds a two-lens adversarial adjudication of the frozen 36-target
reference.

- **Adjudication:** one adjudicator per 4 targets, a protocol-accounting
  verifier, a scientific-fidelity verifier, and a judge when they disagree.
- **Precision judging:** every SOURCE_SUPPORTED non-duplicate proposal is
  judged by a judge and a skeptic.
- **Scoring:** `scripts/score_scientific_review.py`.
- **Equal standard:** the same protocol was applied to v4 `prepared_2` (the
  `v4_equal_standard_*` files).
- **Not gold:** these are assistant adjudications against the original text,
  not expert gold.
- **Judge consistency:** on the 10 accepted proposals present in both runs, the
  two reviews agreed on 9. The one difference is a non-critical role call on the
  page-18 opening conclusion.
- **Hand check of a review defect:** the reviewers saw a compact proposal view
  that cut proposal text at 400 characters, kept only 3 support spans and cut
  quotes at 300 characters. Source pages were complete. A hand check on the
  full records found:
  - no target outcome changes in either run, because no qualifying proposal was
    hidden;
  - no precision verdict changes;
  - only the written reasons of `proposal-4d624b1e` and `proposal-ef1c4448`
    relied on the excerpt. They were rewritten from the full record
    (`review_corrections` in `review/source_review.json`), and both remain
    incorrect and critical.

### Results

Denominators: 36 frozen targets, of which 2 photo-only targets are excluded as
inaccessible, so recall and retention use 34. Precision is over every accepted
(SOURCE_SUPPORTED, non-duplicate) proposal.

| Review | Correct | Unresolved | Omitted | Semantic recall | Retention | Reviewed precision | Critical in sample |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| v4, original v4 review | 7 | 15 | 12 | 7/34 (0.21) | 22/34 (0.65) | 28/29 | 0 |
| v4, this protocol | 8 | 15 | 11 | 8/34 (0.24) | 23/34 (0.68) | 20/29 (0.69) | 4 |
| live, this protocol | 10 | 15 | 9 | 10/34 (0.29) | 25/34 (0.74) | 25/32 (0.78) | 5 |

- **Same-protocol comparison (rows 2 and 3):** +2 correct targets, +2 retained
  targets, +1 critical error.
- **By kind, live versus v4 under this protocol:**
  - entities 7 vs 6 correct;
  - statements 3 vs 2 correct;
  - quantities 0 vs 0 correct (5 unresolved, 5 omitted in both);
  - relations 0 vs 0 correct, 1 vs 0 unresolved.
- **Critical errors:**
  - live: three cited-only comparator materials labelled `current` (Viton A,
    Viton A-500, Fluorel) and two copies of one table span (findings 3 and 4);
  - v4 under this protocol: four materials with the same lineage error.
- **Verdict:** the frozen minima (recall 0.50, retention 0.75) are still not
  met, at 0.29 and 0.74. PTFE scientific acceptance: **FAIL**.

**Attribution.** The numeric grammar changed only quantity handling, and
quantity target outcomes are identical in both runs (5 unresolved, 5 omitted).
The target changes come from model nondeterminism and from the run completing
within its deadline, not from this branch's code:

- `entities-07` and `entities-08` (Batch #1 and #2 identities) went from
  omitted to correct.
- `statements-19` went from unresolved to correct.
- `relations-34` went from omitted to unresolved.
- `entities-02` went from correct to omitted.

## Findings for M1/M2

1. **Quantities.** Nemotron proposed 179 quantities and all were rejected.
   - None was rejected by the numeric grammar.
   - An offline replay of the same raw output at `4a2f99d`, with column-header
     unit binding (`offline_replay_4a2f99d/`), leaves these first reasons:
     - `QUANTITY_SUBJECT_NOT_IN_APPLICABLE_SOURCE`: 77
     - `QUANTITY_LOCAL_SUBJECT_BINDING_UNRESOLVED`: 72 (Table 3/5/6 rows, such
       as `72 ft-lbs (98J)` and `0/20`, without a resolved row/batch subject)
     - `QUANTITY_UNIT_NOT_BOUND_TO_EXPRESSION`: 30, all in continuation tables
       (see 2)
   - Scope and row-group attribution are the binding constraint.
2. **Continuation tables (defect 1 family).** On pages 13, 16 (first table) and
   17, the detected table takes its **first data row as the header**. Page 13's
   header is `72 ft-lbs (98J) | LOX/-297°F | 10,000 | 0.06206 | 0/20`. That data
   row is lost as values, and the cells below have no column header to inherit
   units or variable names from. Continuations need the header of the table they
   continue: Table 3 on page 12, Table 5/6 on pages 15–16.
3. **Lineage of comparator materials (critical under this protocol).**
   - Material entities whose data in this paper come only from cited or
     historical sources are accepted as `study=current`:
     - **v4:** Kel-F 81, Viton A, Viton A-500, Fluorel.
     - **Live:** Viton A, Viton A-500, Fluorel.
   - The original v4 review counted them correct; this protocol counts them
     critical.
   - A decision is needed on what `study` means for a Material identity that the
     current paper discusses but did not test.
4. **Table text accepted as statements (live, critical).**
   - The page-12 span joining the Figure 2 caption to the Table 3 title and
     header was accepted twice:
     - once as a statement that stops mid-row;
     - once as Publication/documentary_context, which demotes measured MSFC rows
       to context.
   - Table regions should not be eligible statement anchors.
