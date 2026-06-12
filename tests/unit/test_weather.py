"""Unit tests for weather MCP server."""

from unittest.mock import MagicMock, patch

import pytest


class TestGetWeather:
    """Tests for get_weather tool."""

    def test_returns_weather(self) -> None:
        from servers.weather import get_weather

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Moscow: ☀️ +15°C"

        with patch("servers.weather.httpx.get", return_value=mock_response):
            result = get_weather("Moscow")
            assert "Moscow" in result
            assert "+15°C" in result

    def test_api_error(self) -> None:
        from servers.weather import get_weather

        mock_response = MagicMock()
        mock_response.status_code = 500

        with patch("servers.weather.httpx.get", return_value=mock_response):
            with pytest.raises(RuntimeError, match="Weather API error"):
                get_weather("InvalidCity")


class TestGetForecast:
    """Tests for get_forecast tool."""

    def test_returns_forecast(self) -> None:
        from servers.weather import get_forecast

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Forecast for 3 days"

        with patch("servers.weather.httpx.get", return_value=mock_response):
            result = get_forecast("London", days=3)
            assert "Forecast" in result
