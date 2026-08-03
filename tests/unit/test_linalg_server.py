"""Unit tests for Linalg MCP server."""

import pytest


class TestVectorAdd:
    """Tests for vector_add tool."""

    def test_basic(self) -> None:
        from servers.linalg_server import vector_add

        assert vector_add("1,2,3", "4,5,6") == "5, 7, 9"

    def test_length_mismatch(self) -> None:
        from servers.linalg_server import vector_add

        with pytest.raises(ValueError, match="Vector length mismatch"):
            vector_add("1,2", "1,2,3")


class TestVectorSubtract:
    """Tests for vector_subtract tool."""

    def test_basic(self) -> None:
        from servers.linalg_server import vector_subtract

        assert vector_subtract("4,5,6", "1,2,3") == "3, 3, 3"

    def test_length_mismatch(self) -> None:
        from servers.linalg_server import vector_subtract

        with pytest.raises(ValueError, match="Vector length mismatch"):
            vector_subtract("1,2", "1,2,3")


class TestVectorDot:
    """Tests for vector_dot tool."""

    def test_basic(self) -> None:
        from servers.linalg_server import vector_dot

        assert vector_dot("1,2,3", "4,5,6") == "32"

    def test_orthogonal(self) -> None:
        from servers.linalg_server import vector_dot

        assert vector_dot("1,0", "0,1") == "0"


class TestVectorNorm:
    """Tests for vector_norm tool."""

    def test_basic(self) -> None:
        from servers.linalg_server import vector_norm

        assert vector_norm("3,4") == "5"

    def test_zero_vector(self) -> None:
        from servers.linalg_server import vector_norm

        assert vector_norm("0,0,0") == "0"


class TestMatrixMultiply:
    """Tests for matrix_multiply tool."""

    def test_basic(self) -> None:
        from servers.linalg_server import matrix_multiply

        result = matrix_multiply("1,2;3,4", "5,6;7,8")
        assert result == "19, 22; 43, 50"

    def test_shape_mismatch(self) -> None:
        from servers.linalg_server import matrix_multiply

        with pytest.raises(ValueError, match="Shape mismatch"):
            matrix_multiply("1,2,3;4,5,6", "1,2;3,4")


class TestMatrixTranspose:
    """Tests for matrix_transpose tool."""

    def test_basic(self) -> None:
        from servers.linalg_server import matrix_transpose

        assert matrix_transpose("1,2,3;4,5,6") == "1, 4; 2, 5; 3, 6"


class TestMatrixDeterminant:
    """Tests for matrix_determinant tool."""

    def test_basic(self) -> None:
        from servers.linalg_server import matrix_determinant

        assert matrix_determinant("1,2;3,4") == "-2"

    def test_non_square(self) -> None:
        from servers.linalg_server import matrix_determinant

        with pytest.raises(ValueError, match="must be square"):
            matrix_determinant("1,2,3;4,5,6")


class TestMatrixInverse:
    """Tests for matrix_inverse tool."""

    def test_basic(self) -> None:
        from servers.linalg_server import matrix_inverse

        assert matrix_inverse("1,2;3,4") == "-2, 1; 1.5, -0.5"

    def test_singular(self) -> None:
        from servers.linalg_server import matrix_inverse

        with pytest.raises(ValueError, match="singular"):
            matrix_inverse("1,2;2,4")

    def test_non_square(self) -> None:
        from servers.linalg_server import matrix_inverse

        with pytest.raises(ValueError, match="must be square"):
            matrix_inverse("1,2,3;4,5,6")
