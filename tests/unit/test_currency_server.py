"""Unit tests for Currency MCP server."""

from unittest.mock import MagicMock, patch

import pytest


def _mock_rates_response(rates: dict[str, float], date: str = "2026-08-09") -> MagicMock:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"base": "USD", "date": date, "rates": rates}
    return mock_response


class TestConvertCurrency:
    """Tests for convert_currency tool."""

    def test_basic_conversion(self) -> None:
        from servers.currency_server import convert_currency

        mock_response = _mock_rates_response({"RUB": 80.0, "EUR": 0.9})
        with patch("servers.currency_server.httpx.get", return_value=mock_response):
            result = convert_currency(100, "USD", "RUB")
            assert "8000.00 RUB" in result
            assert "rate: 80.0" in result

    def test_unsupported_target_currency(self) -> None:
        from servers.currency_server import convert_currency

        mock_response = _mock_rates_response({"RUB": 80.0})
        with patch("servers.currency_server.httpx.get", return_value=mock_response):
            with pytest.raises(ValueError, match="Unsupported currency code"):
                convert_currency(100, "USD", "ZZZ")

    def test_unsupported_base_currency(self) -> None:
        from servers.currency_server import convert_currency

        mock_response = MagicMock()
        mock_response.status_code = 404
        with patch("servers.currency_server.httpx.get", return_value=mock_response):
            with pytest.raises(ValueError, match="Unsupported currency code"):
                convert_currency(100, "BADCODE", "RUB")

    def test_api_error(self) -> None:
        from servers.currency_server import convert_currency

        mock_response = MagicMock()
        mock_response.status_code = 500
        with patch("servers.currency_server.httpx.get", return_value=mock_response):
            with pytest.raises(RuntimeError, match="Currency API error"):
                convert_currency(100, "USD", "RUB")


class TestGetExchangeRate:
    """Tests for get_exchange_rate tool."""

    def test_basic_rate(self) -> None:
        from servers.currency_server import get_exchange_rate

        mock_response = _mock_rates_response({"RUB": 94.5})
        with patch("servers.currency_server.httpx.get", return_value=mock_response):
            result = get_exchange_rate("EUR", "RUB")
            assert "1 EUR = 94.5 RUB" in result
            assert "2026-08-09" in result

    def test_unsupported_target_currency(self) -> None:
        from servers.currency_server import get_exchange_rate

        mock_response = _mock_rates_response({"RUB": 80.0})
        with patch("servers.currency_server.httpx.get", return_value=mock_response):
            with pytest.raises(ValueError, match="Unsupported currency code"):
                get_exchange_rate("USD", "ZZZ")


class TestListCurrencies:
    """Tests for list_currencies tool."""

    def test_includes_common_currencies(self) -> None:
        from servers.currency_server import list_currencies

        mock_response = _mock_rates_response({"RUB": 80.0, "EUR": 0.9})
        with patch("servers.currency_server.httpx.get", return_value=mock_response):
            result = list_currencies()
            assert "RUB" in result
            assert "EUR" in result
            assert "USD" in result
