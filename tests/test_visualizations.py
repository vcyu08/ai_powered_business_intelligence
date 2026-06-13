import pandas as pd
import plotly.graph_objects as go
import pytest

from visualizations import (
    plot_age_groups,
    plot_product_breakdown,
    plot_region_comparison,
    plot_sales_trend,
    plot_satisfaction_heatmap,
)


@pytest.fixture
def product_df():
    return pd.DataFrame({
        "Product": ["Widget A", "Widget B"],
        "sum": [10000.0, 8000.0],
        "mean": [500.0, 400.0],
        "count": [20, 20],
    })


@pytest.fixture
def region_df():
    return pd.DataFrame({
        "Region": ["North", "South"],
        "sum": [9000.0, 9000.0],
        "mean": [450.0, 450.0],
        "count": [20, 20],
    })


@pytest.fixture
def age_group_df():
    return pd.DataFrame({
        "AgeGroup": ["18-25", "26-35", "36-45"],
        "count": [10, 15, 12],
        "avg_satisfaction": [4.0, 4.2, 3.9],
    })


@pytest.fixture
def satisfaction_pivot():
    return pd.DataFrame(
        {"North": [4.1, 3.8], "South": [4.3, 4.0]},
        index=pd.Index(["Widget A", "Widget B"], name="Product"),
    )


def test_plot_sales_trend_returns_figure():
    fig = plot_sales_trend({"2024-01": 1000.0, "2024-02": 1200.0})
    assert isinstance(fig, go.Figure)



def test_plot_product_breakdown_returns_figure(product_df):
    fig = plot_product_breakdown(product_df)
    assert isinstance(fig, go.Figure)


def test_plot_region_comparison_returns_figure(region_df):
    fig = plot_region_comparison(region_df)
    assert isinstance(fig, go.Figure)


def test_plot_age_groups_returns_figure(age_group_df):
    fig = plot_age_groups(age_group_df)
    assert isinstance(fig, go.Figure)


def test_plot_satisfaction_heatmap_returns_figure(satisfaction_pivot):
    fig = plot_satisfaction_heatmap(satisfaction_pivot)
    assert isinstance(fig, go.Figure)
