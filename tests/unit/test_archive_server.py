"""Unit tests for Archive MCP server."""

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


class TestArchive:
    """Tests for Archive tools."""

    def test_zip_and_unzip(self, workspace: Path) -> None:
        from servers.archive_server import unzip_file, zip_files

        (workspace / "a.txt").write_text("hello")
        (workspace / "b.txt").write_text("world")

        result = zip_files("a.txt,b.txt", "out.zip")
        assert "2" in result
        assert (workspace / "out.zip").exists()

        result = unzip_file("out.zip", "extracted")
        assert "2" in result
        assert (workspace / "extracted" / "a.txt").read_text() == "hello"
        assert (workspace / "extracted" / "b.txt").read_text() == "world"

    def test_list_archive(self, workspace: Path) -> None:
        from servers.archive_server import list_archive, zip_files

        (workspace / "a.txt").write_text("hello")
        zip_files("a.txt", "out.zip")

        result = list_archive("out.zip")
        assert "a.txt" in result
        assert "KB" in result

    def test_zip_missing_file(self, workspace: Path) -> None:
        from servers.archive_server import zip_files

        with pytest.raises(FileNotFoundError, match="File not found"):
            zip_files("missing.txt", "out.zip")

    def test_unzip_nonexistent(self, workspace: Path) -> None:
        from servers.archive_server import unzip_file

        with pytest.raises(FileNotFoundError, match="File not found"):
            unzip_file("missing.zip", "extracted")

    def test_outside_workspace(self, workspace: Path) -> None:
        from servers.archive_server import zip_files

        with pytest.raises(PermissionError, match="Access denied"):
            zip_files("../outside.txt", "out.zip")

    def test_list_empty_archive(self, workspace: Path) -> None:
        import zipfile

        from servers.archive_server import list_archive

        with zipfile.ZipFile(workspace / "empty.zip", "w"):
            pass

        result = list_archive("empty.zip")
        assert result == "Archive is empty."
