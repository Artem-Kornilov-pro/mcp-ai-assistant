"""MCP server for linear barcode generation and decoding."""

import io
import os
from pathlib import Path

import barcode as barcode_lib
from barcode.writer import ImageWriter
from fastmcp import FastMCP
from PIL import Image

mcp = FastMCP("Barcode")


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
def list_barcode_types() -> str:
    """List barcode symbologies supported by generate_barcode.

    Returns:
        Comma-separated list of supported barcode type names.
    """
    return ", ".join(sorted(barcode_lib.PROVIDED_BARCODES))


@mcp.tool()
def generate_barcode(
    data: str, output: str, barcode_type: str = "code128", write_text: bool = True
) -> str:
    """Generate a linear barcode image.

    Args:
        data: Data to encode. Must match the format expected by barcode_type
            (e.g. 12-13 digits for 'ean13', 7 digits for 'ean8').
        output: Output image path relative to workspace.
        barcode_type: Barcode symbology, e.g. 'code128', 'ean13', 'ean8', 'upca',
            'code39', 'isbn13'. Use list_barcode_types for the full list. Default: 'code128'.
        write_text: Whether to print the human-readable data below the barcode. Default: True.

    Returns:
        Confirmation message.
    """
    if barcode_type not in barcode_lib.PROVIDED_BARCODES:
        raise ValueError(
            f"Unsupported barcode_type: {barcode_type}. "
            f"Use one of {sorted(barcode_lib.PROVIDED_BARCODES)}"
        )

    barcode_class = barcode_lib.get_barcode_class(barcode_type)
    try:
        instance = barcode_class(data, writer=ImageWriter())
    except Exception as e:
        raise ValueError(f"Invalid data for barcode type '{barcode_type}': {e}") from e

    buffer = io.BytesIO()
    instance.write(buffer, options={"write_text": write_text})
    buffer.seek(0)

    dest = _resolve_path(output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    Image.open(buffer).convert("RGB").save(dest)

    return f"Barcode saved: {output}"


@mcp.tool()
def batch_generate_barcode(items: str, output_dir: str, barcode_type: str = "code128") -> str:
    """Generate multiple barcodes of the same type at once.

    Args:
        items: ';'-separated "filename.png:data" pairs.
        output_dir: Output directory relative to workspace.
        barcode_type: Barcode symbology for all items. Default: 'code128'.

    Returns:
        Confirmation message with the number of barcodes generated.
    """
    entries = [e.strip() for e in items.split(";") if e.strip()]
    if not entries:
        raise ValueError("No items provided")

    count = 0
    for entry in entries:
        if ":" not in entry:
            raise ValueError(f"Invalid item format: '{entry}'. Use 'filename.png:data'")
        filename, data = entry.split(":", 1)
        generate_barcode(data, str(Path(output_dir) / filename.strip()), barcode_type=barcode_type)
        count += 1

    return f"Generated {count} barcode(s) in {output_dir}"


@mcp.tool()
def read_barcode(path: str) -> str:
    """Detect and decode barcode(s) from an image.

    Args:
        path: Path to image file relative to workspace.

    Returns:
        Decoded barcode(s) as "type: data", one per line.
    """
    target = _resolve_path(path)
    if not target.exists():
        raise FileNotFoundError(f"File not found: {path}")

    from pyzbar.pyzbar import decode as zbar_decode

    with Image.open(target) as img:
        results = zbar_decode(img)

    if not results:
        raise ValueError(f"No barcode detected in image: {path}")

    return "\n".join(f"{r.type}: {r.data.decode('utf-8')}" for r in results)


if __name__ == "__main__":
    mcp.run()
