"""Unit tests for Translate MCP server."""

from unittest.mock import MagicMock, patch

import pytest


class TestDetectLanguage:
    """Tests for detect_language tool."""

    def test_russian(self) -> None:
        from servers.translate_server import detect_language

        result = detect_language("Это длинный текст на русском языке для проверки.")
        assert result.startswith("ru")
        assert "confidence" in result

    def test_english(self) -> None:
        from servers.translate_server import detect_language

        result = detect_language("This is a fairly long piece of English text for testing.")
        assert result.startswith("en")

    def test_empty_text(self) -> None:
        from servers.translate_server import detect_language

        with pytest.raises(ValueError, match="Could not detect language"):
            detect_language("")


class TestTranslateText:
    """Tests for translate_text tool."""

    def test_explicit_source_lang(self) -> None:
        from servers.translate_server import translate_text

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "responseData": {"translatedText": "Привет, мир!"},
            "responseStatus": 200,
        }

        with patch("servers.translate_server.httpx.get", return_value=mock_response) as mock_get:
            result = translate_text("Hello, world!", target_lang="ru", source_lang="en")
            assert result == "Привет, мир!"
            args, kwargs = mock_get.call_args
            assert kwargs["params"]["langpair"] == "en|ru"

    def test_auto_detect_source(self) -> None:
        from servers.translate_server import translate_text

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "responseData": {"translatedText": "Hello, world!"},
            "responseStatus": 200,
        }

        with patch("servers.translate_server.httpx.get", return_value=mock_response) as mock_get:
            result = translate_text(
                "Это длинный текст на русском языке для проверки.", target_lang="en"
            )
            assert result == "Hello, world!"
            args, kwargs = mock_get.call_args
            assert kwargs["params"]["langpair"].startswith("ru|")

    def test_api_http_error(self) -> None:
        from servers.translate_server import translate_text

        mock_response = MagicMock()
        mock_response.status_code = 500

        with patch("servers.translate_server.httpx.get", return_value=mock_response):
            with pytest.raises(RuntimeError, match="Translation API error"):
                translate_text("Hello", target_lang="ru", source_lang="en")

    def test_api_response_error(self) -> None:
        from servers.translate_server import translate_text

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "responseStatus": 403,
            "responseDetails": "QUOTA EXCEEDED",
        }

        with patch("servers.translate_server.httpx.get", return_value=mock_response):
            with pytest.raises(RuntimeError, match="Translation failed"):
                translate_text("Hello", target_lang="ru", source_lang="en")
