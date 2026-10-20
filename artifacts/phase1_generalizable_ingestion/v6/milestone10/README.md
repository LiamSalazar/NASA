# Phase 1 v6, milestone 10: provider fallback and quantity validation mechanisms

**Status: `PHASE1_COMPLETE=NO`.** No live run was made in this milestone. The §13 gate is not met and the holdout has not been acquired.

## Provider fallback

**Why it changed.** In evaluation B (`../milestone9/`), one propositions window was lost on PTFE (pp. 9–12 and 18) and one on the regulator (pp. 1 and 4). The primary model failed: the 600 s deadline on PTFE, HTTP 500 three times on the regulator. Every call to the configured fallback `nvidia/nemotron-3-super-120b-a12b` then returned HTTP 404 "function not found for account". The model is listed by `GET /v1/models`, but the key cannot call it.

**How the replacement was chosen** (2026-10-20, key from `.env`, never printed):

| Model | Minimal call | Call with the adapter's request shape (`chat_template_kwargs.enable_thinking`, `reasoning_budget`, JSON response) |
| --- | --- | --- |
| `nvidia/nemotron-3-ultra-550b-a55b` | 200 | **400**: the server rejects `reasoning_budget` ("thinking_token_budget is not yet supported"). It would fail as a fallback. |
| `nvidia/nemotron-3.5-lightning-30b-a3b` | 200 | **200**, valid JSON |

Four calls in total, with no scientific content.

**Decision.** `NVIDIA_SCIENCE_FALLBACK_MODELS=nvidia/nemotron-3.5-lightning-30b-a3b`, set in `.env.example` and in the local `.env`, which is not committed.
- It is the same Nemotron 3.5 generation as the primary model and accepts the same request.
- It is a smaller model. Any record from a window it answers stays traceable through the run's `served_models` and `requested_model` per call.
- The primary model is unchanged. Retry counts and budgets are unchanged.

## Quantity validation mechanisms (from `../milestone9/quantity_rejection_audit.md`)

Each mechanism is one commit. Its effect is measured by offline replay (evaluation A, 0 model calls) of 26 inputs:
- the 5 exposed v4 packages;
- the 2 PTFE runs with historical negatives;
- the 12 reviewed PTFE runs;
- the 3 milestone 7 development runs;
- the 4 evaluation B runs of milestone 9.

The baseline is code `b19f3c6`, which is the same validation code as `1850be3`.

### (a) Units the unit inventory already interprets (`numeric_expressions.UNIT_LITERAL`)

| | |
| --- | --- |
| Class (addendum §2) | general dimensional rule |
| Motivated by | ignition: "299 l", "1.4 m3 (50 ft3)" rejected as `QUANTITY_NOT_ORIGINAL_NUMERIC_EXPRESSION` |
| Change | The recognition grammar now reads the lowercase litre (`l`, `ml` …) and the cubic or square foot (`ft3`, `ft^3`, `ft²`), which `normalization.units` already interprets. A bare `l` is ambiguous: it is split only against an identical declared unit, never with no unit, and case stays significant (`l` ≠ `L`). |
| Tests | `tests/test_numeric_expressions.py`. Metamorphic: spacing ("299 l" / "299l"), caret and superscript forms. Negative: undeclared `l`; `l` against `L`; `lbs`, `lm` and `ft` are not litres. |
| Effect (replay) | 0 accepted records added or removed on all 26 inputs. On ignition (B and A), 6 rejections move from `QUANTITY_NOT_ORIGINAL_NUMERIC_EXPRESSION` to the name check (`QUANTITY_NAME_NOT_IN_SOURCE_SUPPORT`, 5) or to a hold (`QUANTITY_SEMANTICS_OR_UNIT_UNRESOLVED`, 1). The other three sources do not change. |
