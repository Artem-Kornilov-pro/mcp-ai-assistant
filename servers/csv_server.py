"""MCP server for CSV file operations."""

import csv
import os
from pathlib import Path

from fastmcp import FastMCP

mcp = FastMCP("CSV")


def _resolve_path(path: str) -> Path:
    """Resolve path and enforce workspace boundary."""
    workspace = Path(os.getenv("WORKSPACE_DIR", "./workspace")).resolve()
    target = (workspace / path).resolve()
    try:
        target.relative_to(workspace)
    except ValueError:
        raise PermissionError(f"Access denied: '{path}' is outside workspace")
    return target


@mcp.tool()
def read_csv(path: str, limit: int = 100) -> str:
    """Read a CSV file.

    Args:
        path: Path to .csv file relative to workspace.
        limit: Max rows to read. Default: 100.

    Returns:
        Tab-separated table as text.
    """
    target = _resolve_path(path)
    if not target.exists():
        raise FileNotFoundError(f"File not found: {path}")

    lines: list[str] = []
    with open(target, encoding="utf-8") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i >= limit:
                lines.append(f"... ({limit} row limit reached)")
                break
            lines.append("\t".join(row))
    return "\n".join(lines)


@mcp.tool()
def write_csv(path: str, data: str) -> str:
    """Write data to a CSV file.

    Args:
        path: Path to .csv file relative to workspace.
        data: Tab-separated rows, newline-separated lines.

    Returns:
        Confirmation message.
    """
    target = _resolve_path(path)
    rows = [line.split("\t") for line in data.strip().split("\n")]

    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    return f"Written {len(rows)} rows to {path}"


@mcp.tool()
def csv_to_json(path: str) -> str:
    """Convert a CSV file to JSON.

    Args:
        path: Path to .csv file relative to workspace.

    Returns:
        JSON array of objects.
    """
    import json

    target = _resolve_path(path)
    if not target.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with open(target, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    return json.dumps(rows, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    mcp.run()
