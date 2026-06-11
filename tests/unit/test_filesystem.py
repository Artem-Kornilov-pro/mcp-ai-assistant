"""Unit tests for filesystem MCP server."""

import os
from pathlib import Path

import pytest

os.environ["WORKSPACE_DIR"] = "./workspace"


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """Create isolated workspace for tests."""
    ws = tmp_path / "workspace"
    ws.mkdir()
    os.environ["WORKSPACE_DIR"] = str(ws)
    return ws


@pytest.fixture
def sample_file(workspace: Path) -> Path:
    """Create a sample file in workspace."""
    f = workspace / "test.txt"
    f.write_text("Hello, World!", encoding="utf-8")
    return f


class TestResolvePath:
    """Tests for path resolution and security."""

    def test_inside_workspace(self, workspace: Path) -> None:
        from servers.filesystem import _resolve_path

        result = _resolve_path("test.txt")
        assert result == (workspace / "test.txt").resolve()

    def test_outside_workspace_raises(self, workspace: Path) -> None:
        from servers.filesystem import _resolve_path

        with pytest.raises(PermissionError, match="Access denied"):
            _resolve_path("../etc/passwd")

    def test_absolute_path_outside_raises(self, workspace: Path) -> None:
        from servers.filesystem import _resolve_path

        with pytest.raises(PermissionError, match="Access denied"):
            _resolve_path("/etc/passwd")


class TestReadFile:
    """Tests for read_file tool."""

    def test_read_existing_file(self, workspace: Path, sample_file: Path) -> None:
        from servers.filesystem import read_file

        result = read_file("test.txt")
        assert result == "Hello, World!"

    def test_read_nonexistent_file(self, workspace: Path) -> None:
        from servers.filesystem import read_file

        with pytest.raises(FileNotFoundError, match="File not found"):
            read_file("missing.txt")

    def test_read_directory_as_file(self, workspace: Path) -> None:
        from servers.filesystem import read_file

        (workspace / "subdir").mkdir()
        with pytest.raises(ValueError, match="Not a file"):
            read_file("subdir")


class TestWriteFile:
    """Tests for write_file tool."""

    def test_write_new_file(self, workspace: Path) -> None:
        from servers.filesystem import write_file

        result = write_file("output.txt", "test content")
        assert "File written" in result
        assert (workspace / "output.txt").read_text() == "test content"

    def test_write_creates_directories(self, workspace: Path) -> None:
        from servers.filesystem import write_file

        write_file("deep/nested/file.txt", "nested content")
        assert (workspace / "deep" / "nested" / "file.txt").read_text() == "nested content"

    def test_write_outside_workspace(self, workspace: Path) -> None:
        from servers.filesystem import write_file

        with pytest.raises(PermissionError, match="Access denied"):
            write_file("../outside.txt", "should fail")


class TestListDirectory:
    """Tests for list_directory tool."""

    def test_list_empty_directory(self, workspace: Path) -> None:
        from servers.filesystem import list_directory

        result = list_directory(".")
        assert result == []

    def test_list_with_files_and_dirs(self, workspace: Path) -> None:
        from servers.filesystem import list_directory

        (workspace / "file1.txt").touch()
        (workspace / "file2.txt").touch()
        (workspace / "subdir").mkdir()

        result = list_directory(".")
        assert "file1.txt" in result
        assert "file2.txt" in result
        assert "subdir/" in result

    def test_list_nonexistent_directory(self, workspace: Path) -> None:
        from servers.filesystem import list_directory

        with pytest.raises(FileNotFoundError, match="Directory not found"):
            list_directory("nonexistent")

    def test_list_file_as_directory(self, workspace: Path, sample_file: Path) -> None:
        from servers.filesystem import list_directory

        with pytest.raises(ValueError, match="Not a directory"):
            list_directory("test.txt")


class TestSearchFiles:
    """Tests for search_files tool."""

    def test_search_by_pattern(self, workspace: Path) -> None:
        from servers.filesystem import search_files

        (workspace / "a.py").touch()
        (workspace / "b.py").touch()
        (workspace / "c.txt").touch()

        result = search_files("*.py")
        assert "a.py" in result
        assert "b.py" in result
        assert "c.txt" not in result

    def test_search_recursive(self, workspace: Path) -> None:
        from servers.filesystem import search_files

        sub = workspace / "sub"
        sub.mkdir()
        (sub / "deep.py").touch()

        result = search_files("*.py")
        # Нормализуем разделители для кроссплатформенности
        normalized = [p.replace("\\", "/") for p in result]
        assert "sub/deep.py" in normalized

    def test_search_no_matches(self, workspace: Path) -> None:
        from servers.filesystem import search_files

        result = search_files("*.nonexistent")
        assert result == []

    def test_search_workspace_created(self, workspace: Path) -> None:
        from servers.filesystem import search_files

        # workspace already exists, should not crash
        result = search_files("*.py")
        assert isinstance(result, list)
