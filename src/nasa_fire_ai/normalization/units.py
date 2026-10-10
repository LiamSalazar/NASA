"""Deliberately small, explicit conversion table; source values are never overwritten."""


def normalize(value: float, unit: str) -> tuple[float, str]:
    u = unit.strip().lower().replace(" ", "")
    table = {
        "%": (0.01, "fraction"),
        "fraction": (1, "fraction"),
        "ppm": (0.000001, "fraction"),
        "um": (0.000001, "m"),
        "µm": (0.000001, "m"),
        "μm": (0.000001, "m"),
        "cm/s": (0.01, "m/s"),
        "m/s": (1, "m/s"),
        "mm/s": (0.001, "m/s"),
        "mm2/s": (0.000001, "m2/s"),
        "mm²/s": (0.000001, "m2/s"),
        "mm^2/s": (0.000001, "m2/s"),
        "m2/s": (1, "m2/s"),
        "m²/s": (1, "m2/s"),
        "m^2/s": (1, "m2/s"),
        "kpa": (1000, "Pa"),
        # Conventional millimetres of mercury (0 °C), expressed in SI pascals.
        # This is a unit conversion only; it does not establish property identity.
        "mmhg": (133.322387415, "Pa"),
        "pa": (1, "Pa"),
        "cm": (0.01, "m"),
        "mm": (0.001, "m"),
        "m": (1, "m"),
        "w": (1, "W"),
        "k": (1, "K"),
        "s": (1, "s"),
    }
    if u not in table:
        raise ValueError(f"Unsupported unit: {unit}")
    factor, canonical = table[u]
    return value * factor, canonical
