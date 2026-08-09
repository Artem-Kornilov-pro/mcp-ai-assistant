"""Unit tests for Units MCP server."""

import pytest


class TestConvertLength:
    """Tests for convert_length tool."""

    def test_mile_to_km(self) -> None:
        from servers.units_server import convert_length

        result = float(convert_length(1, "mile", "km"))
        assert result == pytest.approx(1.609344)

    def test_same_unit(self) -> None:
        from servers.units_server import convert_length

        assert convert_length(5, "m", "m") == "5.0"

    def test_unsupported_unit(self) -> None:
        from servers.units_server import convert_length

        with pytest.raises(ValueError, match="Unsupported unit"):
            convert_length(1, "banana", "m")


class TestConvertWeight:
    """Tests for convert_weight tool."""

    def test_kg_to_pound(self) -> None:
        from servers.units_server import convert_weight

        result = float(convert_weight(1, "kg", "pound"))
        assert result == pytest.approx(2.2046226218487757)

    def test_unsupported_unit(self) -> None:
        from servers.units_server import convert_weight

        with pytest.raises(ValueError, match="Unsupported unit"):
            convert_weight(1, "kg", "banana")


class TestConvertTemperature:
    """Tests for convert_temperature tool."""

    def test_celsius_to_fahrenheit(self) -> None:
        from servers.units_server import convert_temperature

        assert convert_temperature(100, "celsius", "fahrenheit") == "212.0"

    def test_celsius_to_kelvin(self) -> None:
        from servers.units_server import convert_temperature

        assert convert_temperature(0, "celsius", "kelvin") == "273.15"

    def test_fahrenheit_to_celsius(self) -> None:
        from servers.units_server import convert_temperature

        assert convert_temperature(32, "fahrenheit", "celsius") == "0.0"

    def test_kelvin_to_fahrenheit(self) -> None:
        from servers.units_server import convert_temperature

        result = float(convert_temperature(273.15, "kelvin", "fahrenheit"))
        assert result == pytest.approx(32.0)

    def test_unsupported_unit(self) -> None:
        from servers.units_server import convert_temperature

        with pytest.raises(ValueError, match="Unsupported unit"):
            convert_temperature(0, "rankine", "celsius")


class TestConvertVolume:
    """Tests for convert_volume tool."""

    def test_gallon_to_liter(self) -> None:
        from servers.units_server import convert_volume

        result = float(convert_volume(1, "gallon", "l"))
        assert result == pytest.approx(3.785411784)

    def test_unsupported_unit(self) -> None:
        from servers.units_server import convert_volume

        with pytest.raises(ValueError, match="Unsupported unit"):
            convert_volume(1, "l", "banana")


class TestConvertArea:
    """Tests for convert_area tool."""

    def test_hectare_to_sq_m(self) -> None:
        from servers.units_server import convert_area

        assert convert_area(1, "hectare", "sq_m") == "10000.0"

    def test_unsupported_unit(self) -> None:
        from servers.units_server import convert_area

        with pytest.raises(ValueError, match="Unsupported unit"):
            convert_area(1, "banana", "sq_m")
