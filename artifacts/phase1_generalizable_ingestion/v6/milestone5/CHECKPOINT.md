# Phase 1 v6 checkpoint after milestone 5 (`diego/research`)

**PHASE1_COMPLETE=NO.** Resume from here.

- **Code:** `77828b9` (author Diegomed11). `main` untouched at `54445d0`. 695 tests pass, and ruff is clean.
- **Frozen-code live confirmations on PTFE:** both failed. Run 12 scored 24/34 at 0.934, and run 13 scored 18/34 at 0.900, with 0 critical in both.
- **Twelve reviewed runs at `77828b9`:**
  - recall 25–28/34, with nine runs at 28/34;
  - precision 0.978–1.000;
  - 0 critical in every run.
- **Closure rule (2026-10-20):** consecutive PTFE runs are a stability check, not the closure criterion.

## Next concrete action

1. **Milestone 6, material composition.**
   - Verify the NASA evidence for the Salox-M® composition and the bronze filler.
   - Find what the ontology, SemanticRegistry and contracts already offer.
   - Add a generic, document-driven composition mechanism in staging: component relation, contextual component role, proportions with their documented basis, and natural-language explanations generated from the relations.
   - No global ontology or baseline change, and no evaluator change.
2. **Variance:** measure and reduce it on several exposed development investigations, not only PTFE.
3. **Readiness gate (§13), then the prospective independent evaluation** with frozen code and contracts, on an unexposed NASA lineage.
