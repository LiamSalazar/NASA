"""Requests sent ahead yield to an earlier window's retry before the brake refuses it.

Network-free: a fake client bills a fixed usage per request and fails chosen
requests once with a connection reset (sent, billing unknown, so the reservation
is kept). A brake with room for the whole run's billing plus its largest
reservation leaves every decision of concurrency 1 unchanged at concurrency 3.
"""

import json
import re
import threading
from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import pytest
from test_document_extraction import submitted
from test_prefetch_brake import TEXT, USAGE, fresh_service

from nasa_fire_ai.config import Settings
from nasa_fire_ai.ingestion import document_extraction
from nasa_fire_ai.ingestion.document_extraction import STAGES, ExtractionBudget


def failing_client(failures):
    """Bill USAGE per answered request; fail once each (stage, run) in ``failures``."""
    client, lock = Mock(), threading.Lock()
    sent, pending = [], set(failures)

    def respond(**kwargs):
        content = kwargs["messages"][1]["content"]
        payload = json.loads(content)
        with lock:
            sent.append(content)
            hit = next(
                (
                    f
                    for f in pending
                    if payload["stage"] == f[0] and re.search(rf"Run {f[1]} was", content)
                ),
                None,
            )
            pending.discard(hit)
        if hit:
            raise httpx.ReadError("connection reset after the request was sent")
        result = {k: [] for k in STAGES[payload["stage"]]}
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=json.dumps(result)), finish_reason="stop"
                )
            ],
            usage=SimpleNamespace(
                model_dump=lambda: {
                    "prompt_tokens": USAGE - 100,
                    "completion_tokens": 100,
                    "total_tokens": USAGE,
                }
            ),
        )

    client.client.with_options.return_value.chat.completions.create.side_effect = respond
    return client, sent


def run(tmp_path, monkeypatch, name, concurrency, brake, failures=()):
    monkeypatch.setenv("SCIENCE_WINDOW_CONCURRENCY", str(concurrency))
    # Retries wait Retry-After style backoff; the test does not need the wall time.
    monkeypatch.setattr(document_extraction.time, "sleep", lambda seconds: None)
    service = fresh_service(tmp_path / name)
    package = submitted(service, TEXT)
    client, sent = failing_client(failures)
    result = service.prepare_scientific(
        package["id"],
        Settings(root=service.root),
        model_enabled=True,
        budget=ExtractionBudget(segment_chars=1000, max_total_tokens=brake),
        client=client,
    )
    attempts = [
        json.loads(row[0])
        for row in service.registry.db.execute(
            "SELECT payload_json FROM phase3_cache WHERE cache_kind='scientific_document_attempt'"
        )
    ]
    service.registry.db.close()
    return result, sent, attempts


def decisions(result):
    return [
        (o.get("stage"), o["model"], o.get("attempts")) for o in result["processing"]["outcomes"]
    ]


def records(result):
    return json.dumps(result["package"]["scientific_extraction"]["records"], sort_keys=True)


def roomy_brake(result):
    """The run's whole billing plus its largest reservation: concurrency 1 never stops."""
    processing = result["processing"]
    largest = max(o.get("reserved_tokens_per_attempt", 0) for o in processing["outcomes"])
    return processing["tokens_consumed_or_reserved"] + largest


def retained_reservations(attempts):
    """Reservations kept for requests that left and failed without a known usage."""
    return sum(
        a["outcome"]["reserved_tokens_per_attempt"]
        for a in attempts
        if a.get("state") == "FINISHED"
        and a.get("outcome", {}).get("error_type") == "network"
        and not a["outcome"].get("transport", {}).get("request_not_sent")
    )


def billed(sent, failures):
    return (len(sent) - len(failures)) * USAGE


@pytest.mark.parametrize("stage", ["relationships", "propositions"])
def test_a_retry_in_window_one_completes_at_concurrency_three(tmp_path, monkeypatch, stage):
    failures = [(stage, "A1")]
    reference, _, _ = run(tmp_path, monkeypatch, "free", 1, None, failures)
    brake = roomy_brake(reference)
    one, sent_one, _ = run(tmp_path, monkeypatch, "one", 1, brake, failures)
    three, sent_three, _ = run(tmp_path, monkeypatch, "three", 3, brake, failures)
    assert decisions(one) == decisions(reference)
    assert "DEFERRED_BUDGET" not in {model for _, model, _ in decisions(three)}
    assert decisions(three) == decisions(one)
    assert records(three) == records(one)
    assert sorted(sent_three) == sorted(sent_one)


def test_billing_stays_under_the_brake_and_the_counter_is_billing_plus_kept_reservations(
    tmp_path, monkeypatch
):
    failures = [("relationships", "A1"), ("identity", "A4")]
    reference, _, _ = run(tmp_path, monkeypatch, "free", 1, None, failures)
    brake = roomy_brake(reference)
    for concurrency in (1, 3):
        result, sent, attempts = run(
            tmp_path, monkeypatch, f"c{concurrency}", concurrency, brake, failures
        )
        assert billed(sent, failures) <= brake
        assert result["processing"]["tokens_consumed_or_reserved"] == billed(
            sent, failures
        ) + retained_reservations(attempts)


@pytest.mark.parametrize(
    "failures",
    [
        [("identity", "A1")],
        [("identity", "A12")],
        [("propositions", "A5")],
        [("relationships", "A1"), ("relationships", "A2")],
        [("identity", "A3"), ("propositions", "A1"), ("relationships", "A7")],
    ],
)
def test_a_brake_with_room_for_the_run_decides_as_concurrency_one(tmp_path, monkeypatch, failures):
    reference, _, _ = run(tmp_path, monkeypatch, "free", 1, None, failures)
    brake = roomy_brake(reference)
    one, sent_one, _ = run(tmp_path, monkeypatch, "one", 1, brake, failures)
    three, sent_three, _ = run(tmp_path, monkeypatch, "three", 3, brake, failures)
    assert decisions(one) == decisions(reference)
    assert decisions(three) == decisions(one)
    assert records(three) == records(one)
    assert sorted(sent_three) == sorted(sent_one)
