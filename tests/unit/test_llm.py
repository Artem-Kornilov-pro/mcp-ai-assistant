"""Unit tests for LLM client."""

from unittest.mock import MagicMock, patch

import pytest

from src.llm import LLMAuthError, LLMClient, LLMError, LLMRateLimitError


@pytest.fixture
def client() -> LLMClient:
    return LLMClient(
        api_key="test-key",
        folder_id="test-folder",
        model="test-model/latest",
    )


@pytest.fixture
def sample_messages() -> list[dict[str, str]]:
    return [
        {"role": "user", "content": "Привет, как дела?"},
    ]


class TestLLMClient:
    """Tests for LLMClient."""

    def test_model_uri(self, client: LLMClient) -> None:
        assert client.model_uri == "gpt://test-folder/test-model/latest"

    def test_chat_success(self, client: LLMClient, sample_messages: list[dict[str, str]]) -> None:
        mock_response = MagicMock()
        mock_response.output_text = "Привет! У меня всё отлично."
        mock_response.output = []

        with patch.object(client, "_client") as mock_openai:
            mock_openai.responses.create.return_value = mock_response
            result = client.chat(sample_messages)

        assert result["content"] == "Привет! У меня всё отлично."
        assert result["tool_calls"] == []
        mock_openai.responses.create.assert_called_once()

    def test_chat_calls_with_correct_params(
        self, client: LLMClient, sample_messages: list[dict[str, str]]
    ) -> None:
        mock_response = MagicMock()
        mock_response.output_text = "OK"
        mock_response.output = []

        with patch.object(client, "_client") as mock_openai:
            mock_openai.responses.create.return_value = mock_response
            client.chat(sample_messages)

        call_kwargs = mock_openai.responses.create.call_args.kwargs
        assert call_kwargs["model"] == "gpt://test-folder/test-model/latest"
        assert call_kwargs["input"] == client._build_input(sample_messages)

    def test_raises_auth_error_on_401(
        self, client: LLMClient, sample_messages: list[dict[str, str]]
    ) -> None:
        with patch.object(client, "_client") as mock_openai:
            mock_openai.responses.create.side_effect = Exception("401 Unauthorized")

            with pytest.raises(LLMAuthError, match="Authentication failed"):
                client.chat(sample_messages)

    def test_retries_on_rate_limit(
        self, client: LLMClient, sample_messages: list[dict[str, str]]
    ) -> None:
        mock_success = MagicMock()
        mock_success.output_text = "Success after retry"
        mock_success.output = []

        with patch.object(client, "_client") as mock_openai:
            mock_openai.responses.create.side_effect = [
                Exception("429 rate limit"),
                mock_success,
            ]
            result = client.chat(sample_messages)

        assert result["content"] == "Success after retry"
        assert mock_openai.responses.create.call_count == 2

    def test_raises_rate_limit_after_max_retries(
        self, client: LLMClient, sample_messages: list[dict[str, str]]
    ) -> None:
        with patch.object(client, "_client") as mock_openai:
            mock_openai.responses.create.side_effect = Exception("429 rate limit")
            with patch("time.sleep", return_value=None):
                with pytest.raises(LLMRateLimitError, match="Rate limit exceeded"):
                    client.chat(sample_messages)

        assert mock_openai.responses.create.call_count == 3

    def test_raises_generic_error(
        self, client: LLMClient, sample_messages: list[dict[str, str]]
    ) -> None:
        with patch.object(client, "_client") as mock_openai:
            mock_openai.responses.create.side_effect = Exception("Something broke")

            with pytest.raises(LLMError, match="LLM API error"):
                client.chat(sample_messages)
