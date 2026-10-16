# Phase 1 checkpoint

HEAD: 3233628; no commit. Changes are in the working tree, exact hashes in implementation_receipt.json.

Production: CurationService.submit_ntrs/prepare_scientific, strict document extraction contracts, structural batching, bounded context, source validators, partial/successful cache replay, typed table attributes, existing ontology instance reuse, ScopeResolver local-exception proof and app/CLI integration.

Passing: ruff formatting/lint, 355 tests, canonical and four isolated native SHACL checks, original-source integrity, idempotence and 2,267 protected file digests. No baseline publication or ontology activation.

Artifacts: final_development_receipts/, final_holdout_deterministic_receipts/, holdout_first_pass/, scientific_quality.json, acceptance_decisions.json; see docs/PHASE1_GENERALIZABLE_SCIENTIFIC_INGESTION.md. Original PDFs are immutable under the receipt workspaces' data/submissions directories and ZIP exports.

Scientific acceptance: PHASE1_COMPLETE=NO. LUCI first pass and post-exposure repair have zero complete model windows; unknown source/subject identifiers, missing entity support, truncation and timeouts prevent full scientific attribution. Complex merged PDF tables and non-run CSV rows still need reliable source-supported scientific classification. No independent expert gold exists.

Resources: all 14 reserved provider calls used; 56,244 received usage tokens, additional failed-call billing unknown. Do not silently spend more inference.

Next concrete task: inspect existing scientific_document_failure checkpoints and isolate entity-reference/support-schema failures with controlled adapters. Reuse exact known-source entity anchors without granting approval or treating initial model associations as authority. Then perform a separately bounded, authorized live replay and source-adjudicate experiment/group/quantity/conclusion recovery. Retain LUCI's failed first-pass boundary and select a genuinely independent investigation before claiming untouched holdout success. Do not overwrite historical receipts or publish a scientific package.
