"""Unit tests for Color MCP server."""

import pytest


class TestHexToRgb:
    """Tests for hex_to_rgb tool."""

    def test_with_hash(self) -> None:
        from servers.color_server import hex_to_rgb

        assert hex_to_rgb("#ff0000") == "255, 0, 0"

    def test_without_hash(self) -> None:
        from servers.color_server import hex_to_rgb

        assert hex_to_rgb("00ff00") == "0, 255, 0"

    def test_invalid_length(self) -> None:
        from servers.color_server import hex_to_rgb

        with pytest.raises(ValueError, match="Invalid hex color"):
            hex_to_rgb("#fff")

    def test_invalid_characters(self) -> None:
        from servers.color_server import hex_to_rgb

        with pytest.raises(ValueError, match="Invalid hex color"):
            hex_to_rgb("zzzzzz")


class TestRgbToHex:
    """Tests for rgb_to_hex tool."""

    def test_basic(self) -> None:
        from servers.color_server import rgb_to_hex

        assert rgb_to_hex(255, 0, 0) == "#ff0000"

    def test_clamps_out_of_range(self) -> None:
        from servers.color_server import rgb_to_hex

        assert rgb_to_hex(300, -10, 128) == "#ff0080"


class TestHexToHsl:
    """Tests for hex_to_hsl tool."""

    def test_red(self) -> None:
        from servers.color_server import hex_to_hsl

        assert hex_to_hsl("#ff0000") == "0, 100%, 50%"

    def test_gray(self) -> None:
        from servers.color_server import hex_to_hsl

        assert hex_to_hsl("#808080") == "0, 0%, 50%"


class TestGetContrastColor:
    """Tests for get_contrast_color tool."""

    def test_white_background_needs_black_text(self) -> None:
        from servers.color_server import get_contrast_color

        assert get_contrast_color("#ffffff") == "black"

    def test_black_background_needs_white_text(self) -> None:
        from servers.color_server import get_contrast_color

        assert get_contrast_color("#000000") == "white"


class TestLightenDarken:
    """Tests for lighten_color / darken_color tools."""

    def test_lighten(self) -> None:
        from servers.color_server import lighten_color

        assert lighten_color("#000000", 20) == "#333333"

    def test_darken(self) -> None:
        from servers.color_server import darken_color

        assert darken_color("#ffffff", 20) == "#cccccc"

    def test_lighten_clamps_at_white(self) -> None:
        from servers.color_server import lighten_color

        assert lighten_color("#ffffff", 50) == "#ffffff"

    def test_darken_clamps_at_black(self) -> None:
        from servers.color_server import darken_color

        assert darken_color("#000000", 50) == "#000000"

    def test_roundtrip_preserves_hue(self) -> None:
        from servers.color_server import darken_color, hex_to_hsl, lighten_color

        base_hue = hex_to_hsl("#3366cc").split(",")[0]
        lightened_hue = hex_to_hsl(lighten_color("#3366cc", 10)).split(",")[0]
        darkened_hue = hex_to_hsl(darken_color("#3366cc", 10)).split(",")[0]
        assert base_hue == lightened_hue == darkened_hue
