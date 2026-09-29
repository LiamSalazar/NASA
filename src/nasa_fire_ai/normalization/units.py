"""Deliberately small, explicit conversion table; source values are never overwritten."""


def normalize(value: float, unit: str) -> tuple[float, str]:
    u = unit.strip().lower().replace(" ", "")
    table = {
        "%": (0.01, "fraction"),
        "fraction": (1, "fraction"),
        "cm/s": (0.01, "m/s"),
        "m/s": (1, "m/s"),
        "mm/s": (0.001, "m/s"),
        "kpa": (1000, "Pa"),
        "pa": (1, "Pa"),
        "cm": (0.01, "m"),
        "mm": (0.001, "m"),
        "m": (1, "m"),
        "w": (1, "W"),
        "s": (1, "s"),
    }
    if u not in table:
        raise ValueError(f"Unsupported unit: {unit}")
    factor, canonical = table[u]
    return value * factor, canonical
