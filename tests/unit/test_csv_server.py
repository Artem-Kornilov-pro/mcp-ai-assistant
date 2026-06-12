"""Unit tests for CSV MCP server."""

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


class TestCSV:
    """Tests for CSV tools."""

    def test_write_and_read(self, workspace: Path) -> None:
        from servers.csv_server import read_csv, write_csv

        write_csv("test.csv", "Name\tAge\nAlice\t30\nBob\t25")
        result = read_csv("test.csv")
        assert "Alice" in result
        assert "30" in result

    def test_read_limit(self, workspace: Path) -> None:
        from servers.csv_server import read_csv, write_csv

        write_csv("big.csv", "\n".join(f"row{i}" for i in range(200)))
        result = read_csv("big.csv", limit=5)
        assert "limit" in result
        assert "row0" in result

    def test_read_nonexistent(self, workspace: Path) -> None:
        from servers.csv_server import read_csv

        with pytest.raises(FileNotFoundError, match="File not found"):
            read_csv("missing.csv")

    def test_outside_workspace(self, workspace: Path) -> None:
        from servers.csv_server import read_csv

        with pytest.raises(PermissionError, match="Access denied"):
            read_csv("../outside.csv")

    def test_csv_to_json(self, workspace: Path) -> None:
        from servers.csv_server import csv_to_json, write_csv

        write_csv("data.csv", "Name\tAge\nAlice\t30")
        result = csv_to_json("data.csv")
        assert "Alice" in result
        assert "30" in result
        assert '"Name"' in result
