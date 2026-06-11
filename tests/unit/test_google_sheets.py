"""Unit tests for Google Sheets MCP server."""

import os
from unittest.mock import MagicMock, patch

import pytest

os.environ["GOOGLE_SERVICE_ACCOUNT_PATH"] = "./credentials/test-service-account.json"


class TestReadSheet:
    """Tests for read_sheet tool."""

    def test_read_returns_values(self) -> None:
        from servers.google_sheets import read_sheet

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "values": [["Name", "Age"], ["Alice", "30"]],
        }

        with patch("servers.google_sheets.httpx.get", return_value=mock_response):
            with patch("servers.google_sheets._headers", return_value={}):
                result = read_sheet("spreadsheet123", "Sheet1!A1:B10")
                assert result == [["Name", "Age"], ["Alice", "30"]]

    def test_read_empty_sheet(self) -> None:
        from servers.google_sheets import read_sheet

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}

        with patch("servers.google_sheets.httpx.get", return_value=mock_response):
            with patch("servers.google_sheets._headers", return_value={}):
                result = read_sheet("spreadsheet123")
                assert result == []

    def test_read_not_found(self) -> None:
        from servers.google_sheets import read_sheet

        mock_response = MagicMock()
        mock_response.status_code = 404

        with patch("servers.google_sheets.httpx.get", return_value=mock_response):
            with patch("servers.google_sheets._headers", return_value={}):
                with pytest.raises(FileNotFoundError, match="Spreadsheet not found"):
                    read_sheet("invalid_id")

    def test_read_forbidden(self) -> None:
        from servers.google_sheets import read_sheet

        mock_response = MagicMock()
        mock_response.status_code = 403

        with patch("servers.google_sheets.httpx.get", return_value=mock_response):
            with patch("servers.google_sheets._headers", return_value={}):
                with pytest.raises(PermissionError, match="Access denied"):
                    read_sheet("no_access_id")


class TestWriteSheet:
    """Tests for write_sheet tool."""

    def test_write_returns_updated_range(self) -> None:
        from servers.google_sheets import write_sheet

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"updatedRange": "Sheet1!A1:B2"}

        with patch("servers.google_sheets.httpx.put", return_value=mock_response):
            with patch("servers.google_sheets._headers", return_value={}):
                result = write_sheet(
                    "spreadsheet123",
                    "Sheet1!A1",
                    [["Name", "Age"], ["Bob", "25"]],
                )
                assert "Sheet1!A1:B2" in result

    def test_write_api_error(self) -> None:
        from servers.google_sheets import write_sheet

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad request"

        with patch("servers.google_sheets.httpx.put", return_value=mock_response):
            with patch("servers.google_sheets._headers", return_value={}):
                with pytest.raises(RuntimeError, match="Sheets API error"):
                    write_sheet("spreadsheet123", "Sheet1!A1", [["data"]])


class TestCreateSheet:
    """Tests for create_sheet tool."""

    def test_create_returns_spreadsheet_id(self) -> None:
        from servers.google_sheets import create_sheet

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"spreadsheetId": "new-id-123"}

        with patch("servers.google_sheets.httpx.post", return_value=mock_response):
            with patch("servers.google_sheets._headers", return_value={}):
                result = create_sheet("My New Sheet")
                assert result == "new-id-123"

    def test_create_api_error(self) -> None:
        from servers.google_sheets import create_sheet

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal error"

        with patch("servers.google_sheets.httpx.post", return_value=mock_response):
            with patch("servers.google_sheets._headers", return_value={}):
                with pytest.raises(RuntimeError, match="Sheets API error"):
                    create_sheet("Bad Sheet")
