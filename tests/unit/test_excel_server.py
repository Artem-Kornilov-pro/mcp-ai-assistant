"""Unit tests for Excel MCP server."""

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


class TestExcel:
    """Tests for Excel tools."""

    def test_write_and_read(self, workspace: Path) -> None:
        from servers.excel_server import read_excel, write_excel

        write_excel("test.xlsx", "Name\tAge\nAlice\t30\nBob\t25")
        result = read_excel("test.xlsx")
        assert "Alice" in result
        assert "30" in result
        assert "Bob" in result

    def test_list_sheets(self, workspace: Path) -> None:
        from servers.excel_server import list_sheets, write_excel

        write_excel("multi.xlsx", "data", sheet="First")
        write_excel("multi.xlsx", "more", sheet="Second")
        result = list_sheets("multi.xlsx")
        assert "First" in result
        assert "Second" in result

    def test_read_nonexistent(self, workspace: Path) -> None:
        from servers.excel_server import read_excel

        with pytest.raises(FileNotFoundError, match="File not found"):
            read_excel("missing.xlsx")

    def test_outside_workspace(self, workspace: Path) -> None:
        from servers.excel_server import read_excel

        with pytest.raises(PermissionError, match="Access denied"):
            read_excel("../outside.xlsx")

    def test_csv_to_excel(self, workspace: Path) -> None:
        from servers.excel_server import csv_to_excel, read_excel

        csv_path = workspace / "data.csv"
        csv_path.write_text("X,Y\n1,2\n3,4", encoding="utf-8")

        csv_to_excel("data.csv", "out.xlsx")
        result = read_excel("out.xlsx")
        assert "1" in result
        assert "2" in result
        