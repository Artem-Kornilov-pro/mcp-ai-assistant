"""Unit tests for Image MCP server."""

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


def _make_image(path: Path, size: tuple[int, int] = (100, 50)) -> None:
    Image.new("RGB", size, color=(255, 0, 0)).save(path)


class TestGetImageInfo:
    """Tests for get_image_info tool."""

    def test_basic(self, workspace: Path) -> None:
        from servers.image_server import get_image_info

        _make_image(workspace / "test.png")
        result = get_image_info("test.png")
        assert "100x50" in result
        assert "PNG" in result

    def test_nonexistent(self, workspace: Path) -> None:
        from servers.image_server import get_image_info

        with pytest.raises(FileNotFoundError, match="File not found"):
            get_image_info("missing.png")

    def test_outside_workspace(self, workspace: Path) -> None:
        from servers.image_server import get_image_info

        with pytest.raises(PermissionError, match="Access denied"):
            get_image_info("../outside.png")


class TestResizeImage:
    """Tests for resize_image tool."""

    def test_basic(self, workspace: Path) -> None:
        from servers.image_server import resize_image

        _make_image(workspace / "test.png")
        resize_image("test.png", 20, 10, "resized.png")

        with Image.open(workspace / "resized.png") as img:
            assert img.size == (20, 10)

    def test_invalid_dimensions(self, workspace: Path) -> None:
        from servers.image_server import resize_image

        _make_image(workspace / "test.png")
        with pytest.raises(ValueError, match="must be positive"):
            resize_image("test.png", 0, 10, "out.png")


class TestCropImage:
    """Tests for crop_image tool."""

    def test_basic(self, workspace: Path) -> None:
        from servers.image_server import crop_image

        _make_image(workspace / "test.png")
        crop_image("test.png", 0, 0, 40, 30, "cropped.png")

        with Image.open(workspace / "cropped.png") as img:
            assert img.size == (40, 30)

    def test_invalid_box(self, workspace: Path) -> None:
        from servers.image_server import crop_image

        _make_image(workspace / "test.png")
        with pytest.raises(ValueError, match="Invalid crop box"):
            crop_image("test.png", 40, 0, 10, 30, "out.png")


class TestRotateImage:
    """Tests for rotate_image tool."""

    def test_basic(self, workspace: Path) -> None:
        from servers.image_server import rotate_image

        _make_image(workspace / "test.png")
        rotate_image("test.png", 90, "rotated.png")

        assert (workspace / "rotated.png").exists()


class TestConvertFormat:
    """Tests for convert_format tool."""

    def test_png_to_jpg(self, workspace: Path) -> None:
        from servers.image_server import convert_format

        _make_image(workspace / "test.png")
        result = convert_format("test.png", "test.jpg")

        assert "jpg" in result
        with Image.open(workspace / "test.jpg") as img:
            assert img.format == "JPEG"


class TestCreateThumbnail:
    """Tests for create_thumbnail tool."""

    def test_preserves_aspect_ratio(self, workspace: Path) -> None:
        from servers.image_server import create_thumbnail

        _make_image(workspace / "test.png", size=(200, 100))
        create_thumbnail("test.png", "thumb.png", max_size=50)

        with Image.open(workspace / "thumb.png") as img:
            assert img.width <= 50
            assert img.height <= 50
            assert img.width == 2 * img.height

    def test_invalid_max_size(self, workspace: Path) -> None:
        from servers.image_server import create_thumbnail

        _make_image(workspace / "test.png")
        with pytest.raises(ValueError, match="must be positive"):
            create_thumbnail("test.png", "thumb.png", max_size=0)


class TestAddWatermark:
    """Tests for add_watermark tool."""

    def test_basic(self, workspace: Path) -> None:
        from servers.image_server import add_watermark

        _make_image(workspace / "test.png")
        add_watermark("test.png", "Sample", "watermarked.png")

        assert (workspace / "watermarked.png").exists()

    def test_jpg_output(self, workspace: Path) -> None:
        from servers.image_server import add_watermark

        _make_image(workspace / "test.png")
        add_watermark("test.png", "Sample", "watermarked.jpg")

        with Image.open(workspace / "watermarked.jpg") as img:
            assert img.mode == "RGB"
