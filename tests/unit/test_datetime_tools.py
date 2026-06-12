"""Unit tests for datetime MCP server."""


class TestGetCurrentTime:
    """Tests for get_current_time tool."""

    def test_returns_formatted_time(self) -> None:
        from servers.datetime_tools import get_current_time

        result = get_current_time()
        assert "202" in result
        assert ":" in result


class TestCalculateDate:
    """Tests for calculate_date tool."""

    def test_add_days(self) -> None:
        from servers.datetime_tools import calculate_date

        result = calculate_date("2026-01-01", 10)
        assert result == "2026-01-11"

    def test_subtract_days(self) -> None:
        from servers.datetime_tools import calculate_date

        result = calculate_date("2026-01-10", -5)
        assert result == "2026-01-05"

    def test_invalid_date(self) -> None:
        import pytest

        from servers.datetime_tools import calculate_date

        with pytest.raises(ValueError, match="Invalid date format"):
            calculate_date("not-a-date", 5)


class TestDaysBetween:
    """Tests for days_between tool."""

    def test_positive_difference(self) -> None:
        from servers.datetime_tools import days_between

        result = days_between("2026-01-01", "2026-01-10")
        assert result == 9

    def test_absolute_value(self) -> None:
        from servers.datetime_tools import days_between

        result = days_between("2026-01-10", "2026-01-01")
        assert result == 9

    def test_same_date(self) -> None:
        from servers.datetime_tools import days_between

        result = days_between("2026-06-15", "2026-06-15")
        assert result == 0
