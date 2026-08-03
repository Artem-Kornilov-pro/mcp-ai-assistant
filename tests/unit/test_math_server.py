"""Unit tests for Math MCP server."""

import pytest


class TestIsPrime:
    """Tests for is_prime tool."""

    @pytest.mark.parametrize("n", [2, 3, 5, 7, 11, 97])
    def test_primes(self, n: int) -> None:
        from servers.math_server import is_prime

        assert is_prime(n) == "True"

    @pytest.mark.parametrize("n", [-5, 0, 1, 4, 9, 100])
    def test_non_primes(self, n: int) -> None:
        from servers.math_server import is_prime

        assert is_prime(n) == "False"


class TestGcd:
    """Tests for gcd tool."""

    def test_common_case(self) -> None:
        from servers.math_server import gcd

        assert gcd(12, 18) == "6"

    def test_coprime(self) -> None:
        from servers.math_server import gcd

        assert gcd(7, 13) == "1"

    def test_zero(self) -> None:
        from servers.math_server import gcd

        assert gcd(0, 5) == "5"


class TestLcm:
    """Tests for lcm tool."""

    def test_common_case(self) -> None:
        from servers.math_server import lcm

        assert lcm(4, 6) == "12"

    def test_same_number(self) -> None:
        from servers.math_server import lcm

        assert lcm(5, 5) == "5"


class TestFactorial:
    """Tests for factorial tool."""

    def test_zero(self) -> None:
        from servers.math_server import factorial

        assert factorial(0) == "1"

    def test_positive(self) -> None:
        from servers.math_server import factorial

        assert factorial(5) == "120"

    def test_negative(self) -> None:
        from servers.math_server import factorial

        with pytest.raises(ValueError, match="n must be >= 0"):
            factorial(-1)


class TestFibonacci:
    """Tests for fibonacci tool."""

    def test_base_cases(self) -> None:
        from servers.math_server import fibonacci

        assert fibonacci(0) == "0"
        assert fibonacci(1) == "1"

    def test_sequence(self) -> None:
        from servers.math_server import fibonacci

        assert fibonacci(10) == "55"

    def test_negative(self) -> None:
        from servers.math_server import fibonacci

        with pytest.raises(ValueError, match="n must be >= 0"):
            fibonacci(-1)
