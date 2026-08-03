"""MCP server for linear algebra operations (vectors and matrices) using numpy."""

import numpy as np
import numpy.typing as npt
from fastmcp import FastMCP

mcp = FastMCP("Linalg")


def _parse_vector(v: str) -> npt.NDArray[np.float64]:
    """Parse a comma-separated string of numbers into a vector."""
    try:
        return np.array([float(x) for x in v.split(",")])
    except ValueError as e:
        raise ValueError(f"Invalid vector: {v}") from e


def _parse_matrix(m: str) -> npt.NDArray[np.float64]:
    """Parse a ';'-separated (rows) ','-separated (columns) string into a matrix."""
    try:
        rows = [[float(x) for x in row.split(",")] for row in m.split(";")]
    except ValueError as e:
        raise ValueError(f"Invalid matrix: {m}") from e
    matrix = np.array(rows)
    if matrix.ndim != 2:
        raise ValueError(f"Invalid matrix: {m}")
    return matrix


def _format_number(x: float) -> str:
    """Format a float, dropping unnecessary decimal noise."""
    rounded = round(float(x), 6)
    if rounded == int(rounded):
        return str(int(rounded))
    return f"{rounded:g}"


def _format_vector(v: npt.NDArray[np.float64]) -> str:
    """Format a 1D array as a comma-separated string."""
    return ", ".join(_format_number(x) for x in v)


def _format_matrix(m: npt.NDArray[np.float64]) -> str:
    """Format a 2D array as a ';'/','-separated string."""
    return "; ".join(", ".join(_format_number(x) for x in row) for row in m)


@mcp.tool()
def vector_add(v1: str, v2: str) -> str:
    """Add two vectors element-wise.

    Args:
        v1: First vector, comma-separated numbers (e.g. "1,2,3").
        v2: Second vector, comma-separated numbers.

    Returns:
        Resulting vector as comma-separated numbers.
    """
    a, b = _parse_vector(v1), _parse_vector(v2)
    if a.shape != b.shape:
        raise ValueError(f"Vector length mismatch: {a.shape[0]} vs {b.shape[0]}")
    return _format_vector(a + b)


@mcp.tool()
def vector_subtract(v1: str, v2: str) -> str:
    """Subtract one vector from another element-wise.

    Args:
        v1: First vector, comma-separated numbers.
        v2: Second vector, comma-separated numbers.

    Returns:
        Resulting vector as comma-separated numbers.
    """
    a, b = _parse_vector(v1), _parse_vector(v2)
    if a.shape != b.shape:
        raise ValueError(f"Vector length mismatch: {a.shape[0]} vs {b.shape[0]}")
    return _format_vector(a - b)


@mcp.tool()
def vector_dot(v1: str, v2: str) -> str:
    """Compute the dot product of two vectors.

    Args:
        v1: First vector, comma-separated numbers.
        v2: Second vector, comma-separated numbers.

    Returns:
        The dot product as a single number.
    """
    a, b = _parse_vector(v1), _parse_vector(v2)
    if a.shape != b.shape:
        raise ValueError(f"Vector length mismatch: {a.shape[0]} vs {b.shape[0]}")
    return _format_number(float(np.dot(a, b)))


@mcp.tool()
def vector_norm(v: str) -> str:
    """Compute the Euclidean norm (magnitude) of a vector.

    Args:
        v: Vector, comma-separated numbers.

    Returns:
        The norm as a single number.
    """
    return _format_number(float(np.linalg.norm(_parse_vector(v))))


@mcp.tool()
def matrix_multiply(m1: str, m2: str) -> str:
    """Multiply two matrices.

    Args:
        m1: First matrix, rows separated by ';', values by ',' (e.g. "1,2;3,4").
        m2: Second matrix, same format.

    Returns:
        Resulting matrix in the same format.
    """
    a, b = _parse_matrix(m1), _parse_matrix(m2)
    if a.shape[1] != b.shape[0]:
        raise ValueError(f"Shape mismatch for multiplication: {a.shape} x {b.shape}")
    return _format_matrix(a @ b)


@mcp.tool()
def matrix_transpose(m: str) -> str:
    """Transpose a matrix.

    Args:
        m: Matrix, rows separated by ';', values by ','.

    Returns:
        Transposed matrix in the same format.
    """
    return _format_matrix(_parse_matrix(m).T)


@mcp.tool()
def matrix_determinant(m: str) -> str:
    """Compute the determinant of a square matrix.

    Args:
        m: Matrix, rows separated by ';', values by ','.

    Returns:
        The determinant as a single number.
    """
    matrix = _parse_matrix(m)
    if matrix.shape[0] != matrix.shape[1]:
        raise ValueError(f"Matrix must be square, got shape {matrix.shape}")
    return _format_number(float(np.linalg.det(matrix)))


@mcp.tool()
def matrix_inverse(m: str) -> str:
    """Compute the inverse of a square matrix.

    Args:
        m: Matrix, rows separated by ';', values by ','.

    Returns:
        Inverse matrix in the same format.
    """
    matrix = _parse_matrix(m)
    if matrix.shape[0] != matrix.shape[1]:
        raise ValueError(f"Matrix must be square, got shape {matrix.shape}")
    try:
        inverse = np.linalg.inv(matrix)
    except np.linalg.LinAlgError as e:
        raise ValueError(f"Matrix is singular and has no inverse: {e}") from e
    return _format_matrix(inverse)


if __name__ == "__main__":
    mcp.run()
