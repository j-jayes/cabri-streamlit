"""Common filter components for Streamlit app."""

import streamlit as st
from typing import List, Tuple
import pandas as pd


def create_country_filter(df: pd.DataFrame, key: str = "country_filter", default_all: bool = True) -> List[str]:
    """
    Create country multi-select filter.
    
    Args:
        df: DataFrame with Country column
        key: Unique key for widget
        default_all: If True, select all countries by default
        
    Returns:
        List of selected country names
    """
    countries = sorted(df['Country'].unique())
    
    default = countries if default_all else []
    
    selected = st.multiselect(
        '🌍 Select Countries',
        options=countries,
        default=default,
        key=key,
        help='Choose one or more countries to include'
    )
    
    return selected if selected else countries


def create_indicator_filter(df: pd.DataFrame, key: str = "indicator_filter", default_all: bool = True) -> List[str]:
    """
    Create indicator multi-select filter.
    
    Args:
        df: DataFrame with IndicatorLabel column
        key: Unique key for widget
        default_all: If True, select all indicators by default
        
    Returns:
        List of selected indicator labels
    """
    indicators = sorted(df['IndicatorLabel'].unique())
    
    default = indicators if default_all else []
    
    selected = st.multiselect(
        '📊 Select Indicators',
        options=indicators,
        default=default,
        key=key,
        help='Choose one or more indicators to include'
    )
    
    return selected if selected else indicators


def create_year_range_filter(df: pd.DataFrame, key: str = "year_filter") -> Tuple[int, int]:
    """
    Create year range slider.
    
    Args:
        df: DataFrame with FiscalYear column
        key: Unique key for widget
        
    Returns:
        Tuple of (min_year, max_year)
    """
    min_year = int(df['FiscalYear'].min())
    max_year = int(df['FiscalYear'].max())
    
    selected_range = st.slider(
        '📅 Fiscal Year Range',
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        key=key,
        help='Select the range of years to include'
    )
    
    return selected_range


def create_category_filter(df: pd.DataFrame, key: str = "category_filter") -> List[str]:
    """
    Create category filter.
    
    Args:
        df: DataFrame with Category column
        key: Unique key for widget
        
    Returns:
        List of selected categories
    """
    categories = sorted(df['Category'].unique())
    
    selected = st.multiselect(
        '🏷️ Select Categories',
        options=categories,
        default=categories,
        key=key,
        help='Choose indicator categories to include'
    )
    
    return selected if selected else categories


def create_single_country_selector(df: pd.DataFrame, key: str = "single_country") -> str:
    """
    Create single country dropdown.
    
    Args:
        df: DataFrame with Country column
        key: Unique key for widget
        
    Returns:
        Selected country name
    """
    countries = sorted(df['Country'].unique())
    
    selected = st.selectbox(
        '🌍 Select Country',
        options=countries,
        key=key,
        help='Choose a country to explore'
    )
    
    return selected


def create_single_indicator_selector(df: pd.DataFrame, key: str = "single_indicator") -> str:
    """
    Create single indicator dropdown.
    
    Args:
        df: DataFrame with IndicatorLabel column
        key: Unique key for widget
        
    Returns:
        Selected indicator label
    """
    indicators = sorted(df['IndicatorLabel'].unique())
    
    selected = st.selectbox(
        '📊 Select Indicator',
        options=indicators,
        key=key,
        help='Choose an indicator to analyze'
    )
    
    return selected


def create_data_type_toggle(key: str = "data_type") -> str:
    """
    Create data type radio button.
    
    Args:
        key: Unique key for widget
        
    Returns:
        Selected data type ('All', 'Budgeted', or 'Actual')
    """
    data_type = st.radio(
        '📋 Data Type',
        options=['All', 'Budgeted', 'Actual'],
        horizontal=True,
        key=key,
        help='Filter by budgeted or actual values'
    )
    
    return data_type
