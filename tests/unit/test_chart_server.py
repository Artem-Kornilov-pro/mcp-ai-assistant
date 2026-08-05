"""Unit tests for Chart MCP server."""

import os
from pathlib import Path

import pytest

os.environ["WORKSPACE_DIR"] = "./workspace"


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """Temp workspace."""
    ws = tmp_path / "workspace"
    ws.mkdir()
    os.environ["WORKSPACE_DIR"] = str(ws)
    return ws


class TestPlotLine:
    """Tests for plot_line tool."""

    def test_basic(self, workspace: Path) -> None:
        from servers.chart_server import plot_line

        result = plot_line("1,2,3", "4,5,6", "line.png", title="Test")
        assert "Chart saved" in result
        assert (workspace / "line.png").exists()

    def test_length_mismatch(self, workspace: Path) -> None:
        from servers.chart_server import plot_line

        with pytest.raises(ValueError, match="length mismatch"):
            plot_line("1,2,3", "4,5", "line.png")


class TestPlotBar:
    """Tests for plot_bar tool."""

    def test_basic(self, workspace: Path) -> None:
        from servers.chart_server import plot_bar

        result = plot_bar("a, b, c", "1,2,3", "bar.png")
        assert "Chart saved" in result
        assert (workspace / "bar.png").exists()

    def test_length_mismatch(self, workspace: Path) -> None:
        from servers.chart_server import plot_bar

        with pytest.raises(ValueError, match="length mismatch"):
            plot_bar("a, b", "1,2,3", "bar.png")


class TestPlotPie:
    """Tests for plot_pie tool."""

    def test_basic(self, workspace: Path) -> None:
        from servers.chart_server import plot_pie

        result = plot_pie("a, b, c", "1,2,3", "pie.png")
        assert "Chart saved" in result
        assert (workspace / "pie.png").exists()

    def test_negative_values(self, workspace: Path) -> None:
        from servers.chart_server import plot_pie

        with pytest.raises(ValueError, match="non-negative"):
            plot_pie("a, b", "1,-2", "pie.png")


class TestPlotScatter:
    """Tests for plot_scatter tool."""

    def test_basic(self, workspace: Path) -> None:
        from servers.chart_server import plot_scatter

        result = plot_scatter("1,2,3", "4,5,6", "scatter.png")
        assert "Chart saved" in result
        assert (workspace / "scatter.png").exists()


class TestPlotHistogram:
    """Tests for plot_histogram tool."""

    def test_basic(self, workspace: Path) -> None:
        from servers.chart_server import plot_histogram

        result = plot_histogram("1,2,2,3,3,3", "hist.png", bins=3)
        assert "Chart saved" in result
        assert (workspace / "hist.png").exists()

    def test_invalid_bins(self, workspace: Path) -> None:
        from servers.chart_server import plot_histogram

        with pytest.raises(ValueError, match="bins must be positive"):
            plot_histogram("1,2,3", "hist.png", bins=0)


class TestPlotArea:
    """Tests for plot_area tool."""

    def test_basic(self, workspace: Path) -> None:
        from servers.chart_server import plot_area

        result = plot_area("1,2,3", "4,5,6", "area.png")
        assert "Chart saved" in result
        assert (workspace / "area.png").exists()


class TestPlotMultiLine:
    """Tests for plot_multi_line tool."""

    def test_basic(self, workspace: Path) -> None:
        from servers.chart_server import plot_multi_line

        result = plot_multi_line("1,2,3", "A:1,2,3;B:4,5,6", "multi.png")
        assert "Chart saved" in result
        assert (workspace / "multi.png").exists()

    def test_invalid_series_format(self, workspace: Path) -> None:
        from servers.chart_server import plot_multi_line

        with pytest.raises(ValueError, match="Invalid series format"):
            plot_multi_line("1,2,3", "no-colon-here", "multi.png")

    def test_series_length_mismatch(self, workspace: Path) -> None:
        from servers.chart_server import plot_multi_line

        with pytest.raises(ValueError, match="length mismatch"):
            plot_multi_line("1,2,3", "A:1,2", "multi.png")


class TestPlotBoxplot:
    """Tests for plot_boxplot tool."""

    def test_single_dataset(self, workspace: Path) -> None:
        from servers.chart_server import plot_boxplot

        result = plot_boxplot("1,2,3,4,5", "box.png")
        assert "Chart saved" in result
        assert (workspace / "box.png").exists()

    def test_multiple_datasets_with_labels(self, workspace: Path) -> None:
        from servers.chart_server import plot_boxplot

        result = plot_boxplot("1,2,3;4,5,6", "box.png", labels="A, B")
        assert "Chart saved" in result

    def test_label_count_mismatch(self, workspace: Path) -> None:
        from servers.chart_server import plot_boxplot

        with pytest.raises(ValueError, match="labels count mismatch"):
            plot_boxplot("1,2,3;4,5,6", "box.png", labels="A")


class TestPlotStackedBar:
    """Tests for plot_stacked_bar tool."""

    def test_basic(self, workspace: Path) -> None:
        from servers.chart_server import plot_stacked_bar

        result = plot_stacked_bar("Q1, Q2", "A:1,2;B:3,4", "stacked.png")
        assert "Chart saved" in result
        assert (workspace / "stacked.png").exists()

    def test_series_length_mismatch(self, workspace: Path) -> None:
        from servers.chart_server import plot_stacked_bar

        with pytest.raises(ValueError, match="length mismatch"):
            plot_stacked_bar("Q1, Q2", "A:1,2,3", "stacked.png")


class TestPlotFromCsv:
    """Tests for plot_from_csv tool."""

    def test_basic(self, workspace: Path) -> None:
        from servers.chart_server import plot_from_csv

        (workspace / "data.csv").write_text("month,sales\nJan,10\nFeb,20\nMar,15\n")
        result = plot_from_csv("data.csv", "month", "sales", "from_csv.png")
        assert "Chart saved" in result
        assert (workspace / "from_csv.png").exists()

    def test_bar_chart_type(self, workspace: Path) -> None:
        from servers.chart_server import plot_from_csv

        (workspace / "data.csv").write_text("month,sales\nJan,10\nFeb,20\n")
        result = plot_from_csv("data.csv", "month", "sales", "bar.png", chart_type="bar")
        assert "Chart saved" in result

    def test_missing_file(self, workspace: Path) -> None:
        from servers.chart_server import plot_from_csv

        with pytest.raises(FileNotFoundError, match="File not found"):
            plot_from_csv("missing.csv", "x", "y", "out.png")

    def test_missing_column(self, workspace: Path) -> None:
        from servers.chart_server import plot_from_csv

        (workspace / "data.csv").write_text("month,sales\nJan,10\n")
        with pytest.raises(ValueError, match="Columns not found"):
            plot_from_csv("data.csv", "missing", "sales", "out.png")

    def test_non_numeric_column(self, workspace: Path) -> None:
        from servers.chart_server import plot_from_csv

        (workspace / "data.csv").write_text("month,sales\nJan,abc\n")
        with pytest.raises(ValueError, match="must contain numeric values"):
            plot_from_csv("data.csv", "month", "sales", "out.png")

    def test_invalid_chart_type(self, workspace: Path) -> None:
        from servers.chart_server import plot_from_csv

        (workspace / "data.csv").write_text("month,sales\nJan,10\n")
        with pytest.raises(ValueError, match="Unsupported chart_type"):
            plot_from_csv("data.csv", "month", "sales", "out.png", chart_type="pie")


class TestOutsideWorkspace:
    """Tests for sandbox enforcement."""

    def test_output_outside_workspace(self, workspace: Path) -> None:
        from servers.chart_server import plot_line

        with pytest.raises(PermissionError, match="Access denied"):
            plot_line("1,2", "3,4", "../outside.png")
