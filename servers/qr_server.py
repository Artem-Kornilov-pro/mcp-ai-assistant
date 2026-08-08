"""MCP server for QR code generation and decoding."""

import os
from pathlib import Path
from urllib.parse import quote

import cv2
import numpy as np
import qrcode
from fastmcp import FastMCP
from PIL import Image

mcp = FastMCP("QR")

_ERROR_CORRECTION = {
    "L": qrcode.constants.ERROR_CORRECT_L,
    "M": qrcode.constants.ERROR_CORRECT_M,
    "Q": qrcode.constants.ERROR_CORRECT_Q,
    "H": qrcode.constants.ERROR_CORRECT_H,
}


def _resolve_path(path: str) -> Path:
    """Resolve path and enforce workspace boundary."""
    workspace = Path(os.getenv("WORKSPACE_DIR", "./workspace")).resolve()
    target = (workspace / path).resolve()
    try:
        target.relative_to(workspace)
    except ValueError:
        raise PermissionError(f"Access denied: '{path}' is outside workspace")
    return target


def _make_qr_image(
    data: str,
    box_size: int,
    border: int,
    error_correction: str,
    fill_color: str = "black",
    back_color: str = "white",
) -> Image.Image:
    """Build a QR code image from data."""
    if box_size <= 0 or border < 0:
        raise ValueError("box_size must be positive and border must be non-negative")
    if error_correction not in _ERROR_CORRECTION:
        raise ValueError(
            f"Unsupported error_correction: {error_correction}. "
            f"Use one of {sorted(_ERROR_CORRECTION)}"
        )

    qr = qrcode.QRCode(
        error_correction=_ERROR_CORRECTION[error_correction],
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fill_color, back_color=back_color)
    return img.convert("RGB")


def _save_qr_image(img: Image.Image, output: str) -> Path:
    """Save a QR code image into the workspace."""
    dest = _resolve_path(output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest)
    return dest


@mcp.tool()
def generate_qr_code(
    data: str,
    output: str,
    box_size: int = 10,
    border: int = 4,
    error_correction: str = "M",
) -> str:
    """Generate a QR code from arbitrary text or a URL.

    Args:
        data: Text, URL, or any string to encode.
        output: Output image path relative to workspace (e.g. "qr.png").
        box_size: Pixel size of each QR module. Default: 10.
        border: Border width in modules. Default: 4.
        error_correction: One of 'L', 'M', 'Q', 'H'. Default: 'M'.

    Returns:
        Confirmation message.
    """
    img = _make_qr_image(data, box_size, border, error_correction)
    _save_qr_image(img, output)
    return f"QR code saved: {output}"


@mcp.tool()
def generate_qr_code_colored(
    data: str,
    output: str,
    fill_color: str = "black",
    back_color: str = "white",
    box_size: int = 10,
    border: int = 4,
) -> str:
    """Generate a QR code with custom foreground/background colors.

    Args:
        data: Text, URL, or any string to encode.
        output: Output image path relative to workspace.
        fill_color: Module (foreground) color name or hex code. Default: 'black'.
        back_color: Background color name or hex code. Default: 'white'.
        box_size: Pixel size of each QR module. Default: 10.
        border: Border width in modules. Default: 4.

    Returns:
        Confirmation message.
    """
    img = _make_qr_image(data, box_size, border, "M", fill_color, back_color)
    _save_qr_image(img, output)
    return f"QR code saved: {output}"


@mcp.tool()
def generate_qr_with_logo(
    data: str, logo_path: str, output: str, box_size: int = 10, border: int = 4
) -> str:
    """Generate a QR code with a logo image embedded in the center.

    Uses high error correction so the code stays scannable despite the logo.

    Args:
        data: Text, URL, or any string to encode.
        logo_path: Path to the logo image relative to workspace.
        output: Output image path relative to workspace.
        box_size: Pixel size of each QR module. Default: 10.
        border: Border width in modules. Default: 4.

    Returns:
        Confirmation message.
    """
    logo_target = _resolve_path(logo_path)
    if not logo_target.exists():
        raise FileNotFoundError(f"File not found: {logo_path}")

    img = _make_qr_image(data, box_size, border, "H")

    with Image.open(logo_target) as logo:
        logo_size = min(img.size) // 4
        logo = logo.convert("RGBA").resize((logo_size, logo_size))
        position = ((img.width - logo_size) // 2, (img.height - logo_size) // 2)
        img.paste(logo, position, mask=logo)

    _save_qr_image(img, output)
    return f"QR code with logo saved: {output}"


@mcp.tool()
def generate_wifi_qr(
    ssid: str, password: str, output: str, security: str = "WPA", hidden: bool = False
) -> str:
    """Generate a QR code that connects a phone to a Wi-Fi network when scanned.

    Args:
        ssid: Wi-Fi network name.
        password: Wi-Fi password (ignored if security is 'nopass').
        output: Output image path relative to workspace.
        security: One of 'WPA', 'WEP', 'nopass'. Default: 'WPA'.
        hidden: Whether the network is hidden. Default: False.

    Returns:
        Confirmation message.
    """
    if security not in ("WPA", "WEP", "nopass"):
        raise ValueError("security must be one of 'WPA', 'WEP', 'nopass'")

    pwd = "" if security == "nopass" else password
    data = f"WIFI:T:{security};S:{ssid};P:{pwd};H:{'true' if hidden else 'false'};;"
    img = _make_qr_image(data, 10, 4, "M")
    _save_qr_image(img, output)
    return f"Wi-Fi QR code saved: {output}"


@mcp.tool()
def generate_vcard_qr(
    name: str,
    output: str,
    phone: str = "",
    email: str = "",
    organization: str = "",
    url: str = "",
) -> str:
    """Generate a QR code contact card (vCard) that a phone can save.

    Args:
        name: Full name.
        output: Output image path relative to workspace.
        phone: Phone number.
        email: Email address.
        organization: Company or organization name.
        url: Website URL.

    Returns:
        Confirmation message.
    """
    lines = ["BEGIN:VCARD", "VERSION:3.0", f"N:{name}", f"FN:{name}"]
    if organization:
        lines.append(f"ORG:{organization}")
    if phone:
        lines.append(f"TEL:{phone}")
    if email:
        lines.append(f"EMAIL:{email}")
    if url:
        lines.append(f"URL:{url}")
    lines.append("END:VCARD")

    img = _make_qr_image("\n".join(lines), 10, 4, "M")
    _save_qr_image(img, output)
    return f"vCard QR code saved: {output}"


@mcp.tool()
def generate_sms_qr(phone: str, message: str, output: str) -> str:
    """Generate a QR code that pre-fills an SMS message.

    Args:
        phone: Recipient phone number.
        message: SMS message body.
        output: Output image path relative to workspace.

    Returns:
        Confirmation message.
    """
    data = f"SMSTO:{phone}:{message}"
    img = _make_qr_image(data, 10, 4, "M")
    _save_qr_image(img, output)
    return f"SMS QR code saved: {output}"


@mcp.tool()
def generate_email_qr(email: str, output: str, subject: str = "", body: str = "") -> str:
    """Generate a QR code that pre-fills an email.

    Args:
        email: Recipient email address.
        output: Output image path relative to workspace.
        subject: Email subject.
        body: Email body.

    Returns:
        Confirmation message.
    """
    query = "&".join(
        f"{key}={quote(value)}" for key, value in (("subject", subject), ("body", body)) if value
    )
    data = f"mailto:{email}" + (f"?{query}" if query else "")
    img = _make_qr_image(data, 10, 4, "M")
    _save_qr_image(img, output)
    return f"Email QR code saved: {output}"


@mcp.tool()
def generate_geo_qr(latitude: float, longitude: float, output: str) -> str:
    """Generate a QR code that opens a map at the given coordinates.

    Args:
        latitude: Latitude in decimal degrees.
        longitude: Longitude in decimal degrees.
        output: Output image path relative to workspace.

    Returns:
        Confirmation message.
    """
    data = f"geo:{latitude},{longitude}"
    img = _make_qr_image(data, 10, 4, "M")
    _save_qr_image(img, output)
    return f"Geo QR code saved: {output}"


@mcp.tool()
def batch_generate_qr(items: str, output_dir: str, box_size: int = 10, border: int = 4) -> str:
    """Generate multiple QR codes at once.

    Args:
        items: ';'-separated "filename.png:data" pairs.
        output_dir: Output directory relative to workspace.
        box_size: Pixel size of each QR module. Default: 10.
        border: Border width in modules. Default: 4.

    Returns:
        Confirmation message with the number of QR codes generated.
    """
    entries = [e.strip() for e in items.split(";") if e.strip()]
    if not entries:
        raise ValueError("No items provided")

    count = 0
    for entry in entries:
        if ":" not in entry:
            raise ValueError(f"Invalid item format: '{entry}'. Use 'filename.png:data'")
        filename, data = entry.split(":", 1)
        img = _make_qr_image(data, box_size, border, "M")
        _save_qr_image(img, str(Path(output_dir) / filename.strip()))
        count += 1

    return f"Generated {count} QR code(s) in {output_dir}"


@mcp.tool()
def read_qr_code(path: str) -> str:
    """Detect and decode QR codes from an image.

    Args:
        path: Path to image file relative to workspace.

    Returns:
        Decoded text (one per line if multiple QR codes are found).
    """
    target = _resolve_path(path)
    if not target.exists():
        raise FileNotFoundError(f"File not found: {path}")

    image = cv2.imdecode(np.fromfile(str(target), dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Could not read image: {path}")

    detector = cv2.QRCodeDetector()
    ok, decoded_info, _points, _straight = detector.detectAndDecodeMulti(image)
    results = [text for text in decoded_info if text] if ok else []

    if not results:
        raise ValueError(f"No QR code detected in image: {path}")

    return "\n".join(results)


if __name__ == "__main__":
    mcp.run()
