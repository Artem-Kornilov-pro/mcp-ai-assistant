"""MCP server for weather via wttr.in (no API key needed)."""

import httpx
from fastmcp import FastMCP

mcp = FastMCP("Weather")

BASE_URL = "https://wttr.in"


def _request(path: str) -> str:
    """Make a request to wttr.in."""
    url = f"{BASE_URL}/{path}"
    response = httpx.get(url, timeout=15.0)
    if response.status_code != 200:
        raise RuntimeError(f"Weather API error: {response.status_code}")
    return response.text


@mcp.tool()
def get_weather(city: str) -> str:
    """Get current weather for a city.

    Args:
        city: City name (e.g., "Moscow", "London", "Tokyo").

    Returns:
        Current conditions: temperature (°C), wind, humidity, visibility.
    """
    return _request(f"{city}?format=j1&lang=ru")


@mcp.tool()
def get_temperature(city: str) -> str:
    """Get current temperature in Celsius for a city.

    Args:
        city: City name.

    Returns:
        Temperature in °C with feels-like.
    """
    return _request(f"{city}?format=%t+%28ощущается+как+%f%29&lang=ru")


@mcp.tool()
def get_forecast(city: str, days: int = 3) -> str:
    """Get weather forecast for up to 3 days.

    Args:
        city: City name.
        days: Number of days (1-3). Default: 3.

    Returns:
        Formatted forecast with temperatures in °C.
    """
    days = max(1, min(days, 3))
    return _request(f"{city}?format={days}&lang=ru&m")


@mcp.tool()
def get_wind(city: str) -> str:
    """Get wind information for a city.

    Args:
        city: City name.

    Returns:
        Wind speed, direction, and gusts.
    """
    return _request(f"{city}?format=%w&lang=ru")


@mcp.tool()
def get_humidity(city: str) -> str:
    """Get humidity for a city.

    Args:
        city: City name.

    Returns:
        Humidity percentage.
    """
    return _request(f"{city}?format=%h&lang=ru")


@mcp.tool()
def get_astronomy(city: str) -> str:
    """Get sunrise, sunset, and moon phase for a city.

    Args:
        city: City name.

    Returns:
        Sunrise, sunset times, moon phase.
    """
    return _request(f"{city}?format=%S+%s+%m&lang=ru")


@mcp.tool()
def get_weather_ascii(city: str) -> str:
    """Get a visual ASCII weather report for a city.

    Args:
        city: City name.

    Returns:
        Multi-day ASCII art weather chart.
    """
    return _request(f"{city}?lang=ru&m")


@mcp.tool()
def compare_weather(city1: str, city2: str) -> str:
    """Compare current weather between two cities.

    Args:
        city1: First city.
        city2: Second city.

    Returns:
        Side-by-side weather comparison.
    """
    weather1 = _request(f"{city1}?format=%l:+%t+%C&lang=ru").strip()
    weather2 = _request(f"{city2}?format=%l:+%t+%C&lang=ru").strip()
    return f"{weather1}\n{weather2}"


if __name__ == "__main__":
    mcp.run()
