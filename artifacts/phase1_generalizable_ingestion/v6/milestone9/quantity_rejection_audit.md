# Audit of the model's rejected quantity proposals (evaluation B, code `1850be3`)

This is an analysis and a proposal only. **No code, prompt or configuration was changed.** Each proposed correction waits for Diego's approval. It must then be classified under the addendum (§2), and measured on all four sources with metamorphic and negative tests before it is accepted.

Scope: every quantity the model proposed in the three B runs (not candidates, not duplicates).

| Source | Model quantities | Accepted |
| --- | --- | --- |
| Lunar ignition | 99 | 3 |
| Oxygen regulator | 30 | 3 |
| Textiles | 13 | 0 |

## Families, with what the model did and whether the rejection was right

### 1. `QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT`: ignition 41, regulator 5, textiles 7

**What happens.** The model names the quantity with a descriptive label that the page does not print:
- "chamber volume" for "a WSTF 1.4 m3 (50 ft3) chamber";
- "duct ID" for "a 7.4 cm ID by 30 cm long quartz tube duct";
- "O2 concentration" for "48% O2";
- "ball diameter" for "The ball in the figure is 1mm diameter".

**Was the rejection right?** Value, unit and subject are often right. The rejection is right under the current contract, which requires the name in the support. Some proposals also carry a wrong subject: on textiles, the Artemis IV+ atmosphere values go to "Standard Edge Ignition". Rejecting those is right on two counts.

**Proposed general correction.** Separate the printed name from the label:
- The quantity schema gets a `printed_name` field: the exact words of the support that name the quantity. These can be a head noun ("chamber"), an abbreviation ("ID"), a symbol ("O2") or a noun after the value ("diameter").
- The validator checks `printed_name` against the support, plus the unit's dimension for the property. The label stays free.
- **Class:** general scientific (dimensional rule) plus document structure.
- **Expected effect:** ignition geometry and setup values; on regulator "ball diameter"; on textiles "O2" against "O2 concentration", which also removes the duplicate 37 % record. PTFE uses the same family for its table values.
- **Negative tests needed:** a printed noun of another quantity in the same sentence; a unit whose dimension contradicts the label.

### 2. `QUANTITY_UNIT_NOT_BOUND_TO_EXPRESSION`: ignition 26

**What happens.** These are the ignition paper's Table 1 material properties (density 1190, specific heat 1400, and so on), cited from references 21–25. The unit headers are printed in a math font that extracts as garbled glyphs ("ሾ𝑘𝑔…").

**Was the rejection right?** Yes. The unit cannot be bound from the extracted text, and these are cited model inputs, not current measurements (target quantities-28 asks to keep the original header).

**Proposed correction.** None to the validator. Any glyph mapping would be font-specific, which the addendum forbids. Keep these held. If anything, the figure or table route with the page image could read the header (a later, separate decision).

### 3. `QUANTITY_NOT_ORIGINAL_NUMERIC_EXPRESSION`: ignition 16, regulator 2

**What happens.** The model repeats the unit inside the expression ("299 l" with unit "l", "7.4 cm" with unit "cm", ".013in dia"). Or it writes a compound ("1.4 m3 (50 ft3)", "5.2 cm by 14.0 cm", "approximately a second").

**Was the rejection right?** Right under the contract. It costs correct values: the GRC 299 l volume, the WSTF duct and samples, the regulator orifice.

**Proposed general correction (numeric grammar):**
- **(a)** When the expression ends with exactly the unit string, which is printed right after the number in the support, keep only the number as the expression. Nothing is invented, because the remaining number is printed.
- **(b)** Read "A by B <unit>" as two values of the same unit (a dimension pair), each bound to its own printed name.
- Approximate words ("approximately a second") stay rejected.
- **Class:** general scientific (numeric expression grammar). The same grammar runs on every source.
- **Negative tests needed:** a unit string that differs from the printed one; "by" between two different quantities.

### 4. `QUANTITY_NAME_VALUE_NOT_LOCALLY_BOUND` (ignition 3) and `QUANTITY_EXPRESSION_ABSENT` (ignition 2, textiles 1)

**What happens.** "5.2 cm by 14.0 cm samples" (same as 3b). Lists such as "at least 4 flow rates (60, 80, 100, 144 cm/s)", and the bound ">30% O2".

**Proposed general correction.** Expand a printed list of values sharing one unit into one proposal per value, all with the printed name ("flow rates"). Bounds (">30%") keep their comparator. Same class as 3.

### 5. `TEST_ARTICLE_ALIAS_EXPERIMENTAL_GROUP_SCOPE_REQUIRES_REVIEW` (regulator 7) and `QUANTITY_SUBJECT_NOT_IN_APPLICABLE_SOURCE` (regulator 6, textiles 1)

**What happens.** The model gives the test article (POR 2.0, s/n 003) the settings of a test series: 4.05 psid set point, ~1 pph demand, 80–93 msec. It gave 46–49 msec to the first wet series because this run had no second-series entity.

**Was the rejection right?** Holding them was right. In particular, 46–49 msec on the first series would have been a critical false attribution.

**Proposed general correction (document structure):**
- When a value's span lies inside a group's own subsection, propose that group as the subject, and keep the model's subject as the alternative under review. Never move a value across subsections.
- This extends milestone 8's reader to model proposals (rule C2 of the addendum).
- The cleaner path is model-side: the third milestone 8 commit already gives each anchor its heading and group, and the next step is to say in the quantity instruction that settings printed under a group belong to that group.
- **Negative tests needed:** a value under group A's heading that names group B; a value in the method section outside every subsection.

### 6. `CONFIGURATION_OR_DERIVED_IS_NOT_MEASUREMENT`: regulator 5, textiles 3

**What happens.** The model types configuration values as measurements: "tested at 48% O2 and 8.2 psia", "maintained its 4.05 psid set-point at ~1 pph demand", the "100%" in "100% PBI knit fabric".

**Was the rejection right?** Yes, but a correct configuration is lost each time.

**Proposed general correction.**
- Where the support carries an explicit setting cue (the cues already used by `6277466` and milestone 8: "tested at", "set point", "nominal", "target", "at … demand"), re-type the role as `experimental_configuration` instead of rejecting, and mark the record as role-corrected.
- Composition words inside a material name ("100% PBI") stay rejected as quantities.
- **Class:** semantic with evidence (the cue must be printed).

## Ranking (largest expected gain per unit of risk)

1. Family 3a (unit repeated in the expression): mechanical, nothing invented; it covers most of the 16 ignition and both regulator rejections in family 3.
2. Family 1 (`printed_name`): the largest family, but it needs a schema change and new model calls.
3. Family 5 (subject by subsection for model quantities): high value on the regulator, highest risk; negative tests first.
4. Family 6 (role from an explicit setting cue).
5. Families 3b and 4 (dimension pairs, lists).
6. Family 2: no change.

## Two findings outside the quantity families

- **Duplicates are the largest precision cost** on the development sources (`record_precision_review.json`). Ignition has 9 duplicate records out of 23 errors, from two windows or from the model and a candidate. A general deduplication by (kind, subject, normalized value, unit, support span overlap) would remove them.
- **The configured fallback model returns HTTP 404 for this account.** Two propositions windows were lost in B (PTFE pp. 9–12 and 18; regulator pp. 1 and 4). This is a configuration decision, not code: a fallback the account can call, or more primary retries.
