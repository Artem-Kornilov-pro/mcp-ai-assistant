"""Unit tests for QR MCP server."""

import os
from pathlib import Path

import pytest
from PIL import Image

os.environ["WORKSPACE_DIR"] = "./workspace"


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """Temp workspace."""
    ws = tmp_path / "workspace"
    ws.mkdir()
    os.environ["WORKSPACE_DIR"] = str(ws)
    return ws


class TestGenerateQrCode:
    """Tests for generate_qr_code tool."""

    def test_basic(self, workspace: Path) -> None:
        from servers.qr_server import generate_qr_code

        result = generate_qr_code("hello world", "qr.png")
        assert "QR code saved" in result
        assert (workspace / "qr.png").exists()

    def test_invalid_box_size(self, workspace: Path) -> None:
        from servers.qr_server import generate_qr_code

        with pytest.raises(ValueError, match="box_size must be positive"):
            generate_qr_code("hello", "qr.png", box_size=0)

    def test_invalid_error_correction(self, workspace: Path) -> None:
        from servers.qr_server import generate_qr_code

        with pytest.raises(ValueError, match="Unsupported error_correction"):
            generate_qr_code("hello", "qr.png", error_correction="X")

    def test_outside_workspace(self, workspace: Path) -> None:
        from servers.qr_server import generate_qr_code

        with pytest.raises(PermissionError, match="Access denied"):
            generate_qr_code("hello", "../outside.png")


class TestGenerateQrCodeColored:
    """Tests for generate_qr_code_colored tool."""

    def test_basic(self, workspace: Path) -> None:
        from servers.qr_server import generate_qr_code_colored

        result = generate_qr_code_colored("hello", "qr.png", fill_color="blue", back_color="white")
        assert "QR code saved" in result
        assert (workspace / "qr.png").exists()


class TestGenerateQrWithLogo:
    """Tests for generate_qr_with_logo tool."""

    def test_basic(self, workspace: Path) -> None:
        from servers.qr_server import generate_qr_with_logo

        Image.new("RGBA", (50, 50), color=(255, 0, 0, 255)).save(workspace / "logo.png")
        result = generate_qr_with_logo("https://example.com", "logo.png", "qr.png")
        assert "QR code with logo saved" in result
        assert (workspace / "qr.png").exists()

    def test_missing_logo(self, workspace: Path) -> None:
        from servers.qr_server import generate_qr_with_logo

        with pytest.raises(FileNotFoundError, match="File not found"):
            generate_qr_with_logo("data", "missing.png", "qr.png")


class TestGenerateWifiQr:
    """Tests for generate_wifi_qr tool."""

    def test_basic(self, workspace: Path) -> None:
        from servers.qr_server import generate_wifi_qr

        result = generate_wifi_qr("MyNetwork", "secret123", "wifi.png")
        assert "Wi-Fi QR code saved" in result
        assert (workspace / "wifi.png").exists()

    def test_invalid_security(self, workspace: Path) -> None:
        from servers.qr_server import generate_wifi_qr

        with pytest.raises(ValueError, match="security must be one of"):
            generate_wifi_qr("Net", "pwd", "wifi.png", security="OPEN")


class TestGenerateVcardQr:
    """Tests for generate_vcard_qr tool."""

    def test_basic(self, workspace: Path) -> None:
        from servers.qr_server import generate_vcard_qr

        result = generate_vcard_qr(
            "Ivan Petrov", "vcard.png", phone="+1234567890", email="ivan@example.com"
        )
        assert "vCard QR code saved" in result
        assert (workspace / "vcard.png").exists()


class TestGenerateSmsQr:
    """Tests for generate_sms_qr tool."""

    def test_basic(self, workspace: Path) -> None:
        from servers.qr_server import generate_sms_qr

        result = generate_sms_qr("+1234567890", "Hi there", "sms.png")
        assert "SMS QR code saved" in result
        assert (workspace / "sms.png").exists()


class TestGenerateEmailQr:
    """Tests for generate_email_qr tool."""

    def test_basic(self, workspace: Path) -> None:
        from servers.qr_server import generate_email_qr

        result = generate_email_qr("test@example.com", "email.png", subject="Hi", body="Hello")
        assert "Email QR code saved" in result
        assert (workspace / "email.png").exists()

    def test_no_extras(self, workspace: Path) -> None:
        from servers.qr_server import generate_email_qr

        result = generate_email_qr("test@example.com", "email.png")
        assert "Email QR code saved" in result


class TestGenerateGeoQr:
    """Tests for generate_geo_qr tool."""

    def test_basic(self, workspace: Path) -> None:
        from servers.qr_server import generate_geo_qr

        result = generate_geo_qr(55.7558, 37.6173, "geo.png")
        assert "Geo QR code saved" in result
        assert (workspace / "geo.png").exists()


class TestBatchGenerateQr:
    """Tests for batch_generate_qr tool."""

    def test_basic(self, workspace: Path) -> None:
        from servers.qr_server import batch_generate_qr

        result = batch_generate_qr("a.png:hello;b.png:world", "codes")
        assert "Generated 2 QR code(s)" in result
        assert (workspace / "codes" / "a.png").exists()
        assert (workspace / "codes" / "b.png").exists()

    def test_empty_items(self, workspace: Path) -> None:
        from servers.qr_server import batch_generate_qr

        with pytest.raises(ValueError, match="No items provided"):
            batch_generate_qr("", "codes")

    def test_invalid_item_format(self, workspace: Path) -> None:
        from servers.qr_server import batch_generate_qr

        with pytest.raises(ValueError, match="Invalid item format"):
            batch_generate_qr("no-colon-here", "codes")


class TestReadQrCode:
    """Tests for read_qr_code tool."""

    def test_roundtrip(self, workspace: Path) -> None:
        from servers.qr_server import generate_qr_code, read_qr_code

        generate_qr_code("Hello QR World", "qr.png")
        result = read_qr_code("qr.png")
        assert result == "Hello QR World"

    def test_missing_file(self, workspace: Path) -> None:
        from servers.qr_server import read_qr_code

        with pytest.raises(FileNotFoundError, match="File not found"):
            read_qr_code("missing.png")

    def test_no_qr_in_image(self, workspace: Path) -> None:
        from servers.qr_server import read_qr_code

        Image.new("RGB", (100, 100), color=(255, 255, 255)).save(workspace / "blank.png")
        with pytest.raises(ValueError, match="No QR code detected"):
            read_qr_code("blank.png")
