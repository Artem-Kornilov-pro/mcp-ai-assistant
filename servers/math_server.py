"""MCP server for math utilities (primes, gcd/lcm, factorial, fibonacci)."""

import math

from fastmcp import FastMCP

mcp = FastMCP("Math")


@mcp.tool()
def is_prime(n: int) -> str:
    """Check whether a number is prime.

    Args:
        n: Integer to check.

    Returns:
        'True' or 'False'.
    """
    if n < 2:
        return "False"
    if n in (2, 3):
        return "True"
    if n % 2 == 0:
        return "False"
    for divisor in range(3, int(math.isqrt(n)) + 1, 2):
        if n % divisor == 0:
            return "False"
    return "True"


@mcp.tool()
def gcd(a: int, b: int) -> str:
    """Compute the greatest common divisor of two integers.

    Args:
        a: First integer.
        b: Second integer.

    Returns:
        The greatest common divisor.
    """
    return str(math.gcd(a, b))


@mcp.tool()
def lcm(a: int, b: int) -> str:
    """Compute the least common multiple of two integers.

    Args:
        a: First integer.
        b: Second integer.

    Returns:
        The least common multiple.
    """
    return str(math.lcm(a, b))


@mcp.tool()
def factorial(n: int) -> str:
    """Compute the factorial of a non-negative integer.

    Args:
        n: Non-negative integer.

    Returns:
        n! as a string.
    """
    if n < 0:
        raise ValueError("n must be >= 0")
    return str(math.factorial(n))


@mcp.tool()
def fibonacci(n: int) -> str:
    """Compute the n-th Fibonacci number (0-indexed: fib(0) = 0, fib(1) = 1).

    Args:
        n: Index in the Fibonacci sequence (>= 0).

    Returns:
        The n-th Fibonacci number.
    """
    if n < 0:
        raise ValueError("n must be >= 0")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return str(a)


if __name__ == "__main__":
    mcp.run()
