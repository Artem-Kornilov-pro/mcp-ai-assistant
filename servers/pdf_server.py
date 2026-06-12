"""MCP server for PDF operations (fpdf2 create, PyMuPDF read)."""

import os
from pathlib import Path

import fitz  # PyMuPDF
from fastmcp import FastMCP

mcp = FastMCP("PDF")

_FONT_PATH: Path | None = None


def _get_font_path() -> Path | None:
    """Find a Unicode-capable TTF font."""
    global _FONT_PATH

    if _FONT_PATH is not None and _FONT_PATH.exists():
        return _FONT_PATH

    candidates = [
        Path("C:/Windows/Fonts/arial.ttf"),           # Windows (Arial)
        Path("C:/Windows/Fonts/DejaVuSans.ttf"),      # Windows (DejaVu if present)
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),  # Linux
        Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),  # Linux alt
        Path("/Library/Fonts/Arial.ttf"),             # macOS
        Path("/Library/Fonts/DejaVuSans.ttf"),        # macOS alt
    ]

    for fp in candidates:
        if fp.exists():
            _FONT_PATH = fp
            return fp

    return None


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
    """Extract text from a PDF file (PyMuPDF). Handles Unicode.

    Args:
        path: Path to .pdf file relative to workspace.
        max_pages: Maximum pages to read. Default: 10.

    Returns:
        Extracted text from PDF.
    """
    target = _resolve_path(path)
    if not target.exists():
        raise FileNotFoundError(f"File not found: {path}")

    doc = fitz.open(target)
    text_parts: list[str] = []
    pages = min(len(doc), max_pages)

    for i in range(pages):
        page = doc[i]
        page_text = page.get_text()
        if page_text.strip():
            text_parts.append(f"--- Page {i+1} ---\n{page_text.strip()}")

    doc.close()
    return "\n\n".join(text_parts) if text_parts else "No text extracted."


@mcp.tool()
def pdf_info(path: str) -> str:
    """Get information about a PDF file.

    Args:
        path: Path to .pdf file relative to workspace.

    Returns:
        Page count, metadata, file size.
    """
    target = _resolve_path(path)
    if not target.exists():
        raise FileNotFoundError(f"File not found: {path}")

    doc = fitz.open(target)
    size_kb = target.stat().st_size / 1024
    meta = doc.metadata
    lines = [
        f"Pages: {len(doc)}",
        f"Size: {size_kb:.1f} KB",
    ]
    if meta:
        if meta.get("title"):
            lines.append(f"Title: {meta['title']}")
        if meta.get("author"):
            lines.append(f"Author: {meta['author']}")
        if meta.get("subject"):
            lines.append(f"Subject: {meta['subject']}")

    doc.close()
    return "\n".join(lines)


@mcp.tool()
def create_pdf(path: str, text: str, title: str = "Document") -> str:
    """Create a new PDF file from text with full Unicode/Cyrillic support.

    Args:
        path: Output .pdf path relative to workspace.
        text: Text content for the PDF.
        title: Document title.

    Returns:
        Confirmation message.
    """
    from fpdf import FPDF

    target = _resolve_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_title(title)

    font_path = _get_font_path()
    if font_path:
        pdf.add_font("UniFont", "", str(font_path), uni=True)
        pdf.set_font("UniFont", "", 12)
    else:
        pdf.set_font("Helvetica", "", 12)

    page_width = pdf.w - 2 * pdf.l_margin

    for line in text.split("\n"):
        if font_path:
            pdf.multi_cell(w=page_width, h=8, text=line)
        else:
            safe_line = line.encode("latin-1", errors="replace").decode("latin-1")
            pdf.multi_cell(w=page_width, h=8, text=safe_line)

    pdf.output(str(target))
    return f"PDF created: {path}"


if __name__ == "__main__":
    mcp.run()
    