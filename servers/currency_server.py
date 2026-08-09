"""MCP server for currency conversion via exchangerate-api.com (no API key needed)."""

from typing import Any

import httpx
from fastmcp import FastMCP

mcp = FastMCP("Currency")

BASE_URL = "https://api.exchangerate-api.com/v4/latest"


def _get_rates(base_currency: str) -> dict[str, Any]:
    """Fetch latest exchange rates for a base currency."""
    url = f"{BASE_URL}/{base_currency.upper()}"
    response = httpx.get(url, timeout=15.0, follow_redirects=True)
    if response.status_code == 404:
        raise ValueError(f"Unsupported currency code: {base_currency}")
    if response.status_code != 200:
        raise RuntimeError(f"Currency API error: {response.status_code}")
    return response.json()


@mcp.tool()
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """Convert an amount from one currency to another using the latest exchange rate.

    Args:
        amount: Amount to convert.
        from_currency: Source currency code (e.g. 'USD', 'EUR', 'RUB').
        to_currency: Target currency code.

    Returns:
        Converted amount with the exchange rate and date used.
    """
    data = _get_rates(from_currency)
    rates = data["rates"]
    to_code = to_currency.upper()
    if to_code not in rates:
        raise ValueError(f"Unsupported currency code: {to_currency}")

    rate = rates[to_code]
    converted = amount * rate
    return (
        f"{amount} {from_currency.upper()} = {converted:.2f} {to_code} "
        f"(rate: {rate}, date: {data['date']})"
    )


@mcp.tool()
def get_exchange_rate(from_currency: str, to_currency: str) -> str:
    """Get the current exchange rate between two currencies.

    Args:
        from_currency: Source currency code (e.g. 'USD').
        to_currency: Target currency code (e.g. 'RUB').

    Returns:
        Exchange rate and the date it was published.
    """
    data = _get_rates(from_currency)
    rates = data["rates"]
    to_code = to_currency.upper()
    if to_code not in rates:
        raise ValueError(f"Unsupported currency code: {to_currency}")

    return f"1 {from_currency.upper()} = {rates[to_code]} {to_code} (date: {data['date']})"


@mcp.tool()
def list_currencies() -> str:
    """List currency codes supported by the currency conversion tools.

    Returns:
        Comma-separated list of supported currency codes.
    """
    data = _get_rates("USD")
    codes = set(data["rates"].keys()) | {"USD"}
    return ", ".join(sorted(codes))


if __name__ == "__main__":
    mcp.run()
