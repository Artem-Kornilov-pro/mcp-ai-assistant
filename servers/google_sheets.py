"""MCP server for Google Sheets API integration."""

import json
import os
from pathlib import Path
from typing import Any

import httpx
from fastmcp import FastMCP

mcp = FastMCP("GoogleSheets")

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
TOKEN_URI = "https://oauth2.googleapis.com/token"
SHEETS_API = "https://sheets.googleapis.com/v4/spreadsheets"


def _load_credentials() -> dict[str, Any]:
    """Load service account credentials from JSON file."""
    creds_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH", "./credentials/service-account.json")
    path = Path(creds_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Service account file not found: {creds_path}. "
            "Set GOOGLE_SERVICE_ACCOUNT_PATH in .env"
        )
    with open(path) as f:
        return json.load(f)


def _get_access_token() -> str:
    """Get OAuth2 access token for service account."""
    import time

    import jwt

    credentials = _load_credentials()
    now = int(time.time())

    payload = {
        "iss": credentials["client_email"],
        "scope": " ".join(SCOPES),
        "aud": TOKEN_URI,
        "iat": now,
        "exp": now + 3600,
    }

    signed_jwt = jwt.encode(
        payload,
        credentials["private_key"],
        algorithm="RS256",
    )

    response = httpx.post(
        TOKEN_URI,
        data={
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": signed_jwt,
        },
        timeout=30.0,
    )

    if response.status_code != 200:
        raise PermissionError(f"Failed to get access token: {response.text}")

    return response.json()["access_token"]


def _headers() -> dict[str, str]:
    """Get authorization headers for Sheets API."""
    token = _get_access_token()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


@mcp.tool()
def read_sheet(spreadsheet_id: str, range_name: str = "A1:Z1000") -> list[list[str]]:
    """Read values from a Google Sheet.

    Args:
        spreadsheet_id: The ID of the spreadsheet.
        range_name: Cell range in A1 notation. Defaults to "A1:Z1000".

    Returns:
        List of rows, each row is a list of cell values as strings.
    """
    url = f"{SHEETS_API}/{spreadsheet_id}/values/{range_name}"

    response = httpx.get(url, headers=_headers(), timeout=30.0)

    if response.status_code == 404:
        raise FileNotFoundError(f"Spreadsheet not found: {spreadsheet_id}")
    if response.status_code == 403:
        raise PermissionError(
            "Access denied. Share the spreadsheet with the service account email."
        )
    if response.status_code >= 400:
        raise RuntimeError(f"Sheets API error: {response.status_code} - {response.text}")

    return response.json().get("values", [])


@mcp.tool()
def write_sheet(
    spreadsheet_id: str,
    range_name: str,
    values: list[list[str]],
) -> str:
    """Write values to a Google Sheet.

    Args:
        spreadsheet_id: The ID of the spreadsheet.
        range_name: Cell range in A1 notation (e.g., "Sheet1!A1").
        values: List of rows to write, each row is a list of cell values.

    Returns:
        Confirmation message with updated range info.
    """
    url = f"{SHEETS_API}/{spreadsheet_id}/values/{range_name}"
    params = {"valueInputOption": "USER_ENTERED"}
    body = {"values": values}

    response = httpx.put(
        url,
        headers=_headers(),
        params=params,
        json=body,
        timeout=30.0,
    )

    if response.status_code >= 400:
        raise RuntimeError(f"Sheets API error: {response.status_code} - {response.text}")

    data = response.json()
    return f"Updated range: {data.get('updatedRange', range_name)}"


@mcp.tool()
def create_sheet(title: str) -> str:
    """Create a new Google Sheet.

    Args:
        title: The title of the new spreadsheet.

    Returns:
        The ID of the created spreadsheet.
    """
    body = {
        "properties": {
            "title": title,
        }
    }

    response = httpx.post(
        SHEETS_API,
        headers=_headers(),
        json=body,
        timeout=30.0,
    )

    if response.status_code >= 400:
        raise RuntimeError(f"Sheets API error: {response.status_code} - {response.text}")

    data = response.json()
    return data["spreadsheetId"]


if __name__ == "__main__":
    mcp.run()
