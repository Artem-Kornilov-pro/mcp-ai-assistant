"""MCP server for public holidays via date.nager.at (no API key needed)."""

from typing import Any

import httpx
from fastmcp import FastMCP

mcp = FastMCP("Holidays")

BASE_URL = "https://date.nager.at/api/v3"


def _request(path: str) -> Any:
    """Make a GET request to the Nager.Date API."""
    response = httpx.get(f"{BASE_URL}/{path}", timeout=15.0, follow_redirects=True)
    if response.status_code == 404:
        raise ValueError(f"Unknown country code or resource: {path}")
    if response.status_code not in (200, 204):
        raise RuntimeError(f"Holidays API error: {response.status_code}")
    if response.status_code == 204 or not response.content:
        return []
    return response.json()


@mcp.tool()
def get_public_holidays(country_code: str, year: int) -> str:
    """Get all public holidays for a country in a given year.

    Args:
        country_code: ISO 3166-1 alpha-2 country code (e.g. 'RU', 'US', 'DE').
        year: Year to look up.

    Returns:
        One "date — name" line per holiday.
    """
    holidays = _request(f"PublicHolidays/{year}/{country_code.upper()}")
    if not holidays:
        return f"No public holidays found for {country_code.upper()} in {year}"

    return "\n".join(f"{h['date']} — {h['localName']} ({h['name']})" for h in holidays)


@mcp.tool()
def is_public_holiday(country_code: str, date: str) -> str:
    """Check whether a specific date is a public holiday in a country.

    Args:
        country_code: ISO 3166-1 alpha-2 country code (e.g. 'RU', 'US', 'DE').
        date: Date in YYYY-MM-DD format.

    Returns:
        Whether the date is a holiday, and its name if so.
    """
    year = date.split("-", 1)[0]
    holidays = _request(f"PublicHolidays/{year}/{country_code.upper()}")
    match = next((h for h in holidays if h["date"] == date), None)

    if match is None:
        return f"{date} is not a public holiday in {country_code.upper()}"
    return (
        f"{date} is a public holiday in {country_code.upper()}: "
        f"{match['localName']} ({match['name']})"
    )


@mcp.tool()
def get_next_holidays(country_code: str) -> str:
    """Get the next upcoming public holidays for a country.

    Args:
        country_code: ISO 3166-1 alpha-2 country code (e.g. 'RU', 'US', 'DE').

    Returns:
        One "date — name" line per upcoming holiday.
    """
    holidays = _request(f"NextPublicHolidays/{country_code.upper()}")
    if not holidays:
        return f"No upcoming public holidays found for {country_code.upper()}"

    return "\n".join(f"{h['date']} — {h['localName']} ({h['name']})" for h in holidays)


@mcp.tool()
def list_holiday_countries() -> str:
    """List countries supported by the holiday tools.

    Returns:
        Comma-separated "CODE (Name)" list of supported countries.
    """
    countries = _request("AvailableCountries")
    return ", ".join(f"{c['countryCode']} ({c['name']})" for c in countries)


if __name__ == "__main__":
    mcp.run()
