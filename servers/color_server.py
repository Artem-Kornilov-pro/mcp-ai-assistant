"""MCP server for color conversion and manipulation utilities."""

from fastmcp import FastMCP

mcp = FastMCP("Color")


def _parse_hex(hex_color: str) -> tuple[int, int, int]:
    """Parse a '#rrggbb' or 'rrggbb' string into an (r, g, b) tuple."""
    value = hex_color.strip().lstrip("#")
    if len(value) != 6:
        raise ValueError(f"Invalid hex color: {hex_color!r}. Expected format '#rrggbb'")
    try:
        return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)
    except ValueError as e:
        raise ValueError(f"Invalid hex color: {hex_color!r}. Expected format '#rrggbb'") from e


def _format_hex(r: int, g: int, b: int) -> str:
    """Format an (r, g, b) tuple as a '#rrggbb' string, clamping to 0-255."""
    r, g, b = (max(0, min(255, round(c))) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


def _rgb_to_hsl(r: int, g: int, b: int) -> tuple[float, float, float]:
    """Convert 0-255 RGB to (hue in [0, 360), saturation/lightness in [0, 1])."""
    rf, gf, bf = r / 255, g / 255, b / 255
    max_c, min_c = max(rf, gf, bf), min(rf, gf, bf)
    lightness = (max_c + min_c) / 2

    if max_c == min_c:
        return 0.0, 0.0, lightness

    d = max_c - min_c
    saturation = d / (2 - max_c - min_c) if lightness > 0.5 else d / (max_c + min_c)

    if max_c == rf:
        hue = (gf - bf) / d + (6 if gf < bf else 0)
    elif max_c == gf:
        hue = (bf - rf) / d + 2
    else:
        hue = (rf - gf) / d + 4

    return hue * 60, saturation, lightness


def _hsl_to_rgb(hue: float, saturation: float, lightness: float) -> tuple[int, int, int]:
    """Convert hue in [0, 360), saturation/lightness in [0, 1] to 0-255 RGB."""
    c = (1 - abs(2 * lightness - 1)) * saturation
    x = c * (1 - abs((hue / 60) % 2 - 1))
    m = lightness - c / 2

    if hue < 60:
        r1, g1, b1 = c, x, 0.0
    elif hue < 120:
        r1, g1, b1 = x, c, 0.0
    elif hue < 180:
        r1, g1, b1 = 0.0, c, x
    elif hue < 240:
        r1, g1, b1 = 0.0, x, c
    elif hue < 300:
        r1, g1, b1 = x, 0.0, c
    else:
        r1, g1, b1 = c, 0.0, x

    return round((r1 + m) * 255), round((g1 + m) * 255), round((b1 + m) * 255)


@mcp.tool()
def hex_to_rgb(hex_color: str) -> str:
    """Convert a hex color to RGB.

    Args:
        hex_color: Color in '#rrggbb' or 'rrggbb' format.

    Returns:
        "r, g, b" with each channel 0-255.
    """
    r, g, b = _parse_hex(hex_color)
    return f"{r}, {g}, {b}"


@mcp.tool()
def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB values to a hex color.

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).

    Returns:
        Color in '#rrggbb' format.
    """
    return _format_hex(r, g, b)


@mcp.tool()
def hex_to_hsl(hex_color: str) -> str:
    """Convert a hex color to HSL.

    Args:
        hex_color: Color in '#rrggbb' or 'rrggbb' format.

    Returns:
        "h, s%, l%" — hue in degrees, saturation and lightness in percent.
    """
    r, g, b = _parse_hex(hex_color)
    h, s, lightness = _rgb_to_hsl(r, g, b)
    return f"{h:.0f}, {s * 100:.0f}%, {lightness * 100:.0f}%"


@mcp.tool()
def get_contrast_color(hex_color: str) -> str:
    """Pick a readable text color (black or white) for a given background color.

    Uses the WCAG relative luminance formula.

    Args:
        hex_color: Background color in '#rrggbb' or 'rrggbb' format.

    Returns:
        "black" or "white".
    """
    r, g, b = _parse_hex(hex_color)

    def channel_luminance(c: int) -> float:
        c_norm = c / 255
        return c_norm / 12.92 if c_norm <= 0.03928 else ((c_norm + 0.055) / 1.055) ** 2.4

    luminance = (
        0.2126 * channel_luminance(r)
        + 0.7152 * channel_luminance(g)
        + 0.0722 * channel_luminance(b)
    )
    return "black" if luminance > 0.179 else "white"


@mcp.tool()
def lighten_color(hex_color: str, amount: float) -> str:
    """Lighten a color by a percentage of the lightness range.

    Args:
        hex_color: Color in '#rrggbb' or 'rrggbb' format.
        amount: Percentage points to add to lightness (0-100).

    Returns:
        Lightened color in '#rrggbb' format.
    """
    r, g, b = _parse_hex(hex_color)
    h, s, lightness = _rgb_to_hsl(r, g, b)
    new_lightness = max(0.0, min(1.0, lightness + amount / 100))
    return _format_hex(*_hsl_to_rgb(h, s, new_lightness))


@mcp.tool()
def darken_color(hex_color: str, amount: float) -> str:
    """Darken a color by a percentage of the lightness range.

    Args:
        hex_color: Color in '#rrggbb' or 'rrggbb' format.
        amount: Percentage points to subtract from lightness (0-100).

    Returns:
        Darkened color in '#rrggbb' format.
    """
    r, g, b = _parse_hex(hex_color)
    h, s, lightness = _rgb_to_hsl(r, g, b)
    new_lightness = max(0.0, min(1.0, lightness - amount / 100))
    return _format_hex(*_hsl_to_rgb(h, s, new_lightness))


if __name__ == "__main__":
    mcp.run()
