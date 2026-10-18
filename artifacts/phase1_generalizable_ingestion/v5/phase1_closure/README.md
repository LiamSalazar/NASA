# Phase 1 closure: tables, scope and lineage (`diego/research`)

**Status: `PHASE1_COMPLETE=NO`.** The closure code removes every critical error
found on the live PTFE runs and keeps precision above the §11 target there.
Recall and retention on that exposed source stay below the frozen v4 minima.
The remaining gaps need decisions outside this branch (see "Blockers for
Liam").

PTFE is `EXPOSED_DEVELOPMENT_REGRESSION_ONLY`, so nothing here is an
independent evaluation. The holdout was deliberately not run.

## What changed

Commits `e19b7c0` and `7997b58`.

- **Tables** (`ingestion/table_continuity.py`, new):
  - a data-first table right after a headed table with the same columns is its
    continuation and inherits the header;
  - row groups (material, batch) carry down, also across a continuation;
  - a leading letter is a footnote marker only when the text printed with that
    table has its legend line; legends are read per table, not per page;
  - a model quantity binds to its row group as `UNIQUE`, `GROUP_CONSTANT` or
    `AMBIGUOUS` (held), needs the column header as its name, and is located in
    its exact printed cell;
  - PDF cell proposals keep row group, legend and lineage as review context.
- **Lineage** (`ingestion/study_attribution.py`, new):
  - a table caption citation (`[4]`), a legend naming an author of the
    document's own reference list, or "obtained from" marks rows as cited or
    external;
  - a material marked `current` that appears only in such rows is held
    (`CURRENT_STUDY_LINEAGE_NOT_ESTABLISHED`);
  - cited work keeps a passage out of current-study scope when it is named in
    the passage, or appears as an author name or bracket citation in the
    sentence before it;
  - a measured observation that reads a table whose caption cites a reference
    is never scoped to the current study.
- **Scope:**
  - `logical_section` no longer strips the first word of a section title
    ("Results and Discussion" was read as "and Discussion", so the whole PTFE
    paper fell under "Introduction");
  - a major heading followed by a subsection on the next line stays major;
  - a research-section statement whose proposed subjects are materials is
    scoped to the one current document investigation. The materials stay as
    proposed subjects. A measured observation also needs test or result
    wording.
- **Statement integrity** (`ingestion/statement_integrity.py`, new). These are
  rejected:
  - whole printed table rows used as a "statement";

  These are held for review:
  - statements cut at an abbreviation or a page break;
  - observations whose source prints a conflicting count;
  - acceptance or recording rules typed as configuration;
  - observations stating a purpose ("in order to show"), which describe a
    procedure;
  - entities labelled with a value and unit ("72 ft-lbs (98J)");
  - one source span accepted with incompatible roles.
- **Numbers:**
  - CSV/export values use the shared grammar: `>425`, `< 5` and an unresolved
    `1,500` stay literal, and `−40` keeps its sign;
  - `~.9 and 4.3` is a `LIST` and cannot be one quantity.
- **Tool:** `scripts/phase1_offline_replay.py` replays every proposal kind of a
  saved package with 0 model calls.
- **Quality:**
  - 615 tests pass: 572 before, plus 43 new synthetic positives, critical
    negatives and metamorphic twins;
  - `ruff check` and `ruff format --check` are clean.

## Measurement 1: first live PTFE run, replayed offline

The input is the raw Nemotron proposals of the live run at `2b7d1d6`, with 0
model calls and the same 36 frozen targets. Scoring uses
`scripts/score_scientific_review.py`. Precision covers every non-duplicate
`SOURCE_SUPPORTED` record (59), not a sample.

| Metric | Live review (records at `2b7d1d6`) | Closure replay (`7997b58`) | Required | Result |
|---|---|---|---|---|
| Semantic recall | 10/34 = 0.294 | 15/34 = 0.441 | v4 min 0.50; §11 0.80 | **FAIL** |
| Evidence retention | 25/34 = 0.735 | 25/34 = 0.735 | v4 min 0.75 | **FAIL** (one target short) |
| Reviewed precision | 25/32 = 0.781 | 57/59 = 0.966 | §11 0.95 | PASS on this exposed source |
| Critical errors | 5 | 0 | 0 | PASS on this exposed source |
| Unreviewed supported records | 0 | 0 | 0 | PASS |

- **Newly correct:** statements 20, 23, 26, 27 and 28.
- **Critical errors removed:**
  - Viton A, Viton A-500 and Fluorel lose `current` lineage (cited rows only);
  - the page-12 Table 3 dump is rejected as a statement, in both its
    observation and its documentary reading.
- **The 2 remaining incorrect records** were already incorrect in the live
  review, and neither is critical: the page-18 narrative framing sentence and
  the page-1 front-matter span.
- **Review basis:** 22 judgments are reused for byte-identical records. The
  other 37 are author adjudication of full records, not an independent review.

## Measurement 2: second live run at `e19b7c0`

`ptfe_live_e19b7c0/` holds a new live run through the ordinary application
(`submit/save/prepare_scientific`).

- **Calls:** 13 model calls in 783 s with `nvidia/nemotron-3.5-super-vl-120b-a12b`.
- **Coverage:** `PARTIAL_MODEL_COVERAGE`, the same status as the first run.
- **Integrity:** no source integrity errors, SQLite `ok`, 0 approvals,
  0 publications, and no credentials in any file.
- **Model output differed sharply from the first run:**
  - 20 quantity proposals instead of 179;
  - one generic "Brass-filled PTFE sample" entity instead of per-batch
    entities. Its table values are rejected because that label is not a
    printed row group.

| Metric | As produced (`e19b7c0`) | Revalidated (`7997b58`) | Required | Result |
|---|---|---|---|---|
| Semantic recall | 14/34 = 0.412 | 14/34 = 0.412 | v4 min 0.50 | **FAIL** |
| Evidence retention | 24/34 = 0.706 | 24/34 = 0.706 | v4 min 0.75 | **FAIL** |
| Reviewed precision | 51/56 = 0.911 | 51/52 = 0.981 | §11 0.95 | FAIL as produced; PASS revalidated |
| Critical errors | 1 | 0 | 0 | FAIL as produced; PASS revalidated |

- **The critical error as produced:** "The reactivity of the same material
  increases by 20%…" reports cited Table 6 data as a current-study
  observation.
- **The four rules added in `7997b58` came from adjudicating this run:**
  cited-table observations, purpose clauses, value-labelled entities, and a
  page that resumes in lower case. The revalidated column is therefore **not
  independent** of the errors it fixes.
- **The one remaining incorrect record:** "the calorimeter displayed the gross
  heat content…" is a method typed as an observation.
- **Review files:** the run's targets and judgments are in
  `ptfe_live_e19b7c0/revalidated_7997b58/review/`. The as-produced figures use
  the same judgments, plus the four held records judged incorrect (one of them
  critical).

## Measurement 3: the five exposed v4 receipts, replayed

`exposed_sources_replay/comparison.json` compares the same saved raw proposals
under the base code (`118ec71`) and the closure code (`7997b58`). It reports
status changes only, and the newly supported records are not reviewed.

| Source | Previously supported, now held or rejected | Newly supported |
|---|---|---|
| LUCI | 20: 18 conflicting roles, 2 slide tables | 0 |
| PTFE (v4) | 5: 3 comparator lineage, 1 value-labelled entity, 1 procedure | 36 |
| Regulator | 1: conflicting roles | 10 |
| Textiles | 2: conflicting roles | 0 |
| Ignition | 1: sentence cut at "(e.g." | 0 |

The earlier LUCI reviews had already judged one reading of such a
conflicting-role pair as incorrect. The rule holds both readings rather than
guessing which one is right.

## Blockers for Liam

1. **Vocabulary blocks all 10 PTFE quantity targets.** The semantic registry
   has 4 properties: `AirflowVelocity`, `FlowDirection`, `OxygenConcentration`
   and `Pressure`. Without approved properties no quantity can be
   `SOURCE_SUPPORTED`. The PTFE values need:
   - heat of combustion;
   - AIT, including the `>425 °C` censored bound;
   - impact energy;
   - test or system pressure (perhaps an alias of `Pressure`);
   - reactions/tests as a ratio.

   Only `sample_thickness` exists, as an accessor. Approving vocabulary is
   ontology governance, not something this branch may do.
2. **Scorer semantics.** Some targets are best handled as `UNRESOLVED`:
   - statements-25 is a source count conflict;
   - statements-24 is a cited result;
   - statements-22 is a recording rule.

   The scorer only credits `SOURCE_SUPPORTED`, so these cannot count as
   recovered. A "correctly held" outcome would need Liam's decision and a newly
   frozen protocol.
3. **Model omissions and variance** (prompts and stage design):
   - the relations for targets 32–33 are missing or class-contradicting, for
     example `hasIntervention` on a Material;
   - batch entities exist in one run but not the other;
   - text quantities are missing or unbound (98 J and 10,000 psia on p9, 12%,
     5%, 40/60%).

   Two live runs of the same paper differ by 159 quantity proposals.
4. **Files of Liam's that this branch edits:**
   - `document_extraction.py`
   - `document_structure.py`
   - `scientific_scope.py` (the `logical_section` bug fix)
   - `pdf_quantities.py`
   - `services/curation.py` (`parse_value`)

   Validation output changes, so saved prepared packages must be regenerated
   (`validate()` reports "regenerate"). Continuation tables now keep their first
   data row as data, so `pdf-quantity` ids on continuation pages change. The
   frozen PTFE targets reference only page-8 ids, which are unchanged.
5. **Holdout not run.** The exposed-source minima are not met, so spending the
   holdout now would only confirm a known failure and use up the source.

## Reproduce

```bash
uv run python scripts/phase1_offline_replay.py artifacts/phase1_generalizable_ingestion/v5/numeric_expression_grammar/ptfe_live_2b7d1d6/prepared.json.gz --output /tmp/replay
```

```bash
uv run python scripts/score_scientific_review.py PREPARED.json REVIEW.json --output METRICS.json
```

The scorer reads plain JSON, so decompress `prepared.json.gz` first. The live
run used:

```bash
uv run python scripts/phase1_exposed_live_run.py --pdf 20090043050.pdf --provenance-from artifacts/phase1_generalizable_ingestion/v4/independent_ptfe_application/prepared.json.gz --workspace OUTSIDE_REPO --directory OUT --timeout-seconds 1800
```

The NTRS PDF is `c9de8948…`.

## Files

- `ptfe_live_replay_118ec71/`: base replay of the first live run's raw output.
- `ptfe_live_replay_7997b58/`: closure replay, `review/source_review.json` and
  `review/scientific_metrics.json`.
- `ptfe_live_e19b7c0/`: second live run, as produced (`prepared.json.gz`,
  `attempts.json.gz`, `summary.json.gz`, `validation.json.gz`,
  `submission.json`).
  - `revalidated_7997b58/`: its offline revalidation, review and metrics.
- `exposed_sources_replay/comparison.json`: five-source status comparison.
