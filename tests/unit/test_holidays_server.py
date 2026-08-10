"""Unit tests for Holidays MCP server."""

from unittest.mock import MagicMock, patch

import pytest

_SAMPLE_HOLIDAYS = [
    {
        "date": "2026-01-01",
        "localName": "Новый год",
        "name": "New Year's Day",
        "countryCode": "RU",
    },
    {
        "date": "2026-05-09",
        "localName": "День Победы",
        "name": "Victory Day",
        "countryCode": "RU",
    },
]


def _mock_response(status_code: int, payload: object) -> MagicMock:
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.content = b"1" if payload else b""
    mock_response.json.return_value = payload
    return mock_response


class TestGetPublicHolidays:
    """Tests for get_public_holidays tool."""

    def test_returns_holidays(self) -> None:
        from servers.holidays_server import get_public_holidays

        mock_response = _mock_response(200, _SAMPLE_HOLIDAYS)
        with patch("servers.holidays_server.httpx.get", return_value=mock_response):
            result = get_public_holidays("RU", 2026)
            assert "2026-01-01" in result
            assert "Новый год" in result
            assert "Victory Day" in result

    def test_no_holidays(self) -> None:
        from servers.holidays_server import get_public_holidays

        mock_response = _mock_response(200, [])
        with patch("servers.holidays_server.httpx.get", return_value=mock_response):
            result = get_public_holidays("RU", 2026)
            assert "No public holidays found" in result

    def test_unknown_country(self) -> None:
        from servers.holidays_server import get_public_holidays

        mock_response = _mock_response(404, None)
        with patch("servers.holidays_server.httpx.get", return_value=mock_response):
            with pytest.raises(ValueError, match="Unknown country code"):
                get_public_holidays("ZZ", 2026)

    def test_api_error(self) -> None:
        from servers.holidays_server import get_public_holidays

        mock_response = _mock_response(500, None)
        with patch("servers.holidays_server.httpx.get", return_value=mock_response):
            with pytest.raises(RuntimeError, match="Holidays API error"):
                get_public_holidays("RU", 2026)


class TestIsPublicHoliday:
    """Tests for is_public_holiday tool."""

    def test_is_holiday(self) -> None:
        from servers.holidays_server import is_public_holiday

        mock_response = _mock_response(200, _SAMPLE_HOLIDAYS)
        with patch("servers.holidays_server.httpx.get", return_value=mock_response):
            result = is_public_holiday("RU", "2026-01-01")
            assert "is a public holiday" in result
            assert "Новый год" in result

    def test_is_not_holiday(self) -> None:
        from servers.holidays_server import is_public_holiday

        mock_response = _mock_response(200, _SAMPLE_HOLIDAYS)
        with patch("servers.holidays_server.httpx.get", return_value=mock_response):
            result = is_public_holiday("RU", "2026-06-15")
            assert "is not a public holiday" in result


class TestGetNextHolidays:
    """Tests for get_next_holidays tool."""

    def test_returns_upcoming(self) -> None:
        from servers.holidays_server import get_next_holidays

        mock_response = _mock_response(200, _SAMPLE_HOLIDAYS)
        with patch("servers.holidays_server.httpx.get", return_value=mock_response):
            result = get_next_holidays("RU")
            assert "2026-05-09" in result

    def test_no_upcoming(self) -> None:
        from servers.holidays_server import get_next_holidays

        mock_response = _mock_response(204, [])
        with patch("servers.holidays_server.httpx.get", return_value=mock_response):
            result = get_next_holidays("RU")
            assert "No upcoming public holidays" in result


class TestListHolidayCountries:
    """Tests for list_holiday_countries tool."""

    def test_returns_countries(self) -> None:
        from servers.holidays_server import list_holiday_countries

        mock_response = _mock_response(
            200, [{"countryCode": "RU", "name": "Russia"}, {"countryCode": "US", "name": "USA"}]
        )
        with patch("servers.holidays_server.httpx.get", return_value=mock_response):
            result = list_holiday_countries()
            assert "RU (Russia)" in result
            assert "US (USA)" in result
