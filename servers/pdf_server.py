"""MCP server for PDF operations (pypdf, fpdf2)."""

import os
from pathlib import Path

from fastmcp import FastMCP

mcp = FastMCP("PDF")


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
def read_pdf(path: str, max_pages: int = 10) -> str:
    """Extract text from a PDF file.

    Args:
        path: Path to .pdf file relative to workspace.
        max_pages: Maximum pages to read. Default: 10.

    Returns:
        Extracted text from PDF.
    """
    from pypdf import PdfReader

    target = _resolve_path(path)
    if not target.exists():
        raise FileNotFoundError(f"File not found: {path}")

    reader = PdfReader(target)
    text_parts: list[str] = []
    pages = min(len(reader.pages), max_pages)

    for i in range(pages):
        page_text = reader.pages[i].extract_text()
        if page_text:
            text_parts.append(f"--- Page {i+1} ---\n{page_text}")

    return "\n\n".join(text_parts) if text_parts else "No text extracted."


@mcp.tool()
def pdf_info(path: str) -> str:
    """Get information about a PDF file.

    Args:
        path: Path to .pdf file relative to workspace.

    Returns:
        Page count, metadata, file size.
    """
    from pypdf import PdfReader

    target = _resolve_path(path)
    if not target.exists():
        raise FileNotFoundError(f"File not found: {path}")

    reader = PdfReader(target)
    info = reader.metadata
    size_kb = target.stat().st_size / 1024

    lines = [
        f"Pages: {len(reader.pages)}",
        f"Size: {size_kb:.1f} KB",
    ]
    if info:
        if info.get("/Title"):
            lines.append(f"Title: {info['/Title']}")
        if info.get("/Author"):
            lines.append(f"Author: {info['/Author']}")
        if info.get("/Subject"):
            lines.append(f"Subject: {info['/Subject']}")

    return "\n".join(lines)


@mcp.tool()
def create_pdf(path: str, text: str, title: str = "Document") -> str:
    """Create a new PDF file from text.

    Args:
        path: Output .pdf path relative to workspace.
        text: Text content for the PDF (ASCII only).
        title: Document title.

    Returns:
        Confirmation message.
    """
    from fpdf import FPDF

    target = _resolve_path(path)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_title(title)
    pdf.set_font("Helvetica", "", 12)

    page_width = pdf.w - 2 * pdf.l_margin

    for line in text.split("\n"):
        safe_line = line.encode("latin-1", errors="replace").decode("latin-1")
        pdf.multi_cell(w=page_width, h=8, text=safe_line)

    target.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(target))
    return f"PDF created: {path}"


if __name__ == "__main__":
    mcp.run()
    