"""LLM client abstraction for Yandex Cloud (OpenAI-compatible API)."""

import json
import time
from typing import Any

import httpx
from openai import OpenAI
from openai.types.responses import EasyInputMessageParam


class LLMError(Exception):
    """Base exception for LLM client errors."""


class LLMAuthError(LLMError):
    """Authentication error."""


class LLMRateLimitError(LLMError):
    """Rate limit exceeded."""


class LLMTimeoutError(LLMError):
    """Request timeout."""


class LLMClient:
    """Client for Yandex Cloud LLM with retry logic and tool calling."""

    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 2.0
    TIMEOUT: float = 30.0

    def __init__(
        self,
        api_key: str,
        folder_id: str,
        model: str = "deepseek-v4-flash/latest",
        temperature: float = 0.3,
        max_tokens: int = 2000,
        timeout: float | None = None,
    ) -> None:
        self._folder_id = folder_id
        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._timeout = timeout if timeout is not None else self.TIMEOUT

        self._client = OpenAI(
            api_key=api_key,
            base_url="https://ai.api.cloud.yandex.net/v1",
            project=folder_id,
            timeout=self._timeout,
        )

    @property
    def model_uri(self) -> str:
        """Full model URI for Yandex Cloud."""
        return f"gpt://{self._folder_id}/{self._model}"

    def _build_input(self, messages: list[dict[str, Any]]) -> list[EasyInputMessageParam]:
        """Convert raw message dicts to typed input for OpenAI SDK."""
        result: list[EasyInputMessageParam] = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if not isinstance(content, str):
                content = json.dumps(content, ensure_ascii=False)
            result.append(EasyInputMessageParam(role=role, content=content))  # type: ignore[arg-type]
        return result

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Send messages to LLM and return response with optional tool calls.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            tools: Optional list of tools in OpenAI function calling format.

        Returns:
            Dict with 'content' (str) and 'tool_calls' (list) keys.
        """
        last_error: Exception | None = None

        typed_input = self._build_input(messages)

        create_kwargs: dict[str, Any] = {
            "model": self.model_uri,
            "temperature": self._temperature,
            "instructions": "",
            "input": typed_input,
            "max_output_tokens": self._max_tokens,
        }

        if tools:
            create_kwargs["tools"] = tools

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                response = self._client.responses.create(**create_kwargs)  # type: ignore[arg-type]

                result: dict[str, Any] = {
                    "content": response.output_text,
                    "tool_calls": [],
                }

                # Extract tool calls from response
                output = getattr(response, "output", [])
                for item in output:
                    if hasattr(item, "type") and item.type == "function_call":
                        result["tool_calls"].append(
                            {
                                "id": getattr(item, "call_id", ""),
                                "name": item.name,
                                "arguments": json.loads(item.arguments)
                                if isinstance(item.arguments, str)
                                else item.arguments,
                            }
                        )

                return result

            except httpx.TimeoutException as exc:
                last_error = exc
                if attempt < self.MAX_RETRIES:
                    time.sleep(self.RETRY_DELAY * attempt)
                continue

            except Exception as exc:
                error_str = str(exc).lower()

                if "401" in error_str or "unauthorized" in error_str or "auth" in error_str:
                    raise LLMAuthError(f"Authentication failed: {exc}") from exc

                if "429" in error_str or "rate limit" in error_str:
                    if attempt < self.MAX_RETRIES:
                        time.sleep(self.RETRY_DELAY * attempt)
                        last_error = exc
                        continue
                    raise LLMRateLimitError(
                        f"Rate limit exceeded after {self.MAX_RETRIES} retries"
                    ) from exc

                if "timeout" in error_str:
                    raise LLMTimeoutError(f"Request timed out: {exc}") from exc

                raise LLMError(f"LLM API error: {exc}") from exc

        raise LLMTimeoutError(f"Request timed out after {self.MAX_RETRIES} retries") from last_error
