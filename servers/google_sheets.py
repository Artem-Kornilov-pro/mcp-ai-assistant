"""MCP server for Google Sheets API integration (personal token auth)."""

import os
from typing import Any

import httpx
from fastmcp import FastMCP

mcp = FastMCP("GoogleSheets")

SHEETS_API = "https://sheets.googleapis.com/v4/spreadsheets"


def _headers() -> dict[str, str]:
    """Get authorization headers using access token from .env."""
    token = os.getenv("GOOGLE_ACCESS_TOKEN", "")
    if not token:
        raise ValueError("GOOGLE_ACCESS_TOKEN environment variable is not set")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def _request(method: str, url: str, **kwargs: Any) -> dict[str, Any]:
    """Make an authenticated Sheets API request."""
    response = httpx.request(
        method=method,
        url=url,
        headers=_headers(),
        timeout=30.0,
        **kwargs,
    )
    if response.status_code == 401:
        raise PermissionError(
            "Access token expired. Get a new one from "
            "https://developers.google.com/oauthplayground"
        )
    if response.status_code == 403:
        raise PermissionError(
            "Access denied. Open the spreadsheet and share it with your own Google account."
        )
    if response.status_code == 404:
        raise FileNotFoundError("Spreadsheet not found. Check the spreadsheet ID.")
    if response.status_code >= 400:
        raise RuntimeError(f"Sheets API error: {response.status_code} - {response.text}")
    return response.json()


@mcp.tool()
def read_sheet(spreadsheet_id: str, range_name: str = "A1:Z100") -> list[list[str]]:
    """Read values from a Google Sheet.

    Args:
        spreadsheet_id: The ID from the sheet URL (between /d/ and /edit).
        range_name: Cell range in A1 notation. Default: A1:Z100.

    Returns:
        List of rows as lists of cell values.
    """
    url = f"{SHEETS_API}/{spreadsheet_id}/values/{range_name}"
    data = _request("GET", url)
    return data.get("values", [])


@mcp.tool()
def write_sheet(
    spreadsheet_id: str,
    range_name: str,
    values: str | list[list[str]],
) -> str:
    """Write values to a Google Sheet.

    Args:
        spreadsheet_id: The ID from the sheet URL.
        range_name: Cell range (e.g., "Sheet1!A1").
        values: List of rows as JSON array, e.g. [["A1","B1"],["A2","B2"]].

    Returns:
        Confirmation with updated range.
    """
    import json as _json

    # Parse string to list if needed
    if isinstance(values, str):
        try:
            values = _json.loads(values)
        except _json.JSONDecodeError:
            # Assume single value
            values = [[values]]

    url = f"{SHEETS_API}/{spreadsheet_id}/values/{range_name}"
    params = {"valueInputOption": "USER_ENTERED"}
    body = {"values": values}

    data = _request("PUT", url, params=params, json=body)
    return f"Updated range: {data.get('updatedRange', range_name)}"


@mcp.tool()
def create_sheet(title: str) -> str:
    """Create a new Google Sheet under your account.

    Args:
        title: Title of the new spreadsheet.

    Returns:
        Spreadsheet ID and URL.
    """
    body = {"properties": {"title": title}}
    data = _request("POST", SHEETS_API, json=body)
    spreadsheet_id: str = data["spreadsheetId"]
    return (
        f"Spreadsheet ID: {spreadsheet_id}\n"
        f"URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
    )


if __name__ == "__main__":
    mcp.run()
