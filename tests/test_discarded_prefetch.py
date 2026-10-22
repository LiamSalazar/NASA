"""A request sent ahead and then discarded is recorded with its usage; one never sent is not."""

from concurrent.futures import Future
from types import SimpleNamespace

from nasa_fire_ai.ingestion.document_extraction import record_discarded_prefetch
from nasa_fire_ai.llm.scientific_provider import ScientificTransportError


class Registry:
    def __init__(self):
        self.rows = []

    def set_phase3_cache(self, key, kind, payload):
        self.rows.append((kind, payload))


CALL = {"model": "claude-sonnet-5-5", "max_tokens": 8192}


def test_a_sent_and_answered_request_is_recorded_and_counted():
    registry, ahead = Registry(), Future()
    ahead.set_running_or_notify_cancel()
    ahead.set_result(SimpleNamespace(usage={"total_tokens": 1500}, metadata={"provider": "x"}))
    assert record_discarded_prefetch(registry, "propositions", CALL, ahead) == 1500
    ((kind, payload),) = registry.rows
    assert kind == "scientific_document_attempt" and payload["state"] == "FINISHED"
    assert payload["outcome"]["prefetch"] == "DISCARDED"
    assert payload["outcome"]["usage"]["total_tokens"] == 1500


def test_a_failed_request_sent_ahead_is_recorded_without_usage():
    registry, ahead = Registry(), Future()
    ahead.set_running_or_notify_cancel()
    ahead.set_exception(ScientificTransportError("network", metadata={"provider": "x"}))
    assert record_discarded_prefetch(registry, "identity", CALL, ahead) == 0
    ((_kind, payload),) = registry.rows
    assert payload["outcome"]["transport"]["error_type"] == "network"


def test_a_request_never_sent_is_cancelled_and_not_recorded():
    registry = Registry()
    assert record_discarded_prefetch(registry, "identity", CALL, Future()) == 0
    assert registry.rows == []
