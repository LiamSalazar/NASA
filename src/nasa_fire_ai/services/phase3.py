"""Explicit, inspectable Phase-3 orchestration; there is no autonomous tool loop."""

import hashlib
import time
from pathlib import Path

from nasa_fire_ai.config import Settings
from nasa_fire_ai.evidence import EvidenceRegistry
from nasa_fire_ai.llm.interfaces import (
    GroundedSynthesisLLM,
    NvidiaGroundedSynthesizer,
    NvidiaQueryInterpreter,
    ProviderFailure,
    QueryInterpreterLLM,
)
from nasa_fire_ai.models import (
    AnswerResponse,
    ConversationContext,
    ExecutionTrace,
    GroundedAnswerDraft,
    ProposedQueryIntent,
)
from nasa_fire_ai.query.phase3 import (
    deterministic_proposal,
    lexicon_digest,
    ontology_digest,
    validate_proposed_intent,
)
from nasa_fire_ai.services.grounding import GroundingValidator
from nasa_fire_ai.services.pipeline import build_bundle
from nasa_fire_ai.services.product import scientific_answer
from nasa_fire_ai.services.renderer import render, render_grounded


class Phase3AssistantService:
    def __init__(
        self,
        root: Path | None = None,
        settings: Settings | None = None,
        interpreter: QueryInterpreterLLM | None = None,
        synthesizer: GroundedSynthesisLLM | None = None,
    ):
        self.root = root or Path(__file__).resolve().parents[3]
        self.settings = settings or Settings()
        self.registry = EvidenceRegistry(self.settings.registry_path)
        model = self.settings.nvidia_phase3_model
        self.interpreter = interpreter or (
            NvidiaQueryInterpreter(
                self.settings.nvidia_api_key, self.settings.nvidia_base_url, model
            )
            if self.settings.nvidia_api_key
            else None
        )
        self.synthesizer = synthesizer or (
            NvidiaGroundedSynthesizer(
                self.settings.nvidia_api_key, self.settings.nvidia_base_url, model
            )
            if self.settings.nvidia_api_key
            else None
        )
        self._interpretation_cache: dict[str, object] = {}

    def _cache_key(self, query: str, context: ConversationContext | None) -> str:
        model = self.interpreter.model_identity if self.interpreter else "deterministic"
        prompt = (
            self.interpreter.prompt_version if self.interpreter else "deterministic-proposal-v1"
        )
        raw = "|".join(
            [
                query,
                model,
                prompt,
                "phase3-proposed-v1",
                lexicon_digest(),
                ontology_digest(),
                (context or ConversationContext()).model_dump_json(),
            ]
        )
        return hashlib.sha256(raw.encode()).hexdigest()

    def answer_query(
        self,
        query: str,
        conversation_context: ConversationContext | None = None,
        detail_level: str = "standard",
    ) -> AnswerResponse:
        if detail_level not in {"concise", "standard", "technical"}:
            raise ValueError("detail_level must be concise, standard, or technical")
        began = time.perf_counter()
        trace = ExecutionTrace(raw_query=query)
        key = self._cache_key(query, conversation_context)
        interpretation_start = time.perf_counter()
        proposal = self._interpretation_cache.get(key)
        if proposal is None:
            cached = self.registry.get_phase3_cache(key, "validated-interpretation-proposal")
            if cached:
                proposal = ProposedQueryIntent.model_validate(cached)
        if proposal is None:
            if self.interpreter:
                try:
                    proposal = self.interpreter.interpret(query)
                    trace.model_metadata["interpreter"] = self.interpreter.metadata()
                except (ProviderFailure, ValueError) as exc:
                    trace.fallback_status.append(f"interpreter fallback: {type(exc).__name__}")
                    proposal = deterministic_proposal(query)
            else:
                trace.fallback_status.append("interpreter fallback: provider unavailable")
                proposal = deterministic_proposal(query)
            self._interpretation_cache[key] = proposal
            self.registry.set_phase3_cache(
                key,
                "validated-interpretation-proposal",
                proposal.model_dump(mode="json"),  # type: ignore[union-attr]
            )
        elif self.interpreter is None:
            # Cache content was produced under the same model/ontology/lexicon key;
            # still disclose that no live LLM was used for this request.
            trace.fallback_status.append(
                "interpreter fallback: provider unavailable (cached proposal)"
            )
        trace.proposed_intent = proposal  # type: ignore[assignment]
        validated = validate_proposed_intent(proposal, query, conversation_context)  # type: ignore[arg-type]
        trace.validated_intent = validated
        trace.validation_actions = validated.validation_actions
        trace.latency_ms["interpretation"] = (time.perf_counter() - interpretation_start) * 1000

        retrieval_start = time.perf_counter()
        bundle = build_bundle(validated.intent, query, self.root, self.registry)
        bundle.coverage_notes.extend(
            ["Ambiguous terms were not used as canonical retrieval constraints."]
            if validated.ambiguities
            else []
        )
        bundle.retrieval_metadata = {"architecture": "KG + FTS5/BM25", "vectors_enabled": False}
        trace.evidence_ids = [p["evidence_id"] for p in bundle.evidence_passages]
        trace.latency_ms["retrieval"] = (time.perf_counter() - retrieval_start) * 1000

        draft: GroundedAnswerDraft | None = None
        synthesis_start = time.perf_counter()
        if self.synthesizer:
            try:
                candidate = self.synthesizer.synthesize(bundle)
                result = GroundingValidator().validate(candidate, bundle)
                trace.grounding_valid = result.valid
                if not result.valid:
                    raise ProviderFailure(
                        "grounding validation rejected draft: " + "; ".join(result.errors)
                    )
                draft = candidate
                trace.model_metadata["synthesizer"] = self.synthesizer.metadata()
            except (ProviderFailure, ValueError) as exc:
                trace.fallback_status.append(f"synthesis fallback: {type(exc).__name__}")
        else:
            trace.fallback_status.append("synthesis fallback: provider unavailable")
        trace.latency_ms["synthesis_and_validation"] = (
            time.perf_counter() - synthesis_start
        ) * 1000

        answer = scientific_answer(query, bundle, self.root)
        if draft:
            answer.generated_claims = draft.claims
            answer.coverage_notes = list(
                dict.fromkeys(answer.coverage_notes + draft.coverage_notes)
            )
            rendered = render_grounded(draft, answer, detail_level)
        else:
            rendered = render(bundle)
        trace.latency_ms["total"] = (time.perf_counter() - began) * 1000
        return AnswerResponse(
            answer=answer,
            rendered_answer=rendered,
            validated_intent=validated,
            evidence_bundle=bundle,
            draft=draft,
            trace=trace,
        )
