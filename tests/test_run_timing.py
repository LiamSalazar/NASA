"""Where a live run's time went, from its attempt receipts; synthetic receipts only."""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def live_run_script():
    spec = importlib.util.spec_from_file_location(
        "phase1_exposed_live_run", ROOT / "scripts" / "phase1_exposed_live_run.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def attempt(start, seconds, first=None, error=None, tokens=(100, 20)):
    return {
        "stage": "propositions",
        "requested_model": "m",
        "outcome": {
            "transport": {
                "started_at": f"2026-01-01T00:00:{start:02d}+00:00",
                "duration_seconds": seconds,
                "time_to_first_token_seconds": first,
            },
            "usage": {"prompt_tokens": tokens[0], "completion_tokens": tokens[1]},
            **({"error_type": error} if error else {}),
        },
    }


def test_sequential_calls_leave_the_rest_of_the_wall_clock_local():
    timing = live_run_script().timing_summary(
        [attempt(0, 10, first=8), attempt(20, 5, error="deadline")],
        "2026-01-01T00:00:00+00:00",
        "2026-01-01T00:00:30+00:00",
    )
    assert timing["provider_seconds"] == 15 and timing["local_seconds"] == 15
    assert timing["failure_causes"] == {"deadline": 1} and timing["failed_attempts"] == 1
    assert timing["per_call"][0]["generation_seconds"] == 2
    assert timing["input_tokens"] == 200 and timing["output_tokens"] == 40


def test_overlapping_calls_count_once():
    # Metamorphic: the same two calls run at once take the provider time of the longer.
    timing = live_run_script().timing_summary(
        [attempt(0, 10), attempt(2, 6)],
        "2026-01-01T00:00:00+00:00",
        "2026-01-01T00:00:12+00:00",
    )
    assert timing["provider_seconds"] == 10 and timing["provider_call_seconds_total"] == 16
    assert timing["local_seconds"] == 2
