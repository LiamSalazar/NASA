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
