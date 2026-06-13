import logging

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

logger = logging.getLogger(__name__)

_MARGIN = dict(l=0, r=0, t=35, b=0)


def plot_sales_trend(monthly_sales: dict) -> go.Figure:
    months = sorted(monthly_sales.keys())
    values = [monthly_sales[m] for m in months]
    fig = px.line(
        x=months,
        y=values,
        title="Monthly Sales Trend",
        labels={"x": "Month", "y": "Sales ($)"},
        markers=True,
    )
    fig.update_layout(margin=_MARGIN)
    return fig


def plot_product_breakdown(product_breakdown: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        product_breakdown,
        x="Product",
        y="sum",
        title="Sales by Product",
        labels={"sum": "Total Sales ($)", "Product": "Product"},
        color="Product",
    )
    fig.update_layout(showlegend=False, margin=_MARGIN)
    return fig


def plot_region_comparison(regional_breakdown: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        regional_breakdown,
        x="Region",
        y="sum",
        title="Sales by Region",
        labels={"sum": "Total Sales ($)", "Region": "Region"},
        color="Region",
    )
    fig.update_layout(showlegend=False, margin=_MARGIN)
    return fig


def plot_age_groups(age_group_breakdown: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        age_group_breakdown,
        x="AgeGroup",
        y="count",
        title="Customer Age Distribution",
        labels={"count": "Number of Customers", "AgeGroup": "Age Group"},
        color="AgeGroup",
    )
    fig.update_layout(showlegend=False, margin=_MARGIN)
    return fig


def plot_satisfaction_heatmap(satisfaction_pivot: pd.DataFrame) -> go.Figure:
    fig = px.imshow(
        satisfaction_pivot,
        title="Customer Satisfaction by Product & Region",
        labels=dict(x="Region", y="Product", color="Avg Satisfaction"),
        color_continuous_scale="RdYlGn",
        zmin=1,
        zmax=5,
        text_auto=".2f",
    )
    fig.update_layout(margin=_MARGIN)
    return fig
