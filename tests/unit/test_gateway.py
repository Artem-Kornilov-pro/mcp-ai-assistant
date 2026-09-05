"""Unit tests for the MCP gateway."""

import os
from typing import Any

import pytest


@pytest.fixture(autouse=True)
def _clear_mcp_servers_env() -> None:
    """Ensure MCP_SERVERS doesn't leak between tests."""
    os.environ.pop("MCP_SERVERS", None)


class TestSelectServers:
    """Tests for _select_servers."""

    def test_default_selects_all(self) -> None:
        from src.gateway import SERVER_REGISTRY, _select_servers

        assert _select_servers("all") == sorted(SERVER_REGISTRY)

    def test_empty_selects_all(self) -> None:
        from src.gateway import SERVER_REGISTRY, _select_servers

        assert _select_servers("") == sorted(SERVER_REGISTRY)

    def test_subset(self) -> None:
        from src.gateway import _select_servers

        assert _select_servers("weather, currency") == ["weather", "currency"]

    def test_case_insensitive(self) -> None:
        from src.gateway import _select_servers

        assert _select_servers("WEATHER") == ["weather"]

    def test_unknown_server_raises(self) -> None:
        from src.gateway import _select_servers

        with pytest.raises(ValueError, match="Unknown server"):
            _select_servers("totally_bogus")


class TestBuildGateway:
    """Tests for build_gateway."""

    async def test_default_mounts_all_servers(self) -> None:
        from src.gateway import SERVER_REGISTRY, build_gateway

        gateway = build_gateway()
        tools = await gateway.list_tools()
        names = {t.name for t in tools}

        assert "weather_get_weather" in names
        assert "qr_generate_qr_code" in names
        assert len(names) >= 130
        assert len(SERVER_REGISTRY) == 25

    async def test_subset_selection(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.gateway import build_gateway

        monkeypatch.setenv("MCP_SERVERS", "weather,currency")
        gateway = build_gateway()
        names = {t.name for t in await gateway.list_tools()}

        assert any(name.startswith("weather_") for name in names)
        assert any(name.startswith("currency_") for name in names)
        assert not any(name.startswith("qr_") for name in names)

    def test_unknown_server_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.gateway import build_gateway

        monkeypatch.setenv("MCP_SERVERS", "totally_bogus")
        with pytest.raises(ValueError, match="Unknown server"):
            build_gateway()


class TestBearerAuthMiddleware:
    """Tests for BearerAuthMiddleware."""

    def _make_client(self, api_key: str) -> Any:
        from starlette.applications import Starlette
        from starlette.responses import PlainTextResponse
        from starlette.routing import Route
        from starlette.testclient import TestClient

        from src.gateway import BearerAuthMiddleware

        async def homepage(request: object) -> PlainTextResponse:
            return PlainTextResponse("ok")

        app = Starlette(routes=[Route("/", homepage)])
        app.add_middleware(BearerAuthMiddleware, api_key=api_key)
        return TestClient(app)

    def test_missing_token_rejected(self) -> None:
        client = self._make_client("secret123")
        response = client.get("/")
        assert response.status_code == 401

    def test_wrong_token_rejected(self) -> None:
        client = self._make_client("secret123")
        response = client.get("/", headers={"Authorization": "Bearer wrong"})
        assert response.status_code == 401

    def test_correct_token_allowed(self) -> None:
        client = self._make_client("secret123")
        response = client.get("/", headers={"Authorization": "Bearer secret123"})
        assert response.status_code == 200
        assert response.text == "ok"
