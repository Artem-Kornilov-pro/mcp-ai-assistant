"""Unit tests for Random MCP server."""

import pytest


class TestRandomInt:
    """Tests for random_int tool."""

    def test_within_range(self) -> None:
        from servers.random_server import random_int

        for _ in range(20):
            value = int(random_int(1, 5))
            assert 1 <= value <= 5

    def test_equal_bounds(self) -> None:
        from servers.random_server import random_int

        assert random_int(3, 3) == "3"

    def test_invalid_range(self) -> None:
        from servers.random_server import random_int

        with pytest.raises(ValueError, match="min_value must be <= max_value"):
            random_int(10, 1)


class TestRandomFloat:
    """Tests for random_float tool."""

    def test_within_range(self) -> None:
        from servers.random_server import random_float

        for _ in range(20):
            value = float(random_float(0.0, 1.0))
            assert 0.0 <= value <= 1.0

    def test_invalid_range(self) -> None:
        from servers.random_server import random_float

        with pytest.raises(ValueError, match="min_value must be <= max_value"):
            random_float(5.0, 1.0)


class TestRandomChoice:
    """Tests for random_choice tool."""

    def test_picks_from_list(self) -> None:
        from servers.random_server import random_choice

        result = random_choice("a, b, c")
        assert result in {"a", "b", "c"}

    def test_empty_list(self) -> None:
        from servers.random_server import random_choice

        with pytest.raises(ValueError, match="No items provided"):
            random_choice("")


class TestShuffleList:
    """Tests for shuffle_list tool."""

    def test_same_elements(self) -> None:
        from servers.random_server import shuffle_list

        result = shuffle_list("a, b, c, d")
        assert sorted(item.strip() for item in result.split(",")) == ["a", "b", "c", "d"]

    def test_single_item(self) -> None:
        from servers.random_server import shuffle_list

        assert shuffle_list("only") == "only"


class TestRandomSample:
    """Tests for random_sample tool."""

    def test_unique_subset(self) -> None:
        from servers.random_server import random_sample

        result = random_sample("a, b, c, d, e", 3)
        items = [item.strip() for item in result.split(",")]
        assert len(items) == 3
        assert len(set(items)) == 3
        assert set(items).issubset({"a", "b", "c", "d", "e"})

    def test_zero_count(self) -> None:
        from servers.random_server import random_sample

        assert random_sample("a, b, c", 0) == ""

    def test_count_exceeds_items(self) -> None:
        from servers.random_server import random_sample

        with pytest.raises(ValueError, match="cannot exceed number of items"):
            random_sample("a, b", 5)

    def test_negative_count(self) -> None:
        from servers.random_server import random_sample

        with pytest.raises(ValueError, match="count must be >= 0"):
            random_sample("a, b", -1)
