"""Unit tests for PDF MCP server."""

import os
from pathlib import Path

import pytest

os.environ["WORKSPACE_DIR"] = "./workspace"


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """Temp workspace."""
    ws = tmp_path / "workspace"
    ws.mkdir()
    os.environ["WORKSPACE_DIR"] = str(ws)
    return ws


class TestPDF:
    """Tests for PDF tools."""

    def test_create_and_read(self, workspace: Path) -> None:
        from servers.pdf_server import create_pdf, read_pdf

        create_pdf("test.pdf", "Hello World\nThis is a test.", title="Test Doc")
        assert (workspace / "test.pdf").exists()
        result = read_pdf("test.pdf")
        assert "Hello" in result
        assert "test" in result.lower()

    def test_pdf_info(self, workspace: Path) -> None:
        from servers.pdf_server import create_pdf, pdf_info

        create_pdf("info.pdf", "Content", title="My Title")
        result = pdf_info("info.pdf")
        assert "Pages" in result
        assert "KB" in result

    def test_read_nonexistent(self, workspace: Path) -> None:
        from servers.pdf_server import read_pdf

        with pytest.raises(FileNotFoundError, match="File not found"):
            read_pdf("missing.pdf")

    def test_outside_workspace(self, workspace: Path) -> None:
        from servers.pdf_server import read_pdf

        with pytest.raises(PermissionError, match="Access denied"):
            read_pdf("../outside.pdf")
            