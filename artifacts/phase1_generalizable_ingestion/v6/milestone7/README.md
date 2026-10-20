# Phase 1 v6, milestone 7: measuring and improving on several development investigations

**Status: `PHASE1_COMPLETE=NO`.** The development readiness gate (mandate §13: material recall improvement on several exposed investigations) is not met, so the independent holdout (NTRS 20170004702, registered in `../holdout_registration/`) was not acquired.

## What was run

New live runs with frozen code `1dffc83` (3,600 s budget, 0 approvals) on the three other exposed development investigations with frozen v4 targets. The originals were downloaded from ntrs.nasa.gov with Diego's approval, and their sha256 equals the v4 receipts.

| Run | Source | Calls / time |
| --- | --- | --- |
| `ignition_live_1dffc83/` | Lunar ignition, NTRS 20250002114 | 20 / 1,166 s |
| `regulator_live_1dffc83/` | Oxygen regulator, NTRS 20170003941 | 9 / 288 s |
| `textiles_live_1dffc83/` | Textiles slide deck, NTRS 20260005493 | 6 / 104 s |

## Result (`development_target_outcomes.json`)

Each target was adjudicated by the branch author against the run's active records, replayed offline at the stated code.

| Source | Frozen code `1dffc83` | Code `031f5ab` |
| --- | --- | --- |
| Lunar ignition | 6/29 | 10/29 = 0.34 |
| Oxygen regulator | 11/32 | 18/32 = 0.56 |
| Textiles (slides) | 5/29 | 8/29 = 0.28 |
| PTFE, 12 reviewed runs (`rescored_031f5ab/`, official scorer) | — | 27–28/34, precision 0.981–1.000, 0 critical |

- **The gate is far from met.** Recall on the three other investigations is 0.28–0.56.
- **Most remaining misses are proposals the model never made.** Above all procedure quantities and relations, and on the slide deck almost everything.
- **A smaller part is held correctly but cannot yet be recovered**, for example values whose subject is only the subsection's group.

## What changed (general mechanisms; each checked on all sources)

**Document structure**
- An unnumbered standard heading ("Experimental Method") is a major section in a Roman-numbered paper.
- In a slide deck each page's title is its section.
- A group is named by its printed section heading.
- An acronym form of a printed name ("POR 2.0, s/n 003") is normalized to that name.

**Quantities**
- Common laboratory units: ms, µL, L, ft³, RPM, pph, slm, mg/ft²; psid is kept as a differential pressure.
- Names linked through "ranged from" or a short phrase before "of".
- A value modifying its name ("a 10 cm/s primer flow") or in parentheses after it ("a slow flow (~30 cm/s)").
- An unnamed pressure setting is named by its unit.

**Attribution (critical errors found in development and fixed)**
- A relative clause ("… duct where the samples were tested") separates a value from another noun's subject.
- A printed difference ("5 to 10% higher than") is derived, not a concentration.
- Slide or caption lines are separate units, so a 37% O2 is no longer given to the specimen named on the line above.

**Roles and identities held**
- Criteria ("if …, it was identified as …").
- Definitions ("the limit … is the highest concentration where …").
- Plot keys ("the closed symbols … are the centrifuge data").
- Fragments and contact blocks.
- Running footers.
- Apparatus and section titles as groups ("drop tower", "Testing Methodology").
- Figure captions as experiment families.
- Tests or standards as conditions.

**Relations**
- A group's material by its printed name ("First Dodecane Wetted … Test Series").
- "The regulator tested was the <specimen>" gives the investigation's usesSample.

**Statements**
- Statements whose proposed group the validator holds are scoped to the study when the passage is the paper's own research text.
- Guidance and requirements are the paper's own outside the results sections.
- Specimen-dimension role conflicts are settled as configuration.

Quality at `031f5ab`: `ruff format --check`, `ruff check`, `pytest` (716 tests).

## Next

1. **Procedure quantities and relations the model omits.** Deterministic candidates from the paper's own syntax inside a group's subsection, validated like model proposals.
2. **Slide decks.** More complete propositions per slide, and caption or diagram text kept out of statements.
3. **Precision review.** Record-by-record on ignition and regulator.
4. **New live runs on all four investigations.** The gate requires material improvement on several of them.

Only then comes the readiness gate and the frozen-code prospective holdout.
