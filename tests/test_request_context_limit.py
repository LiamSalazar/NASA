"""Anthropic requests get their own size limit before a window is split; NVIDIA keeps its own."""

from types import SimpleNamespace

from nasa_fire_ai.ingestion.document_extraction import request_context_limit
from nasa_fire_ai.ingestion.extraction_resources import ProviderEnvelope, segment_size


def test_anthropic_requests_have_their_own_limit(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_SCIENCE_REQUEST_CONTEXT_TOKENS", raising=False)
    envelope = ProviderEnvelope()
    assert request_context_limit(SimpleNamespace(science_provider="anthropic"), envelope) == 96000
    monkeypatch.setenv("ANTHROPIC_SCIENCE_REQUEST_CONTEXT_TOKENS", "80000")
    assert request_context_limit(SimpleNamespace(science_provider="anthropic"), envelope) == 80000


def test_nvidia_keeps_its_envelope(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_SCIENCE_REQUEST_CONTEXT_TOKENS", "80000")
    envelope = ProviderEnvelope()
    assert request_context_limit(SimpleNamespace(science_provider="nvidia"), envelope) == (
        envelope.context_tokens
    )


def test_windows_do_not_depend_on_the_request_limit(monkeypatch):
    # Metamorphic: the window size comes from the provider envelope only, so a
    # larger Anthropic limit splits fewer requests without changing any window.
    package = {"evidence": [{"text": "A run was tested. " * 4000}]}
    budget = SimpleNamespace(segment_chars=None, max_output_tokens=None)
    sizes = []
    for limit in ("65536", "96000"):
        monkeypatch.setenv("ANTHROPIC_SCIENCE_REQUEST_CONTEXT_TOKENS", limit)
        sizes.append(segment_size(package, budget, ProviderEnvelope()))
    assert sizes[0] == sizes[1]
