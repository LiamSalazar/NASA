"""Deliberately small, explicit conversion table; source values are never overwritten.

Dimensional equivalence is never semantic-property equivalence: joules may be an
impact energy or a heat release, and the table says nothing about which.
"""

PSI_PA = 6894.757293168361
CALORIE_J = 4.184  # thermochemical calorie
FOOT_POUND_FORCE_J = 1.3558179483314004

# unit -> (factor, canonical unit, dimension); value * factor (+ offset) is canonical.
TABLE = {
    "%": (0.01, "fraction", "fraction"),
    "percent": (0.01, "fraction", "fraction"),
    "fraction": (1, "fraction", "fraction"),
    "ppm": (0.000001, "fraction", "fraction"),
    "um": (0.000001, "m", "length"),
    "µm": (0.000001, "m", "length"),
    "μm": (0.000001, "m", "length"),
    "cm/s": (0.01, "m/s", "velocity"),
    "m/s": (1, "m/s", "velocity"),
    "mm/s": (0.001, "m/s", "velocity"),
    "mm2/s": (0.000001, "m2/s", "area_rate"),
    "mm²/s": (0.000001, "m2/s", "area_rate"),
    "mm^2/s": (0.000001, "m2/s", "area_rate"),
    "m2/s": (1, "m2/s", "area_rate"),
    "m²/s": (1, "m2/s", "area_rate"),
    "m^2/s": (1, "m2/s", "area_rate"),
    "kpa": (1000, "Pa", "pressure"),
    "mpa": (1000000, "Pa", "pressure"),
    # Conventional millimetres of mercury (0 °C), expressed in SI pascals.
    # This is a unit conversion only; it does not establish property identity.
    "mmhg": (133.322387415, "Pa", "pressure"),
    "pa": (1, "Pa", "pressure"),
    "psi": (PSI_PA, "Pa", "pressure"),
    "psia": (PSI_PA, "Pa", "pressure"),
    # Gauge pressure is relative to an unstated ambient; it never becomes absolute.
    "psig": (PSI_PA, "Pa_gauge", "gauge_pressure"),
    "cm": (0.01, "m", "length"),
    "mm": (0.001, "m", "length"),
    "m": (1, "m", "length"),
    "in": (0.0254, "m", "length"),
    "in.": (0.0254, "m", "length"),
    "inch": (0.0254, "m", "length"),
    "inches": (0.0254, "m", "length"),
    "w": (1, "W", "power"),
    "k": (1, "K", "temperature"),
    "s": (1, "s", "time"),
    "j": (1, "J", "energy"),
    "joule": (1, "J", "energy"),
    "joules": (1, "J", "energy"),
    "kj": (1000, "J", "energy"),
    "ft-lbf": (FOOT_POUND_FORCE_J, "J", "energy"),
    "ft-lb": (FOOT_POUND_FORCE_J, "J", "energy"),
    "ft-lbs": (FOOT_POUND_FORCE_J, "J", "energy"),
    "ftlbs": (FOOT_POUND_FORCE_J, "J", "energy"),
    # A rate of temperature change has no offset: one Fahrenheit degree is 5/9 K.
    "°f/min": (5 / 9 / 60, "K/s", "temperature_rate"),
    "degreesf/min": (5 / 9 / 60, "K/s", "temperature_rate"),
    "°c/min": (1 / 60, "K/s", "temperature_rate"),
    "degreesc/min": (1 / 60, "K/s", "temperature_rate"),
    "ft·lbf": (FOOT_POUND_FORCE_J, "J", "energy"),
    "cal/g": (CALORIE_J * 1000, "J/kg", "specific_energy"),
    "kcal/g": (CALORIE_J * 1000000, "J/kg", "specific_energy"),
    "cal/gram": (CALORIE_J * 1000, "J/kg", "specific_energy"),
    "kcal/gram": (CALORIE_J * 1000000, "J/kg", "specific_energy"),
    "j/gram": (1000, "J/kg", "specific_energy"),
    "j/g": (1000, "J/kg", "specific_energy"),
    "kj/g": (1000000, "J/kg", "specific_energy"),
    "kj/kg": (1000, "J/kg", "specific_energy"),
    "mj/kg": (1000000, "J/kg", "specific_energy"),
    "kg": (1, "kg", "mass"),
}
# Affine scales: canonical = value * factor + offset (kelvin).
AFFINE = {
    "°c": (1, 273.15),
    "ºc": (1, 273.15),
    "degc": (1, 273.15),
    "celsius": (1, 273.15),
    "degreesc": (1, 273.15),
    "°f": (5 / 9, 273.15 - 32 * 5 / 9),
    "ºf": (5 / 9, 273.15 - 32 * 5 / 9),
    "degf": (5 / 9, 273.15 - 32 * 5 / 9),
    "degreesf": (5 / 9, 273.15 - 32 * 5 / 9),
    "fahrenheit": (5 / 9, 273.15 - 32 * 5 / 9),
}
PRESSURE_REFERENCE = {"psia": "ABSOLUTE", "psig": "GAUGE", "psi": "UNSPECIFIED"}


def key(unit: str) -> str:
    return unit.strip().lower().replace(" ", "").replace("‑", "-")


def normalize(value: float, unit: str) -> tuple[float, str]:
    u = key(unit)
    if u in AFFINE:
        factor, offset = AFFINE[u]
        return value * factor + offset, "K"
    if u not in TABLE:
        raise ValueError(f"Unsupported unit: {unit}")
    factor, canonical, _ = TABLE[u]
    return value * factor, canonical


def interpret(unit: str | None) -> dict | None:
    """Dimension and reference of a printed unit, or None when it is not established."""
    if not unit:
        return None
    u = key(unit)
    if u in AFFINE:
        return {
            "original_unit": unit,
            "canonical_unit": "K",
            "dimension": "temperature",
            "conversion": "AFFINE",
        }
    if u not in TABLE:
        return None
    _, canonical, dimension = TABLE[u]
    result = {
        "original_unit": unit,
        "canonical_unit": canonical,
        "dimension": dimension,
        "conversion": "LINEAR",
    }
    if dimension in {"pressure", "gauge_pressure"}:
        result["pressure_reference"] = PRESSURE_REFERENCE.get(u, "UNSPECIFIED")
    return result
