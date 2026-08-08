"""MCP server for solving equations, inequalities, and systems (sympy)."""

import sympy as sp
from fastmcp import FastMCP
from sympy.parsing.sympy_parser import parse_expr

mcp = FastMCP("Equation")

# sympy.parsing.sympy_parser.parse_expr evaluates the parsed expression with
# Python's eval() under the hood. With the default (None) global_dict, Python
# auto-injects the real builtins, which makes arbitrary code execution
# possible (e.g. "__import__('os').system(...)"). Build the sympy namespace
# once and explicitly strip __builtins__ so eval() has no access to them.
_SAFE_GLOBALS: dict[str, object] = {}
exec("from sympy import *", _SAFE_GLOBALS)  # noqa: S102
_SAFE_GLOBALS["__builtins__"] = {}

_RELATIONS = {">=": sp.Ge, "<=": sp.Le, ">": sp.Gt, "<": sp.Lt}


def _parse(text: str) -> sp.Expr:
    """Safely parse a math expression string into a sympy expression."""
    try:
        return parse_expr(text, global_dict=_SAFE_GLOBALS, local_dict=None)
    except Exception as e:
        raise ValueError(f"Could not parse expression '{text}': {e}") from e


def _split_equation(text: str) -> tuple[str, str]:
    """Split 'lhs = rhs' into (lhs, rhs); bare expressions default rhs to '0'."""
    if "=" in text:
        lhs, rhs = text.split("=", 1)
        return lhs, rhs
    return text, "0"


@mcp.tool()
def solve_equation(equation: str, variable: str = "x") -> str:
    """Solve an equation for a variable.

    Args:
        equation: Equation as text, e.g. "x**2 - 5*x + 6 = 0" (the "= 0" part
            is optional). Supports standard math notation: **, *, /, sqrt(), sin(), etc.
        variable: Variable to solve for. Default: 'x'.

    Returns:
        Comma-separated solutions (exact symbolic form), or a message if none exist.
    """
    lhs, rhs = _split_equation(equation)
    symbol = sp.Symbol(variable)
    solutions = sp.solve(sp.Eq(_parse(lhs), _parse(rhs)), symbol)

    if not solutions:
        return "No solution"
    return ", ".join(str(sol) for sol in solutions)


@mcp.tool()
def solve_quadratic(a: float, b: float, c: float) -> str:
    """Solve a quadratic equation a*x^2 + b*x + c = 0.

    Args:
        a: Coefficient of x^2 (must be non-zero).
        b: Coefficient of x.
        c: Constant term.

    Returns:
        Discriminant and roots (real or complex).
    """
    if a == 0:
        raise ValueError("a must be non-zero for a quadratic equation")

    x = sp.Symbol("x")
    discriminant = b**2 - 4 * a * c
    roots = sp.solve(sp.Eq(a * x**2 + b * x + c, 0), x)

    return f"D = {discriminant}\nRoots: {', '.join(str(r) for r in roots)}"


@mcp.tool()
def solve_linear_system(equations: str, variables: str) -> str:
    """Solve a system of linear equations.

    Args:
        equations: ';'-separated equations, e.g. "x + y = 5; x - y = 1".
        variables: Comma-separated variable names, e.g. "x, y".

    Returns:
        Solution as "var = value" pairs, or a message if there is no unique solution.
    """
    eq_texts = [e.strip() for e in equations.split(";") if e.strip()]
    if not eq_texts:
        raise ValueError("No equations provided")

    var_names = [v.strip() for v in variables.split(",") if v.strip()]
    if not var_names:
        raise ValueError("No variables provided")

    symbols = sp.symbols(var_names)

    eqs = []
    for eq_text in eq_texts:
        lhs, rhs = _split_equation(eq_text)
        eqs.append(sp.Eq(_parse(lhs), _parse(rhs)))

    result = sp.linsolve(eqs, symbols)
    if not result:
        return "No solution"

    solution = next(iter(result))
    return ", ".join(f"{name} = {value}" for name, value in zip(var_names, solution, strict=True))


@mcp.tool()
def solve_inequality(inequality: str, variable: str = "x") -> str:
    """Solve an inequality for a variable.

    Args:
        inequality: Inequality as text using >, <, >=, or <=, e.g. "x**2 - 4 > 0".
        variable: Variable to solve for. Default: 'x'.

    Returns:
        Solution set (interval notation).
    """
    op = next((candidate for candidate in _RELATIONS if candidate in inequality), None)
    if op is None:
        raise ValueError("Inequality must contain one of: >, <, >=, <=")

    lhs, rhs = inequality.split(op, 1)
    symbol = sp.Symbol(variable)
    relation = _RELATIONS[op](_parse(lhs), _parse(rhs))

    result = sp.solve_univariate_inequality(relation, symbol, relational=False)
    return str(result)


@mcp.tool()
def simplify_expression(expression: str) -> str:
    """Simplify a symbolic math expression.

    Args:
        expression: Expression as text, e.g. "(x**2 - 1)/(x - 1)".

    Returns:
        Simplified expression.
    """
    return str(sp.simplify(_parse(expression)))


if __name__ == "__main__":
    mcp.run()
