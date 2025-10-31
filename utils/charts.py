"""Reusable chart creation functions using Plotly."""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import List, Optional


def create_time_series_chart(df: pd.DataFrame,
                             x_col: str = 'FiscalYear',
                             y_col: str = 'Value',
                             color_col: str = 'Country',
                             title: str = 'Time Series',
                             height: int = 500) -> go.Figure:
    """
    Create an interactive line chart for time series data.
    
    Args:
        df: DataFrame with data
        x_col: Column name for x-axis
        y_col: Column name for y-axis
        color_col: Column name for color grouping
        title: Chart title
        height: Chart height in pixels
        
    Returns:
        Plotly Figure
    """
    fig = px.line(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        title=title,
        markers=True,
        height=height
    )
    
    fig.update_layout(
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    fig.update_traces(
        mode='lines+markers',
        marker=dict(size=8),
        line=dict(width=2)
    )
    
    return fig


def create_bar_chart(df: pd.DataFrame,
                     x_col: str,
                     y_col: str,
                     color_col: Optional[str] = None,
                     title: str = 'Bar Chart',
                     orientation: str = 'v',
                     height: int = 400) -> go.Figure:
    """
    Create a bar chart.
    
    Args:
        df: DataFrame with data
        x_col: Column name for x-axis
        y_col: Column name for y-axis
        color_col: Optional column name for color grouping
        title: Chart title
        orientation: 'v' for vertical, 'h' for horizontal
        height: Chart height in pixels
        
    Returns:
        Plotly Figure
    """
    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        title=title,
        orientation=orientation,
        height=height
    )
    
    fig.update_layout(
        showlegend=True if color_col else False,
        hovermode='closest'
    )
    
    return fig


def create_grouped_bar_chart(df: pd.DataFrame,
                             categories: List[str],
                             values_dict: dict,
                             title: str = 'Comparison',
                             height: int = 400) -> go.Figure:
    """
    Create a grouped bar chart for budgeted vs actual comparison.
    
    Args:
        df: DataFrame with data
        categories: List of category names
        values_dict: Dict with keys as group names and values as lists
        title: Chart title
        height: Chart height in pixels
        
    Returns:
        Plotly Figure
    """
    fig = go.Figure()
    
    colors = ['#4472C4', '#ED7D31']
    
    for idx, (group_name, values) in enumerate(values_dict.items()):
        fig.add_trace(go.Bar(
            name=group_name,
            x=categories,
            y=values,
            marker_color=colors[idx % len(colors)]
        ))
    
    fig.update_layout(
        title=title,
        barmode='group',
        height=height,
        hovermode='x unified'
    )
    
    return fig


def create_pie_chart(values: List[float],
                    labels: List[str],
                    title: str = 'Distribution',
                    height: int = 400) -> go.Figure:
    """
    Create a pie chart.
    
    Args:
        values: List of values
        labels: List of labels
        title: Chart title
        height: Chart height in pixels
        
    Returns:
        Plotly Figure
    """
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.3  # Donut chart
    )])
    
    fig.update_layout(
        title=title,
        height=height,
        showlegend=True
    )
    
    return fig


def create_scatter_plot(df: pd.DataFrame,
                       x_col: str,
                       y_col: str,
                       color_col: Optional[str] = None,
                       size_col: Optional[str] = None,
                       title: str = 'Scatter Plot',
                       height: int = 500) -> go.Figure:
    """
    Create a scatter plot.
    
    Args:
        df: DataFrame with data
        x_col: Column name for x-axis
        y_col: Column name for y-axis
        color_col: Optional column for color grouping
        size_col: Optional column for marker size
        title: Chart title
        height: Chart height in pixels
        
    Returns:
        Plotly Figure
    """
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        size=size_col,
        title=title,
        height=height
    )
    
    # Add diagonal line for x=y reference
    if df[x_col].notna().any() and df[y_col].notna().any():
        max_val = max(df[x_col].max(), df[y_col].max())
        min_val = min(df[x_col].min(), df[y_col].min())
        
        fig.add_trace(go.Scatter(
            x=[min_val, max_val],
            y=[min_val, max_val],
            mode='lines',
            line=dict(color='gray', dash='dash'),
            showlegend=False,
            name='Perfect Alignment'
        ))
    
    return fig


def create_heatmap(df: pd.DataFrame,
                  x_col: str,
                  y_col: str,
                  value_col: str,
                  title: str = 'Heatmap',
                  height: int = 400) -> go.Figure:
    """
    Create a heatmap.
    
    Args:
        df: DataFrame with data
        x_col: Column name for x-axis
        y_col: Column name for y-axis
        value_col: Column name for cell values
        title: Chart title
        height: Chart height in pixels
        
    Returns:
        Plotly Figure
    """
    pivot = df.pivot(index=y_col, columns=x_col, values=value_col)
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='Blues',
        hovertemplate='%{y}<br>%{x}: %{z}<extra></extra>'
    ))
    
    fig.update_layout(
        title=title,
        height=height
    )
    
    return fig


def create_multiple_line_chart(df: pd.DataFrame,
                               x_col: str,
                               indicators: List[str],
                               title: str = 'Multiple Indicators',
                               height: int = 500) -> go.Figure:
    """
    Create a line chart with multiple indicators.
    
    Args:
        df: DataFrame with data
        x_col: Column name for x-axis (usually FiscalYear)
        indicators: List of indicator column names
        title: Chart title
        height: Chart height in pixels
        
    Returns:
        Plotly Figure
    """
    fig = go.Figure()
    
    for indicator in indicators:
        if indicator in df.columns:
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=df[indicator],
                mode='lines+markers',
                name=indicator,
                line=dict(width=2),
                marker=dict(size=8)
            ))
    
    fig.update_layout(
        title=title,
        height=height,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig
