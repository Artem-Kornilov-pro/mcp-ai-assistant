"""MCP server for date and time operations."""

from datetime import date, datetime, timedelta

from fastmcp import FastMCP

mcp = FastMCP("Datetime")


@mcp.tool()
def get_current_time() -> str:
    """Get current date and time.

    Returns:
        Formatted string with date, time and day of week.
    """
    now = datetime.now()
    weekdays = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
    day_name = weekdays[now.weekday()]
    return now.strftime(f"%Y-%m-%d %H:%M:%S ({day_name})")


@mcp.tool()
def calculate_date(date_str: str, days: int) -> str:
    """Add or subtract days from a date.

    Args:
        date_str: Date in YYYY-MM-DD format.
        days: Number of days to add (negative to subtract).

    Returns:
        Resulting date in YYYY-MM-DD format.
    """
    try:
        d = date.fromisoformat(date_str)
        result = d + timedelta(days=days)
        return result.isoformat()
    except ValueError as e:
        raise ValueError(f"Invalid date format. Use YYYY-MM-DD. Error: {e}") from e


@mcp.tool()
def days_between(date1: str, date2: str) -> int:
    """Calculate number of days between two dates.

    Args:
        date1: First date in YYYY-MM-DD format.
        date2: Second date in YYYY-MM-DD format.

    Returns:
        Absolute number of days between dates.
    """
    try:
        d1 = date.fromisoformat(date1)
        d2 = date.fromisoformat(date2)
        return abs((d2 - d1).days)
    except ValueError as e:
        raise ValueError(f"Invalid date format. Use YYYY-MM-DD. Error: {e}") from e


if __name__ == "__main__":
    mcp.run()
