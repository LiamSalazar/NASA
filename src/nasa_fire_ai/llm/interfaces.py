from abc import ABC, abstractmethod

from nasa_fire_ai.models import QueryIntent, ScientificAnswer


class NotConfigured(RuntimeError):
    pass


class QueryInterpreter(ABC):
    @abstractmethod
    def parse(self, text: str) -> QueryIntent: ...


class ScientificSynthesizer(ABC):
    @abstractmethod
    def synthesize(self, answer: ScientificAnswer): ...


class OpenAIQueryInterpreter(QueryInterpreter):
    def parse(self, text):
        raise NotConfigured(
            "OpenAI interpreter is not configured; use controlled vocabulary parsing."
        )


class OpenAIScientificSynthesizer(ScientificSynthesizer):
    def synthesize(self, answer):
        raise NotConfigured("OpenAI synthesizer is not configured; use extractive rendering.")
