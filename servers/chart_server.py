"""MCP server for chart and data visualization (matplotlib)."""

import csv as csv_module
import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from fastmcp import FastMCP
from matplotlib.figure import Figure

mcp = FastMCP("Chart")


def _resolve_path(path: str) -> Path:
    """Resolve path and enforce workspace boundary."""
    workspace = Path(os.getenv("WORKSPACE_DIR", "./workspace")).resolve()
    target = (workspace / path).resolve()
    try:
        target.relative_to(workspace)
    except ValueError:
        raise PermissionError(f"Access denied: '{path}' is outside workspace")
    return target


def _parse_numbers(s: str) -> list[float]:
    """Parse a comma-separated string of numbers."""
    try:
        return [float(x) for x in s.split(",")]
    except ValueError as e:
        raise ValueError(f"Invalid numbers: {s}") from e


def _parse_labels(s: str) -> list[str]:
    """Parse a comma-separated string of labels."""
    labels = [x.strip() for x in s.split(",") if x.strip()]
    if not labels:
        raise ValueError("No labels provided")
    return labels


def _parse_series(s: str) -> list[tuple[str, list[float]]]:
    """Parse ';'-separated 'Label:v1,v2,v3' series groups."""
    groups = [g.strip() for g in s.split(";") if g.strip()]
    if not groups:
        raise ValueError("No series provided")

    result = []
    for group in groups:
        if ":" not in group:
            raise ValueError(f"Invalid series format: '{group}'. Use 'Label:v1,v2,v3'")
        label, raw_values = group.split(":", 1)
        result.append((label.strip(), _parse_numbers(raw_values)))
    return result


def _save_chart(fig: Figure, output: str) -> str:
    """Save a figure to the workspace and close it."""
    dest = _resolve_path(output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(dest, bbox_inches="tight")
    plt.close(fig)
    return f"Chart saved: {output}"


@mcp.tool()
def plot_line(
    x: str, y: str, output: str, title: str = "", xlabel: str = "", ylabel: str = ""
) -> str:
    """Create a line chart.

    Args:
        x: X-axis values, comma-separated numbers.
        y: Y-axis values, comma-separated numbers.
        output: Output image path relative to workspace (e.g. "chart.png").
        title: Chart title.
        xlabel: X-axis label.
        ylabel: Y-axis label.

    Returns:
        Confirmation message.
    """
    x_vals, y_vals = _parse_numbers(x), _parse_numbers(y)
    if len(x_vals) != len(y_vals):
        raise ValueError(f"x and y length mismatch: {len(x_vals)} vs {len(y_vals)}")

    fig, ax = plt.subplots()
    ax.plot(x_vals, y_vals, marker="o")
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.3)
    return _save_chart(fig, output)


@mcp.tool()
def plot_bar(
    labels: str, values: str, output: str, title: str = "", xlabel: str = "", ylabel: str = ""
) -> str:
    """Create a bar chart.

    Args:
        labels: Category labels, comma-separated.
        values: Bar values, comma-separated numbers.
        output: Output image path relative to workspace.
        title: Chart title.
        xlabel: X-axis label.
        ylabel: Y-axis label.

    Returns:
        Confirmation message.
    """
    label_list, value_list = _parse_labels(labels), _parse_numbers(values)
    if len(label_list) != len(value_list):
        raise ValueError(
            f"labels and values length mismatch: {len(label_list)} vs {len(value_list)}"
        )

    fig, ax = plt.subplots()
    ax.bar(label_list, value_list)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    return _save_chart(fig, output)


@mcp.tool()
def plot_pie(labels: str, values: str, output: str, title: str = "") -> str:
    """Create a pie chart.

    Args:
        labels: Slice labels, comma-separated.
        values: Slice values, comma-separated numbers.
        output: Output image path relative to workspace.
        title: Chart title.

    Returns:
        Confirmation message.
    """
    label_list, value_list = _parse_labels(labels), _parse_numbers(values)
    if len(label_list) != len(value_list):
        raise ValueError(
            f"labels and values length mismatch: {len(label_list)} vs {len(value_list)}"
        )
    if any(v < 0 for v in value_list):
        raise ValueError("Pie chart values must be non-negative")

    fig, ax = plt.subplots()
    ax.pie(value_list, labels=label_list, autopct="%1.1f%%")
    ax.set_title(title)
    return _save_chart(fig, output)


@mcp.tool()
def plot_scatter(
    x: str, y: str, output: str, title: str = "", xlabel: str = "", ylabel: str = ""
) -> str:
    """Create a scatter plot.

    Args:
        x: X-axis values, comma-separated numbers.
        y: Y-axis values, comma-separated numbers.
        output: Output image path relative to workspace.
        title: Chart title.
        xlabel: X-axis label.
        ylabel: Y-axis label.

    Returns:
        Confirmation message.
    """
    x_vals, y_vals = _parse_numbers(x), _parse_numbers(y)
    if len(x_vals) != len(y_vals):
        raise ValueError(f"x and y length mismatch: {len(x_vals)} vs {len(y_vals)}")

    fig, ax = plt.subplots()
    ax.scatter(x_vals, y_vals)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.3)
    return _save_chart(fig, output)


@mcp.tool()
def plot_histogram(
    values: str, output: str, bins: int = 10, title: str = "", xlabel: str = ""
) -> str:
    """Create a histogram.

    Args:
        values: Data values, comma-separated numbers.
        output: Output image path relative to workspace.
        bins: Number of histogram bins. Default: 10.
        title: Chart title.
        xlabel: X-axis label.

    Returns:
        Confirmation message.
    """
    value_list = _parse_numbers(values)
    if bins <= 0:
        raise ValueError("bins must be positive")

    fig, ax = plt.subplots()
    ax.hist(value_list, bins=bins, edgecolor="black")
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Frequency")
    return _save_chart(fig, output)


@mcp.tool()
def plot_area(
    x: str, y: str, output: str, title: str = "", xlabel: str = "", ylabel: str = ""
) -> str:
    """Create a filled area chart.

    Args:
        x: X-axis values, comma-separated numbers.
        y: Y-axis values, comma-separated numbers.
        output: Output image path relative to workspace.
        title: Chart title.
        xlabel: X-axis label.
        ylabel: Y-axis label.

    Returns:
        Confirmation message.
    """
    x_vals, y_vals = _parse_numbers(x), _parse_numbers(y)
    if len(x_vals) != len(y_vals):
        raise ValueError(f"x and y length mismatch: {len(x_vals)} vs {len(y_vals)}")

    fig, ax = plt.subplots()
    ax.fill_between(x_vals, y_vals, alpha=0.5)
    ax.plot(x_vals, y_vals)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.3)
    return _save_chart(fig, output)


@mcp.tool()
def plot_multi_line(
    x: str, series: str, output: str, title: str = "", xlabel: str = "", ylabel: str = ""
) -> str:
    """Create a line chart with multiple labeled series.

    Args:
        x: X-axis values, comma-separated numbers.
        series: Series definitions, ';'-separated groups of "Label:v1,v2,v3".
        output: Output image path relative to workspace.
        title: Chart title.
        xlabel: X-axis label.
        ylabel: Y-axis label.

    Returns:
        Confirmation message.
    """
    x_vals = _parse_numbers(x)

    fig, ax = plt.subplots()
    for label, y_vals in _parse_series(series):
        if len(y_vals) != len(x_vals):
            raise ValueError(f"Series '{label}' length mismatch: {len(y_vals)} vs {len(x_vals)}")
        ax.plot(x_vals, y_vals, marker="o", label=label)

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend()
    ax.grid(True, alpha=0.3)
    return _save_chart(fig, output)


@mcp.tool()
def plot_boxplot(values: str, output: str, labels: str = "", title: str = "") -> str:
    """Create a box plot for one or more datasets.

    Args:
        values: One or more datasets, ';'-separated groups of comma-separated numbers.
        output: Output image path relative to workspace.
        labels: Optional comma-separated labels, one per dataset.
        title: Chart title.

    Returns:
        Confirmation message.
    """
    groups = [g.strip() for g in values.split(";") if g.strip()]
    if not groups:
        raise ValueError("No data provided")
    datasets = [_parse_numbers(g) for g in groups]

    label_list = _parse_labels(labels) if labels else None
    if label_list and len(label_list) != len(datasets):
        raise ValueError(f"labels count mismatch: {len(label_list)} vs {len(datasets)}")

    fig, ax = plt.subplots()
    ax.boxplot(datasets)
    if label_list:
        ax.set_xticks(range(1, len(label_list) + 1))
        ax.set_xticklabels(label_list)
    ax.set_title(title)
    return _save_chart(fig, output)


@mcp.tool()
def plot_stacked_bar(
    labels: str, series: str, output: str, title: str = "", xlabel: str = "", ylabel: str = ""
) -> str:
    """Create a stacked bar chart with multiple labeled series.

    Args:
        labels: Category labels, comma-separated.
        series: Series definitions, ';'-separated groups of "Label:v1,v2,v3".
        output: Output image path relative to workspace.
        title: Chart title.
        xlabel: X-axis label.
        ylabel: Y-axis label.

    Returns:
        Confirmation message.
    """
    label_list = _parse_labels(labels)

    fig, ax = plt.subplots()
    bottom = [0.0] * len(label_list)
    for name, series_values in _parse_series(series):
        if len(series_values) != len(label_list):
            raise ValueError(
                f"Series '{name}' length mismatch: {len(series_values)} vs {len(label_list)}"
            )
        ax.bar(label_list, series_values, bottom=bottom, label=name)
        bottom = [b + v for b, v in zip(bottom, series_values, strict=True)]

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend()
    return _save_chart(fig, output)


@mcp.tool()
def plot_from_csv(
    csv_path: str,
    x_column: str,
    y_column: str,
    output: str,
    chart_type: str = "line",
    title: str = "",
) -> str:
    """Create a chart directly from columns in a CSV file.

    Args:
        csv_path: Path to .csv file relative to workspace.
        x_column: Name of the column to use for X values.
        y_column: Name of the column to use for Y values.
        output: Output image path relative to workspace.
        chart_type: One of 'line', 'bar', 'scatter'. Default: 'line'.
        title: Chart title.

    Returns:
        Confirmation message.
    """
    target = _resolve_path(csv_path)
    if not target.exists():
        raise FileNotFoundError(f"File not found: {csv_path}")

    with open(target, encoding="utf-8") as f:
        rows = list(csv_module.DictReader(f))

    if not rows:
        raise ValueError(f"CSV file is empty: {csv_path}")
    if x_column not in rows[0] or y_column not in rows[0]:
        raise ValueError(f"Columns not found. Available: {list(rows[0].keys())}")

    x_vals = [row[x_column] for row in rows]
    try:
        y_vals = [float(row[y_column]) for row in rows]
    except ValueError as e:
        raise ValueError(f"Column '{y_column}' must contain numeric values") from e

    fig, ax = plt.subplots()
    if chart_type == "line":
        ax.plot(x_vals, y_vals, marker="o")
    elif chart_type == "bar":
        ax.bar(x_vals, y_vals)
    elif chart_type == "scatter":
        ax.scatter(x_vals, y_vals)
    else:
        plt.close(fig)
        raise ValueError(f"Unsupported chart_type: {chart_type}. Use 'line', 'bar', or 'scatter'")

    ax.set_title(title)
    ax.set_xlabel(x_column)
    ax.set_ylabel(y_column)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    return _save_chart(fig, output)


if __name__ == "__main__":
    mcp.run()
