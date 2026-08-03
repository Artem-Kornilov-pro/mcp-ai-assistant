"""MCP server for random number and selection utilities."""

import random

from fastmcp import FastMCP

mcp = FastMCP("Random")


def _parse_items(items: str) -> list[str]:
    """Parse a comma-separated list of items."""
    parsed = [i.strip() for i in items.split(",") if i.strip()]
    if not parsed:
        raise ValueError("No items provided")
    return parsed


@mcp.tool()
def random_int(min_value: int, max_value: int) -> str:
    """Generate a random integer within a range (inclusive).

    Args:
        min_value: Lower bound (inclusive).
        max_value: Upper bound (inclusive).

    Returns:
        A random integer as a string.
    """
    if min_value > max_value:
        raise ValueError("min_value must be <= max_value")
    return str(random.randint(min_value, max_value))


@mcp.tool()
def random_float(min_value: float, max_value: float) -> str:
    """Generate a random floating-point number within a range.

    Args:
        min_value: Lower bound.
        max_value: Upper bound.

    Returns:
        A random float as a string.
    """
    if min_value > max_value:
        raise ValueError("min_value must be <= max_value")
    return str(random.uniform(min_value, max_value))


@mcp.tool()
def random_choice(items: str) -> str:
    """Pick a random element from a list.

    Args:
        items: Comma-separated list of items.

    Returns:
        A single randomly chosen item.
    """
    return random.choice(_parse_items(items))


@mcp.tool()
def shuffle_list(items: str) -> str:
    """Shuffle a list of items into random order.

    Args:
        items: Comma-separated list of items.

    Returns:
        Comma-separated shuffled list.
    """
    parsed = _parse_items(items)
    random.shuffle(parsed)
    return ", ".join(parsed)


@mcp.tool()
def random_sample(items: str, count: int) -> str:
    """Pick N unique random elements from a list.

    Args:
        items: Comma-separated list of items.
        count: Number of unique items to pick.

    Returns:
        Comma-separated sample of items.
    """
    parsed = _parse_items(items)
    if count > len(parsed):
        raise ValueError(f"count ({count}) cannot exceed number of items ({len(parsed)})")
    if count < 0:
        raise ValueError("count must be >= 0")
    return ", ".join(random.sample(parsed, count))


if __name__ == "__main__":
    mcp.run()
