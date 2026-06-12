"""MCP server for date and time operations."""

from datetime import date, datetime, timedelta

from fastmcp import FastMCP

mcp = FastMCP("Datetime")

WEEKDAYS_RU = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
MONTHS_RU = [
    "января",
    "февраля",
    "марта",
    "апреля",
    "мая",
    "июня",
    "июля",
    "августа",
    "сентября",
    "октября",
    "ноября",
    "декабря",
]


@mcp.tool()
def get_current_time() -> str:
    """Get current date and time.

    Returns:
        Formatted string with date, time, day of week, week number, and day of year.
    """
    now = datetime.now()
    day_name = WEEKDAYS_RU[now.weekday()]
    week_number = now.isocalendar()[1]
    day_of_year = now.timetuple().tm_yday

    return (
        f"{now.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"День недели: {day_name}\n"
        f"Неделя года: {week_number}\n"
        f"День года: {day_of_year}/365"
    )


@mcp.tool()
def calculate_date(date_str: str, days: int) -> str:
    """Add or subtract days from a date.

    Args:
        date_str: Date in YYYY-MM-DD format.
        days: Number of days to add (negative to subtract).

    Returns:
        Resulting date with day of week.
    """
    try:
        d = date.fromisoformat(date_str)
        result = d + timedelta(days=days)
        day_name = WEEKDAYS_RU[result.weekday()]
        return f"{result.isoformat()} ({day_name})"
    except ValueError as e:
        raise ValueError(f"Invalid date format. Use YYYY-MM-DD. Error: {e}") from e


@mcp.tool()
def days_between(date1: str, date2: str) -> str:
    """Calculate number of days between two dates.

    Args:
        date1: First date in YYYY-MM-DD format.
        date2: Second date in YYYY-MM-DD format.

    Returns:
        Number of days with human-readable breakdown.
    """
    try:
        d1 = date.fromisoformat(date1)
        d2 = date.fromisoformat(date2)
        delta = abs((d2 - d1).days)
        weeks = delta // 7
        days_left = delta % 7
        parts = []
        if weeks:
            parts.append(f"{weeks} нед.")
        if days_left:
            parts.append(f"{days_left} дн.")
        return f"{delta} дней ({' '.join(parts)})"
    except ValueError as e:
        raise ValueError(f"Invalid date format. Use YYYY-MM-DD. Error: {e}") from e


@mcp.tool()
def get_day_of_week(date_str: str) -> str:
    """Get day of week for a specific date.

    Args:
        date_str: Date in YYYY-MM-DD format.

    Returns:
        Day of week in Russian.
    """
    try:
        d = date.fromisoformat(date_str)
        return WEEKDAYS_RU[d.weekday()]
    except ValueError as e:
        raise ValueError(f"Invalid date format. Use YYYY-MM-DD. Error: {e}") from e


@mcp.tool()
def get_week_number(date_str: str) -> str:
    """Get ISO week number for a date.

    Args:
        date_str: Date in YYYY-MM-DD format.

    Returns:
        Week number and year.
    """
    try:
        d = date.fromisoformat(date_str)
        iso = d.isocalendar()
        return f"Неделя {iso[1]}, {iso[0]} год"
    except ValueError as e:
        raise ValueError(f"Invalid date format. Use YYYY-MM-DD. Error: {e}") from e


@mcp.tool()
def format_date_ru(date_str: str) -> str:
    """Format a date in Russian style.

    Args:
        date_str: Date in YYYY-MM-DD format.

    Returns:
        Date formatted as '12 июня 2026 года'.
    """
    try:
        d = date.fromisoformat(date_str)
        return f"{d.day} {MONTHS_RU[d.month - 1]} {d.year} года"
    except ValueError as e:
        raise ValueError(f"Invalid date format. Use YYYY-MM-DD. Error: {e}") from e


@mcp.tool()
def days_until(date_str: str) -> str:
    """Calculate days remaining until a date.

    Args:
        date_str: Target date in YYYY-MM-DD format.

    Returns:
        Number of days remaining (negative if past).
    """
    try:
        target = date.fromisoformat(date_str)
        today = date.today()
        delta = (target - today).days
        if delta > 0:
            return f"Осталось {delta} дней до {format_date_ru(date_str)}"
        elif delta < 0:
            return f"Прошло {abs(delta)} дней с {format_date_ru(date_str)}"
        else:
            return "Это сегодня!"
    except ValueError as e:
        raise ValueError(f"Invalid date format. Use YYYY-MM-DD. Error: {e}") from e


@mcp.tool()
def is_weekend(date_str: str) -> str:
    """Check if a date falls on a weekend.

    Args:
        date_str: Date in YYYY-MM-DD format.

    Returns:
        Yes/no with day name.
    """
    try:
        d = date.fromisoformat(date_str)
        day_name = WEEKDAYS_RU[d.weekday()]
        is_we = d.weekday() >= 5
        return f"{'Да, выходной' if is_we else 'Нет, рабочий день'} ({day_name})"
    except ValueError as e:
        raise ValueError(f"Invalid date format. Use YYYY-MM-DD. Error: {e}") from e


if __name__ == "__main__":
    mcp.run()
