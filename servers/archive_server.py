"""MCP server for ZIP archive operations."""

import os
import zipfile
from pathlib import Path

from fastmcp import FastMCP

mcp = FastMCP("Archive")


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
def zip_files(paths: str, output: str) -> str:
    """Pack one or more files into a ZIP archive.

    Args:
        paths: Comma-separated file paths relative to workspace.
        output: Output .zip path relative to workspace.

    Returns:
        Confirmation message.
    """
    file_paths = [p.strip() for p in paths.split(",") if p.strip()]
    target = _resolve_path(output)
    target.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in file_paths:
            source = _resolve_path(file_path)
            if not source.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            zf.write(source, arcname=source.name)

    return f"Zipped {len(file_paths)} file(s) into {output}"


@mcp.tool()
def unzip_file(path: str, output_dir: str) -> str:
    """Extract a ZIP archive into a directory.

    Args:
        path: Path to .zip file relative to workspace.
        output_dir: Target directory relative to workspace.

    Returns:
        Confirmation message with number of extracted files.
    """
    target = _resolve_path(path)
    if not target.exists():
        raise FileNotFoundError(f"File not found: {path}")

    dest = _resolve_path(output_dir)
    dest.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(target) as zf:
        for member in zf.namelist():
            member_path = (dest / member).resolve()
            if not str(member_path).startswith(str(dest)):
                raise PermissionError(f"Unsafe path in archive: {member}")
        names = zf.namelist()
        zf.extractall(dest)

    return f"Extracted {len(names)} file(s) to {output_dir}"


@mcp.tool()
def list_archive(path: str) -> str:
    """List the contents of a ZIP archive.

    Args:
        path: Path to .zip file relative to workspace.

    Returns:
        Tab-separated list of file names and sizes (KB).
    """
    target = _resolve_path(path)
    if not target.exists():
        raise FileNotFoundError(f"File not found: {path}")

    lines: list[str] = []
    with zipfile.ZipFile(target) as zf:
        for info in zf.infolist():
            size_kb = info.file_size / 1024
            lines.append(f"{info.filename}\t{size_kb:.1f} KB")

    return "\n".join(lines) if lines else "Archive is empty."


if __name__ == "__main__":
    mcp.run()
