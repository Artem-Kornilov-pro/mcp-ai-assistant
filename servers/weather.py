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
        Current weather conditions and temperature.
    """
    return _request(f"{city}?format=3&lang=ru")


@mcp.tool()
def get_forecast(city: str, days: int = 3) -> str:
    """Get weather forecast for several days.

    Args:
        city: City name.
        days: Number of days (1-3). Default: 3.

    Returns:
        Weather forecast as formatted text.
    """
    if days < 1:
        days = 1
    if days > 3:
        days = 3
    return _request(f"{city}?format={days}&lang=ru")


if __name__ == "__main__":
    mcp.run()
