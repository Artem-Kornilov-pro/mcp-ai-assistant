"""MCP server for converting physical units (length, weight, temperature, volume, area)."""

from fastmcp import FastMCP

mcp = FastMCP("Units")

# Each table maps a unit name to how many base units it equals.
_LENGTH = {
    "m": 1.0,
    "km": 1000.0,
    "cm": 0.01,
    "mm": 0.001,
    "mile": 1609.344,
    "yard": 0.9144,
    "foot": 0.3048,
    "inch": 0.0254,
    "nautical_mile": 1852.0,
}

_WEIGHT = {
    "g": 1.0,
    "kg": 1000.0,
    "mg": 0.001,
    "ton": 1_000_000.0,
    "pound": 453.59237,
    "ounce": 28.349523125,
    "stone": 6350.29318,
}

_VOLUME = {
    "l": 1.0,
    "ml": 0.001,
    "cubic_meter": 1000.0,
    "gallon": 3.785411784,
    "quart": 0.946352946,
    "pint": 0.473176473,
    "cup": 0.2365882365,
}

_AREA = {
    "sq_m": 1.0,
    "hectare": 10000.0,
    "sq_km": 1_000_000.0,
    "acre": 4046.8564224,
    "sq_ft": 0.09290304,
    "sq_mile": 2_589_988.110336,
}


def _convert(value: float, from_unit: str, to_unit: str, table: dict[str, float]) -> float:
    """Convert a value between units listed in a base-unit conversion table."""
    if from_unit not in table:
        raise ValueError(f"Unsupported unit: {from_unit}. Use one of {sorted(table)}")
    if to_unit not in table:
        raise ValueError(f"Unsupported unit: {to_unit}. Use one of {sorted(table)}")

    base_value = value * table[from_unit]
    return base_value / table[to_unit]


@mcp.tool()
def convert_length(value: float, from_unit: str, to_unit: str) -> str:
    """Convert a length between units.

    Args:
        value: Value to convert.
        from_unit: Source unit — one of: m, km, cm, mm, mile, yard, foot, inch, nautical_mile.
        to_unit: Target unit (same options).

    Returns:
        Converted value.
    """
    return str(_convert(value, from_unit, to_unit, _LENGTH))


@mcp.tool()
def convert_weight(value: float, from_unit: str, to_unit: str) -> str:
    """Convert a weight/mass between units.

    Args:
        value: Value to convert.
        from_unit: Source unit — one of: g, kg, mg, ton, pound, ounce, stone.
        to_unit: Target unit (same options).

    Returns:
        Converted value.
    """
    return str(_convert(value, from_unit, to_unit, _WEIGHT))


@mcp.tool()
def convert_temperature(value: float, from_unit: str, to_unit: str) -> str:
    """Convert a temperature between Celsius, Fahrenheit, and Kelvin.

    Args:
        value: Value to convert.
        from_unit: Source unit — one of: celsius, fahrenheit, kelvin.
        to_unit: Target unit (same options).

    Returns:
        Converted value.
    """
    units = {"celsius", "fahrenheit", "kelvin"}
    if from_unit not in units:
        raise ValueError(f"Unsupported unit: {from_unit}. Use one of {sorted(units)}")
    if to_unit not in units:
        raise ValueError(f"Unsupported unit: {to_unit}. Use one of {sorted(units)}")

    if from_unit == "fahrenheit":
        celsius = (value - 32) * 5 / 9
    elif from_unit == "kelvin":
        celsius = value - 273.15
    else:
        celsius = value

    if to_unit == "fahrenheit":
        result = celsius * 9 / 5 + 32
    elif to_unit == "kelvin":
        result = celsius + 273.15
    else:
        result = celsius

    return str(result)


@mcp.tool()
def convert_volume(value: float, from_unit: str, to_unit: str) -> str:
    """Convert a volume between units.

    Args:
        value: Value to convert.
        from_unit: Source unit — one of: l, ml, cubic_meter, gallon, quart, pint, cup.
        to_unit: Target unit (same options).

    Returns:
        Converted value.
    """
    return str(_convert(value, from_unit, to_unit, _VOLUME))


@mcp.tool()
def convert_area(value: float, from_unit: str, to_unit: str) -> str:
    """Convert an area between units.

    Args:
        value: Value to convert.
        from_unit: Source unit — one of: sq_m, hectare, sq_km, acre, sq_ft, sq_mile.
        to_unit: Target unit (same options).

    Returns:
        Converted value.
    """
    return str(_convert(value, from_unit, to_unit, _AREA))


if __name__ == "__main__":
    mcp.run()
