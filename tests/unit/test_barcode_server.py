"""Unit tests for Barcode MCP server.

Note: read_barcode depends on pyzbar, which requires the system libzbar
library. It is not exercised here directly since that native dependency
is unavailable in some local dev environments; CI installs libzbar0 to
run it as part of the wider test suite. Generation tools do not need
pyzbar and are fully covered.
"""

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


def _require_pyzbar() -> None:
    """Skip the test if pyzbar/libzbar cannot be loaded (e.g. missing system lib)."""
    try:
        import pyzbar.pyzbar  # noqa: F401
    except Exception as e:  # pyzbar raises OSError/FileNotFoundError, not just ImportError
        pytest.skip(f"pyzbar/libzbar not available: {e}")


class TestListBarcodeTypes:
    """Tests for list_barcode_types tool."""

    def test_includes_common_types(self, workspace: Path) -> None:
        from servers.barcode_server import list_barcode_types

        result = list_barcode_types()
        assert "code128" in result
        assert "ean13" in result


class TestGenerateBarcode:
    """Tests for generate_barcode tool."""

    def test_code128_default(self, workspace: Path) -> None:
        from servers.barcode_server import generate_barcode

        result = generate_barcode("HELLO123", "barcode.png")
        assert "Barcode saved" in result
        assert (workspace / "barcode.png").exists()

    def test_ean13(self, workspace: Path) -> None:
        from servers.barcode_server import generate_barcode

        result = generate_barcode("400638133393", "ean.png", barcode_type="ean13")
        assert "Barcode saved" in result
        assert (workspace / "ean.png").exists()

    def test_without_text(self, workspace: Path) -> None:
        from servers.barcode_server import generate_barcode

        generate_barcode("HELLO123", "notext.png", write_text=False)
        assert (workspace / "notext.png").exists()

    def test_unsupported_type(self, workspace: Path) -> None:
        from servers.barcode_server import generate_barcode

        with pytest.raises(ValueError, match="Unsupported barcode_type"):
            generate_barcode("HELLO123", "barcode.png", barcode_type="not-a-real-type")

    def test_invalid_data_for_type(self, workspace: Path) -> None:
        from servers.barcode_server import generate_barcode

        with pytest.raises(ValueError, match="Invalid data"):
            generate_barcode("not-numeric", "ean.png", barcode_type="ean13")

    def test_outside_workspace(self, workspace: Path) -> None:
        from servers.barcode_server import generate_barcode

        with pytest.raises(PermissionError, match="Access denied"):
            generate_barcode("HELLO123", "../outside.png")


class TestBatchGenerateBarcode:
    """Tests for batch_generate_barcode tool."""

    def test_basic(self, workspace: Path) -> None:
        from servers.barcode_server import batch_generate_barcode

        result = batch_generate_barcode("a.png:HELLO;b.png:WORLD", "codes")
        assert "Generated 2 barcode(s)" in result
        assert (workspace / "codes" / "a.png").exists()
        assert (workspace / "codes" / "b.png").exists()

    def test_empty_items(self, workspace: Path) -> None:
        from servers.barcode_server import batch_generate_barcode

        with pytest.raises(ValueError, match="No items provided"):
            batch_generate_barcode("", "codes")

    def test_invalid_item_format(self, workspace: Path) -> None:
        from servers.barcode_server import batch_generate_barcode

        with pytest.raises(ValueError, match="Invalid item format"):
            batch_generate_barcode("no-colon-here", "codes")


class TestReadBarcode:
    """Tests for read_barcode tool (sandbox/file-existence checks only, see module docstring)."""

    def test_missing_file(self, workspace: Path) -> None:
        from servers.barcode_server import read_barcode

        with pytest.raises(FileNotFoundError, match="File not found"):
            read_barcode("missing.png")

    def test_outside_workspace(self, workspace: Path) -> None:
        from servers.barcode_server import read_barcode

        with pytest.raises(PermissionError, match="Access denied"):
            read_barcode("../outside.png")


class TestReadBarcodeRoundtrip:
    """Round-trip decode test — requires a working pyzbar/libzbar install."""

    def test_roundtrip(self, workspace: Path) -> None:
        _require_pyzbar()
        from servers.barcode_server import generate_barcode, read_barcode

        generate_barcode("HELLO123", "barcode.png", barcode_type="code128")
        result = read_barcode("barcode.png")
        assert "HELLO123" in result


class TestBlankImage:
    """Tests decoding an image with no barcode."""

    def test_no_barcode_in_image(self, workspace: Path) -> None:
        _require_pyzbar()
        from servers.barcode_server import read_barcode

        Image.new("RGB", (100, 100), color=(255, 255, 255)).save(workspace / "blank.png")
        with pytest.raises(ValueError, match="No barcode detected"):
            read_barcode("blank.png")
