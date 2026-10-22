# Package 1.3: does the scorer require global publication? (addendum §3)

I reviewed `scripts/score_scientific_review.py`, the official scorer used for PTFE, and the record-by-record adjudication used for ignition, regulator and textiles (`../review_tools/`, same principle). Nothing was changed: the scorer and the frozen targets are untouched.

## What each state counts as

| state the addendum asks to distinguish | how the scorer treats it | evidence in the code |
|---|---|---|
| Complete source-grounded extraction | A target is `correct` only when its reviewed proposals are `SOURCE_SUPPORTED` | `score()`: "Unresolved or rejected content cannot count as correct recovery" |
| Complete extraction whose property is only **staged** (not in the approved registry) | Counts as correct recall, and is also reported apart | `semantic_recall` includes it; `semantic_recall_approved_properties_only` and `correct_quantity_targets_with_staged_property_only` separate it |
| Genuine scientific ambiguity | `unresolved`, optionally with `hold_assessment: HOLD_IS_THE_CORRECT_OUTCOME` and a source rationale; never recall | `correctly_held_targets`, `counts_as_recall: False` |
| Evidence retained without complete interpretation | `unresolved`, counted in `evidence_retention` (correct + unresolved), not in recall | `evidence_retention` |
| Authorized publication into the canonical baseline | Not consulted. No outcome depends on publication or approval | no reference to publication, approval or baseline state |
| Duplicates | Cannot inflate precision | "Duplicate inference variants cannot inflate scientific precision" |

## Conclusion

- The scorer does **not** require global ontology publication to recognize complete Phase 1 extraction. A staged property already counts, so no correction proposal for Liam is needed.
- It also never credits a staged-only or unresolved record as recovered, as the addendum requires.

## The actual rigidity is upstream of the scorer, in validation

A complete, source-supported proposal can still fail to reach `SOURCE_SUPPORTED` for reasons that are about representation, not evidence. That is a validator or contract issue, handled in packages 2.1 and 3.x; the scorer stays unchanged.
- **Unregistered class:** an entity whose class is not in the approved registry is set to `UNRESOLVED` (`UNREGISTERED_CLASS_NEEDS_SEMANTIC_REVIEW`). Even when it is fully structured and supported, it cannot count.
- **Unprinted name:** a value whose quantity name is not printed in the support is rejected (`QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT`). Package 1.2 found it among the class B rejections.

Package 2.1 will give such proposals a validated "proposed extension" state, separate from "source-supported" and from "published". The scorer can then keep reporting them apart, without any change to it.
