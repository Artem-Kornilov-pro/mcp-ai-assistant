"""MCP server for filesystem operations."""

import os
from pathlib import Path

from fastmcp import FastMCP

mcp = FastMCP("Filesystem")


def _resolve_path(path: str) -> Path:
    """Resolve path and enforce workspace boundary."""
    workspace = Path(os.getenv("WORKSPACE_DIR", "./workspace")).resolve()
    target = (workspace / path).resolve()

    # Ensure target is inside workspace
    try:
        target.relative_to(workspace)
    except ValueError:
        raise PermissionError(f"Access denied: '{path}' is outside workspace")

    return target


@mcp.tool()
def read_file(path: str) -> str:
    """Read contents of a file.

    Args:
        path: File path relative to workspace directory.
    """
    target = _resolve_path(path)

    if not target.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if not target.is_file():
        raise ValueError(f"Not a file: {path}")

    return target.read_text(encoding="utf-8")


@mcp.tool()
def write_file(path: str, content: str) -> str:
    """Write content to a file. Creates directories if needed.

    Args:
        path: File path relative to workspace directory.
        content: Text content to write.
    """
    target = _resolve_path(path)

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")

    return f"File written: {path} ({len(content)} bytes)"


@mcp.tool()
def list_directory(path: str = ".") -> list[str]:
    """List files and directories in a folder.

    Args:
        path: Directory path relative to workspace. Defaults to root.
    """
    target = _resolve_path(path)

    if not target.exists():
        raise FileNotFoundError(f"Directory not found: {path}")

    if not target.is_dir():
        raise ValueError(f"Not a directory: {path}")

    items: list[str] = []
    for item in sorted(target.iterdir()):
        suffix = "/" if item.is_dir() else ""
        items.append(f"{item.name}{suffix}")

    return items


@mcp.tool()
def search_files(pattern: str) -> list[str]:
    """Search for files by name pattern recursively.

    Args:
        pattern: File name pattern (e.g., "*.py", "*.md").
    """
    workspace = Path(os.getenv("WORKSPACE_DIR", "./workspace")).resolve()
    workspace.mkdir(parents=True, exist_ok=True)

    matches: list[str] = []
    for match in workspace.rglob(pattern):
        if match.is_file():
            matches.append(str(match.relative_to(workspace)))

    return sorted(matches)


if __name__ == "__main__":
    mcp.run()
    