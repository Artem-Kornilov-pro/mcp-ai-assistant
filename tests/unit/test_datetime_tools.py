"""Unit tests for datetime MCP server."""

import pytest


class TestGetCurrentTime:
    """Tests for get_current_time tool."""

    def test_returns_formatted_time(self) -> None:
        from servers.datetime_tools import get_current_time

        result = get_current_time()
        assert "202" in result
        assert ":" in result
        assert "День недели" in result


class TestCalculateDate:
    """Tests for calculate_date tool."""

    def test_add_days(self) -> None:
        from servers.datetime_tools import calculate_date

        result = calculate_date("2026-01-01", 10)
        assert "2026-01-11" in result
        assert "воскресенье" in result

    def test_subtract_days(self) -> None:
        from servers.datetime_tools import calculate_date

        result = calculate_date("2026-01-10", -5)
        assert "2026-01-05" in result
        assert "понедельник" in result

    def test_invalid_date(self) -> None:
        from servers.datetime_tools import calculate_date

        with pytest.raises(ValueError, match="Invalid date format"):
            calculate_date("not-a-date", 5)


class TestDaysBetween:
    """Tests for days_between tool."""

    def test_positive_difference(self) -> None:
        from servers.datetime_tools import days_between

        result = days_between("2026-01-01", "2026-01-10")
        assert "9" in result
        assert "дней" in result

    def test_absolute_value(self) -> None:
        from servers.datetime_tools import days_between

        result = days_between("2026-01-10", "2026-01-01")
        assert "9" in result

    def test_same_date(self) -> None:
        from servers.datetime_tools import days_between

        result = days_between("2026-06-15", "2026-06-15")
        assert "0" in result


class TestGetDayOfWeek:
    """Tests for get_day_of_week tool."""

    def test_known_date(self) -> None:
        from servers.datetime_tools import get_day_of_week

        result = get_day_of_week("2026-01-01")
        assert result == "четверг"


class TestDaysUntil:
    """Tests for days_until tool."""

    def test_future_date(self) -> None:
        from servers.datetime_tools import days_until

        result = days_until("2099-01-01")
        assert "Осталось" in result

    def test_past_date(self) -> None:
        from servers.datetime_tools import days_until

        result = days_until("2020-01-01")
        assert "Прошло" in result


class TestIsWeekend:
    """Tests for is_weekend tool."""

    def test_weekend(self) -> None:
        from servers.datetime_tools import is_weekend

        result = is_weekend("2026-01-03")  # Saturday
        assert "Да" in result

    def test_weekday(self) -> None:
        from servers.datetime_tools import is_weekend

        result = is_weekend("2026-01-02")  # Friday
        assert "Нет" in result
