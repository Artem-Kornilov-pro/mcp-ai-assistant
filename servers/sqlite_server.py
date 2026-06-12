"""MCP server for SQLite database operations."""

import os
import sqlite3
from pathlib import Path

from fastmcp import FastMCP

mcp = FastMCP("SQLite")

DB_NAME = "assistant.db"


def _get_db_path() -> Path:
    """Get database path inside workspace."""
    workspace = Path(os.getenv("WORKSPACE_DIR", "./workspace"))
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace / DB_NAME


def _get_connection() -> sqlite3.Connection:
    """Get a connection to the SQLite database."""
    db_path = _get_db_path()
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


@mcp.tool()
def execute_query(query: str) -> str:
    """Execute a SELECT query on the local SQLite database.

    Args:
        query: SQL SELECT query.

    Returns:
        Results as formatted string.
    """
    conn = _get_connection()
    try:
        cursor = conn.execute(query)
        rows = cursor.fetchall()
        if not rows:
            return "No results."
        columns = [desc[0] for desc in cursor.description]
        lines = [", ".join(columns)]
        for row in rows:
            lines.append(", ".join(str(val) for val in row))
        return "\n".join(lines)
    except Exception as e:
        raise RuntimeError(f"Query error: {e}") from e
    finally:
        conn.close()


@mcp.tool()
def execute_statement(statement: str) -> str:
    """Execute INSERT, UPDATE, DELETE, or CREATE statement.

    Args:
        statement: SQL statement.

    Returns:
        Confirmation message with number of affected rows.
    """
    conn = _get_connection()
    try:
        cursor = conn.execute(statement)
        conn.commit()
        return f"Statement executed. Affected rows: {cursor.rowcount}."
    except Exception as e:
        raise RuntimeError(f"Statement error: {e}") from e
    finally:
        conn.close()


@mcp.tool()
def list_tables() -> str:
    """List all tables in the database.

    Returns:
        Formatted list of table names.
    """
    conn = _get_connection()
    try:
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        if not tables:
            return "No tables in database."
        return "Tables:\n" + "\n".join(f"- {t}" for t in tables)
    except Exception as e:
        raise RuntimeError(f"Query error: {e}") from e
    finally:
        conn.close()


if __name__ == "__main__":
    mcp.run()
