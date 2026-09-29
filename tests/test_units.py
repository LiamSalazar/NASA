import pytest

from nasa_fire_ai.normalization import normalize


def test_units():
    assert normalize(5, "cm/s") == (0.05, "m/s")
    assert normalize(17, "%") == (0.17, "fraction")
    assert normalize(10, "kPa") == (10000, "Pa")
    assert normalize(2, "mm") == (0.002, "m")


def test_unknown_unit():
    with pytest.raises(ValueError):
        normalize(1, "furlong")
