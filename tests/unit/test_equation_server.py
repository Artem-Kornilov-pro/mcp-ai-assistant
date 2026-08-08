"""Unit tests for Equation MCP server."""

from pathlib import Path

import pytest


class TestSolveEquation:
    """Tests for solve_equation tool."""

    def test_quadratic_with_explicit_zero(self) -> None:
        from servers.equation_server import solve_equation

        result = solve_equation("x**2 - 5*x + 6 = 0")
        assert result == "2, 3"

    def test_bare_expression_defaults_to_zero(self) -> None:
        from servers.equation_server import solve_equation

        result = solve_equation("x**2 - 5*x + 6")
        assert result == "2, 3"

    def test_linear(self) -> None:
        from servers.equation_server import solve_equation

        result = solve_equation("2*x + 3 = 7")
        assert result == "2"

    def test_no_solution(self) -> None:
        from servers.equation_server import solve_equation

        result = solve_equation("x - x = 1")
        assert result == "No solution"

    def test_other_variable(self) -> None:
        from servers.equation_server import solve_equation

        result = solve_equation("y**2 = 9", variable="y")
        assert result == "-3, 3"

    def test_invalid_expression(self) -> None:
        from servers.equation_server import solve_equation

        with pytest.raises(ValueError, match="Could not parse expression"):
            solve_equation("this is not math @@@")


class TestSolveQuadratic:
    """Tests for solve_quadratic tool."""

    def test_real_roots(self) -> None:
        from servers.equation_server import solve_quadratic

        result = solve_quadratic(1, -5, 6)
        assert "D = 1" in result
        assert "2" in result and "3" in result

    def test_complex_roots(self) -> None:
        from servers.equation_server import solve_quadratic

        result = solve_quadratic(1, 0, 1)
        assert "D = -4" in result
        assert "I" in result

    def test_zero_a_rejected(self) -> None:
        from servers.equation_server import solve_quadratic

        with pytest.raises(ValueError, match="non-zero"):
            solve_quadratic(0, 1, 1)


class TestSolveLinearSystem:
    """Tests for solve_linear_system tool."""

    def test_unique_solution(self) -> None:
        from servers.equation_server import solve_linear_system

        result = solve_linear_system("x + y = 5; x - y = 1", "x, y")
        assert result == "x = 3, y = 2"

    def test_no_solution(self) -> None:
        from servers.equation_server import solve_linear_system

        result = solve_linear_system("x + y = 5; x + y = 6", "x, y")
        assert result == "No solution"

    def test_underdetermined(self) -> None:
        from servers.equation_server import solve_linear_system

        result = solve_linear_system("x + y = 5", "x, y")
        assert "y" in result

    def test_empty_equations(self) -> None:
        from servers.equation_server import solve_linear_system

        with pytest.raises(ValueError, match="No equations provided"):
            solve_linear_system("", "x, y")

    def test_empty_variables(self) -> None:
        from servers.equation_server import solve_linear_system

        with pytest.raises(ValueError, match="No variables provided"):
            solve_linear_system("x = 1", "")


class TestSolveInequality:
    """Tests for solve_inequality tool."""

    def test_greater_than(self) -> None:
        from servers.equation_server import solve_inequality

        result = solve_inequality("x**2 - 4 > 0")
        assert "-2" in result and "2" in result

    def test_less_equal(self) -> None:
        from servers.equation_server import solve_inequality

        result = solve_inequality("2*x - 3 <= 5")
        assert "4" in result

    def test_missing_operator(self) -> None:
        from servers.equation_server import solve_inequality

        with pytest.raises(ValueError, match="must contain one of"):
            solve_inequality("x + 1")


class TestSimplifyExpression:
    """Tests for simplify_expression tool."""

    def test_basic_cancellation(self) -> None:
        from servers.equation_server import simplify_expression

        result = simplify_expression("(x**2 - 1)/(x - 1)")
        assert result == "x + 1"


class TestParseExprSecurity:
    """Regression tests: parse_expr must never execute arbitrary code."""

    def test_import_injection_blocked(self) -> None:
        from servers.equation_server import solve_equation

        with pytest.raises(Exception):  # noqa: B017 - any failure is acceptable, execution is not
            solve_equation("__import__('os').system('echo pwned')")

    def test_dunder_injection_in_inequality_blocked(self) -> None:
        from servers.equation_server import solve_inequality

        with pytest.raises(Exception):  # noqa: B017
            solve_inequality("__import__('os').system('echo pwned') > 0")

    def test_marker_file_not_created(self, tmp_path: Path) -> None:
        from servers.equation_server import solve_equation

        marker = tmp_path / "pwned.txt"
        payload = f"__import__('os').system('echo pwned > {marker}')"
        try:
            solve_equation(payload)
        except Exception:
            pass
        assert not marker.exists()
