"""MCP server for image processing operations (Pillow)."""

import os
from pathlib import Path

from fastmcp import FastMCP
from PIL import Image, ImageDraw, ImageFont

mcp = FastMCP("Image")

_FONT_PATH: Path | None = None


def _get_font_path() -> Path | None:
    """Find a Unicode-capable TTF font."""
    global _FONT_PATH

    if _FONT_PATH is not None and _FONT_PATH.exists():
        return _FONT_PATH

    candidates = [
        Path("C:/Windows/Fonts/arial.ttf"),  # Windows (Arial)
        Path("C:/Windows/Fonts/DejaVuSans.ttf"),  # Windows (DejaVu if present)
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),  # Linux
        Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),  # Linux alt
        Path("/Library/Fonts/Arial.ttf"),  # macOS
        Path("/Library/Fonts/DejaVuSans.ttf"),  # macOS alt
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
def get_image_info(path: str) -> str:
    """Get information about an image file.

    Args:
        path: Path to image file relative to workspace.

    Returns:
        Dimensions, format, color mode, and file size.
    """
    target = _resolve_path(path)
    if not target.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with Image.open(target) as img:
        width, height = img.size
        fmt = img.format or "unknown"
        mode = img.mode

    size_kb = target.stat().st_size / 1024
    return f"Dimensions: {width}x{height}\nFormat: {fmt}\nMode: {mode}\nSize: {size_kb:.1f} KB"


@mcp.tool()
def resize_image(path: str, width: int, height: int, output: str) -> str:
    """Resize an image to exact dimensions.

    Args:
        path: Path to source image relative to workspace.
        width: Target width in pixels.
        height: Target height in pixels.
        output: Output path relative to workspace.

    Returns:
        Confirmation message.
    """
    target = _resolve_path(path)
    if not target.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive")

    dest = _resolve_path(output)
    dest.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(target) as img:
        img.resize((width, height)).save(dest)

    return f"Resized to {width}x{height}: {output}"


@mcp.tool()
def crop_image(path: str, left: int, top: int, right: int, bottom: int, output: str) -> str:
    """Crop an image to a bounding box.

    Args:
        path: Path to source image relative to workspace.
        left: Left edge in pixels.
        top: Top edge in pixels.
        right: Right edge in pixels.
        bottom: Bottom edge in pixels.
        output: Output path relative to workspace.

    Returns:
        Confirmation message.
    """
    target = _resolve_path(path)
    if not target.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if left >= right or top >= bottom:
        raise ValueError("Invalid crop box: left < right and top < bottom required")

    dest = _resolve_path(output)
    dest.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(target) as img:
        img.crop((left, top, right, bottom)).save(dest)

    return f"Cropped to ({left},{top},{right},{bottom}): {output}"


@mcp.tool()
def rotate_image(path: str, degrees: float, output: str) -> str:
    """Rotate an image counter-clockwise by a given angle.

    Args:
        path: Path to source image relative to workspace.
        degrees: Rotation angle in degrees (counter-clockwise).
        output: Output path relative to workspace.

    Returns:
        Confirmation message.
    """
    target = _resolve_path(path)
    if not target.exists():
        raise FileNotFoundError(f"File not found: {path}")

    dest = _resolve_path(output)
    dest.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(target) as img:
        img.rotate(degrees, expand=True).save(dest)

    return f"Rotated {degrees}°: {output}"


@mcp.tool()
def convert_format(path: str, output: str) -> str:
    """Convert an image to a different format based on the output file extension.

    Args:
        path: Path to source image relative to workspace.
        output: Output path relative to workspace (extension determines format).

    Returns:
        Confirmation message.
    """
    target = _resolve_path(path)
    if not target.exists():
        raise FileNotFoundError(f"File not found: {path}")

    dest = _resolve_path(output)
    dest.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(target) as img:
        converted = img.convert("RGB") if dest.suffix.lower() in (".jpg", ".jpeg") else img
        converted.save(dest)

    return f"Converted to {dest.suffix.lstrip('.')}: {output}"


@mcp.tool()
def create_thumbnail(path: str, output: str, max_size: int = 128) -> str:
    """Create a thumbnail preserving aspect ratio.

    Args:
        path: Path to source image relative to workspace.
        output: Output path relative to workspace.
        max_size: Maximum width/height in pixels. Default: 128.

    Returns:
        Confirmation message with resulting dimensions.
    """
    target = _resolve_path(path)
    if not target.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if max_size <= 0:
        raise ValueError("max_size must be positive")

    dest = _resolve_path(output)
    dest.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(target) as img:
        img.thumbnail((max_size, max_size))
        img.save(dest)
        width, height = img.size

    return f"Thumbnail {width}x{height}: {output}"


@mcp.tool()
def add_watermark(path: str, text: str, output: str) -> str:
    """Add a text watermark to the bottom-right corner of an image.

    Args:
        path: Path to source image relative to workspace.
        text: Watermark text.
        output: Output path relative to workspace.

    Returns:
        Confirmation message.
    """
    target = _resolve_path(path)
    if not target.exists():
        raise FileNotFoundError(f"File not found: {path}")

    dest = _resolve_path(output)
    dest.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(target) as img:
        watermarked = img.convert("RGBA")
        draw = ImageDraw.Draw(watermarked)

        font_path = _get_font_path()
        font_size = max(12, watermarked.width // 20)
        font = (
            ImageFont.truetype(str(font_path), font_size) if font_path else ImageFont.load_default()
        )

        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        margin = 10
        position = (
            watermarked.width - text_width - margin,
            watermarked.height - text_height - margin,
        )
        draw.text(position, text, font=font, fill=(255, 255, 255, 180))

        if dest.suffix.lower() in (".jpg", ".jpeg"):
            watermarked = watermarked.convert("RGB")
        watermarked.save(dest)

    return f"Watermark added: {output}"


if __name__ == "__main__":
    mcp.run()
