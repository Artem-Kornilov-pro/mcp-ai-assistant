"""Unit tests for SQLite MCP server."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

os.environ["WORKSPACE_DIR"] = "./workspace"


@pytest.fixture
def clean_db(tmp_path: Path) -> Path:
    """Use a temp database path."""
    ws = tmp_path / "workspace"
    ws.mkdir()
    db_path = ws / "assistant.db"
    with patch("servers.sqlite_server._get_db_path", return_value=db_path):
        yield db_path
    if db_path.exists():
        db_path.unlink()


class TestSqlite:
    """Tests for SQLite tools."""

    def test_create_table_and_list(self, clean_db: Path) -> None:
        from servers.sqlite_server import execute_statement, list_tables

        execute_statement("CREATE TABLE test (id INTEGER, name TEXT)")
        tables = list_tables()
        assert "test" in tables

    def test_insert_and_query(self, clean_db: Path) -> None:
        from servers.sqlite_server import execute_query, execute_statement

        execute_statement("CREATE TABLE users (id INTEGER, name TEXT)")
        execute_statement("INSERT INTO users VALUES (1, 'Alice')")
        execute_statement("INSERT INTO users VALUES (2, 'Bob')")

        result = execute_query("SELECT * FROM users ORDER BY id")
        assert "Alice" in result
        assert "Bob" in result

    def test_update(self, clean_db: Path) -> None:
        from servers.sqlite_server import execute_query, execute_statement

        execute_statement("CREATE TABLE items (id INTEGER, status TEXT)")
        execute_statement("INSERT INTO items VALUES (1, 'pending')")
        execute_statement("UPDATE items SET status = 'done' WHERE id = 1")

        result = execute_query("SELECT * FROM items")
        assert "done" in result

    def test_empty_table(self, clean_db: Path) -> None:
        from servers.sqlite_server import execute_query, execute_statement

        execute_statement("CREATE TABLE empty (x INTEGER)")
        result = execute_query("SELECT * FROM empty")
        assert "No results" in result

    def test_no_tables(self, clean_db: Path) -> None:
        from servers.sqlite_server import list_tables

        result = list_tables()
        assert "No tables" in result
