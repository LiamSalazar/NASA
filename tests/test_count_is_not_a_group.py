"""A count of tests says how many, it does not name a group; synthetic text."""

from test_background_sections import records_for
from test_background_sections import service as _service

service = _service

PAPER = (
    "# Synthetic study\n"
    "II. Methods\nSixty test runs were executed in the Alpha O2 Impact Tests.\n"
    "III. Results\nAlpha O2 Impact Tests flames went out at 18% oxygen.\n"
)


def group(service, label, quote):
    records = records_for(service, PAPER, [("g", label, "ExperimentFamily", quote)])
    (record,) = [r for r in records if r["kind"] == "entities"]
    return record


def test_a_count_of_runs_is_held(service):
    record = group(service, "Sixty test runs", "Sixty test runs were executed")
    assert "COUNT_OF_TESTS_IS_NOT_A_GROUP_NAME" in record["reasons"]


def test_a_printed_group_name_with_its_own_words_is_not_a_count(service):
    # Metamorphic: the group's printed name, not its count, names it.
    record = group(service, "Alpha O2 Impact Tests", "the Alpha O2 Impact Tests.")
    assert "COUNT_OF_TESTS_IS_NOT_A_GROUP_NAME" not in record["reasons"]
