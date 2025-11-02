"""
Data loading and caching utilities for CABRI Budget Explorer.

Handles loading JSON files, converting to DataFrames, and computing derived metrics.
"""

import json
from pathlib import Path
from typing import Dict, List
import pandas as pd
import streamlit as st
from .currency_converter import add_usd_column


# Country metadata
COUNTRY_INFO = {
    'CAF': {'name': 'Central African Republic', 'color': '#E74C3C', 'flag': '🇨🇫', 'currency': 'XAF', 'currency_name': 'CFA franc'},
    'GHA': {'name': 'Ghana', 'color': '#F39C12', 'flag': '🇬🇭', 'currency': 'GHS', 'currency_name': 'Ghanaian cedi'},
    'KEN': {'name': 'Kenya', 'color': '#27AE60', 'flag': '#🇰🇪', 'currency': 'KES', 'currency_name': 'Kenyan shilling'},
    'MDG': {'name': 'Madagascar', 'color': '#3498DB', 'flag': '🇲🇬', 'currency': 'MGA', 'currency_name': 'Malagasy ariary'},
    'ZAF': {'name': 'South Africa', 'color': '#9B59B6', 'flag': '🇿🇦', 'currency': 'ZAR', 'currency_name': 'South African rand'}
}

# Indicator metadata
INDICATOR_INFO = {
    'total_revenue_actual': {
        'label': 'Total Revenue (Actual)',
        'category': 'Revenue',
        'description': 'Total government revenue collected'
    },
    'total_revenue_budgeted': {
        'label': 'Total Revenue (Budgeted)',
        'category': 'Revenue',
        'description': 'Total government revenue budgeted'
    },
    'total_expenditure_actual': {
        'label': 'Total Expenditure (Actual)',
        'category': 'Expenditure',
        'description': 'Total government expenditure incurred'
    },
    'total_expenditure_budgeted': {
        'label': 'Total Expenditure (Budgeted)',
        'category': 'Expenditure',
        'description': 'Total government expenditure budgeted'
    },
    'capital_expenditure_actual': {
        'label': 'Capital Expenditure (Actual)',
        'category': 'Expenditure',
        'description': 'Actual spending on infrastructure and assets'
    },
    'capital_expenditure_budgeted': {
        'label': 'Capital Expenditure (Budgeted)',
        'category': 'Expenditure',
        'description': 'Budgeted spending on infrastructure and assets'
    },
    'recurrent_expenditure_actual': {
        'label': 'Recurrent Expenditure (Actual)',
        'category': 'Expenditure',
        'description': 'Actual recurring operational expenses'
    },
    'recurrent_expenditure_budgeted': {
        'label': 'Recurrent Expenditure (Budgeted)',
        'category': 'Expenditure',
        'description': 'Budgeted recurring operational expenses'
    },
    'health_allocation_actual': {
        'label': 'Health Allocation (Actual)',
        'category': 'Sectoral',
        'description': 'Actual allocation to health sector'
    },
    'health_allocation_budgeted': {
        'label': 'Health Allocation (Budgeted)',
        'category': 'Sectoral',
        'description': 'Budgeted allocation to health sector'
    },
    'agriculture_allocation_actual': {
        'label': 'Agriculture Allocation (Actual)',
        'category': 'Sectoral',
        'description': 'Actual allocation to agriculture sector'
    },
    'agriculture_allocation_budgeted': {
        'label': 'Agriculture Allocation (Budgeted)',
        'category': 'Sectoral',
        'description': 'Budgeted allocation to agriculture sector'
    },
    'debt_service_cost_actual': {
        'label': 'Debt Service Cost (Actual)',
        'category': 'Debt',
        'description': 'Actual cost of servicing government debt'
    },
    'debt_service_cost_budgeted': {
        'label': 'Debt Service Cost (Budgeted)',
        'category': 'Debt',
        'description': 'Budgeted cost of servicing government debt'
    },
}


@st.cache_data
def load_budget_data(data_dir: str = None) -> pd.DataFrame:
    """
    Load all budget data from JSON files into a single DataFrame.
    
    Args:
        data_dir: Directory containing JSON files (defaults to cleaned data)
        
    Returns:
        DataFrame with columns: Country, CountryISO, Indicator, IndicatorLabel,
                                FiscalYear, Value, Unit, Source, Page, Category
    """
    if data_dir is None:
        # Resolve path relative to the project root
        data_dir = Path(__file__).parent.parent / 'data' / 'extracted_clean' / 'by_country_indicator'
    
    data_path = Path(data_dir)
    
    if not data_path.exists():
        st.error(f"Data directory not found: {data_path}")
        return pd.DataFrame()
    
    all_data = []
    json_files = list(data_path.glob('*.json'))
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            country_iso = data.get('country_iso')
            indicator = data.get('indicator')
            
            for year_entry in data.get('years', []):
                fiscal_year = year_entry.get('fiscal_year')
                indicator_data = year_entry.get(indicator)
                
                if indicator_data:
                    value = indicator_data.get('value')
                    unit = indicator_data.get('unit', '')
                    data_type = indicator_data.get('data_type', '')
                    
                    all_data.append({
                        'CountryISO': country_iso,
                        'Country': COUNTRY_INFO.get(country_iso, {}).get('name', country_iso),
                        'CountryFlag': COUNTRY_INFO.get(country_iso, {}).get('flag', ''),
                        'CountryColor': COUNTRY_INFO.get(country_iso, {}).get('color', '#333333'),
                        'Indicator': indicator,
                        'IndicatorLabel': INDICATOR_INFO.get(indicator, {}).get('label', indicator),
                        'Category': INDICATOR_INFO.get(indicator, {}).get('category', 'Other'),
                        'FiscalYear': fiscal_year,
                        'Value': value,
                        'Unit': unit,
                        'DataType': data_type,
                        'Source': indicator_data.get('source_document', ''),
                        'Page': indicator_data.get('source_page', '')
                    })
        except Exception as e:
            st.warning(f"Error loading {json_file.name}: {e}")
    
    df = pd.DataFrame(all_data)
    
    # Sort for better display
    if not df.empty:
        df = df.sort_values(['Country', 'Category', 'IndicatorLabel', 'FiscalYear'])
        
        # Add USD conversion for cross-country comparisons
        df = add_usd_column(df, value_col='Value', unit_col='Unit')
    
    return df


@st.cache_data
def compute_summary_stats(df: pd.DataFrame) -> Dict:
    """Compute summary statistics for the dashboard."""
    if df.empty:
        return {}
    
    latest_year = df['FiscalYear'].max()
    latest_data = df[df['FiscalYear'] == latest_year]
    
    return {
        'total_countries': df['Country'].nunique(),
        'total_indicators': df['IndicatorLabel'].nunique(),
        'year_range': f"{df['FiscalYear'].min()}-{df['FiscalYear'].max()}",
        'total_data_points': len(df),
        'data_completeness': round(len(df) / (df['Country'].nunique() * df['Indicator'].nunique() * 6) * 100, 1),
        'latest_year': latest_year,
        'countries_list': sorted(df['Country'].unique()),
        'indicators_list': sorted(df['IndicatorLabel'].unique()),
    }


@st.cache_data
def compute_growth_rates(df: pd.DataFrame) -> pd.DataFrame:
    """Compute year-over-year growth rates for all indicators."""
    if df.empty:
        return pd.DataFrame()
    
    df_sorted = df.sort_values(['CountryISO', 'Indicator', 'FiscalYear'])
    
    # Group by country and indicator
    df_sorted['PrevValue'] = df_sorted.groupby(['CountryISO', 'Indicator'])['Value'].shift(1)
    df_sorted['GrowthRate'] = ((df_sorted['Value'] - df_sorted['PrevValue']) / df_sorted['PrevValue'] * 100).round(2)
    
    return df_sorted


def filter_dataframe(df: pd.DataFrame,
                     countries: List[str] = None,
                     indicators: List[str] = None,
                     year_range: tuple = None,
                     categories: List[str] = None) -> pd.DataFrame:
    """
    Apply filters to DataFrame.
    
    Args:
        df: Input DataFrame
        countries: List of country names to include
        indicators: List of indicator labels to include
        year_range: Tuple of (min_year, max_year)
        categories: List of categories to include
        
    Returns:
        Filtered DataFrame
    """
    filtered = df.copy()
    
    if countries:
        filtered = filtered[filtered['Country'].isin(countries)]
    
    if indicators:
        filtered = filtered[filtered['IndicatorLabel'].isin(indicators)]
    
    if year_range:
        min_year, max_year = year_range
        filtered = filtered[(filtered['FiscalYear'] >= min_year) & (filtered['FiscalYear'] <= max_year)]
    
    if categories:
        filtered = filtered[filtered['Category'].isin(categories)]
    
    return filtered


def get_country_color(country_iso: str) -> str:
    """Get color for a country."""
    return COUNTRY_INFO.get(country_iso, {}).get('color', '#333333')


def get_indicator_label(indicator: str) -> str:
    """Get display label for indicator."""
    return INDICATOR_INFO.get(indicator, {}).get('label', indicator)


def get_indicator_category(indicator: str) -> str:
    """Get category for indicator."""
    return INDICATOR_INFO.get(indicator, {}).get('category', 'Other')


def get_currency_name_for_country(country_iso: str) -> str:
    """Get the currency name for a specific country."""
    return COUNTRY_INFO.get(country_iso, {}).get('currency_name', 'local currency')


def get_value_column(df: pd.DataFrame, selected_countries: List[str] = None) -> tuple[str, str]:
    """
    Determine which value column to use based on number of countries selected.
    
    For cross-country comparisons, we must use USD to make values comparable.
    For single-country analysis, we can use local currency.
    
    Args:
        df: DataFrame with budget data
        selected_countries: List of selected country names
        
    Returns:
        Tuple of (value_column_name, unit_description)
        e.g., ('ValueUSD', 'million USD') or ('Value', 'billion KES')
    """
    if selected_countries is None:
        # Get unique countries from the filtered data
        num_countries = df['Country'].nunique()
    else:
        num_countries = len(selected_countries)
    
    # Use USD for cross-country comparisons
    if num_countries > 1:
        return ('ValueUSD', 'million USD')
    else:
        # Use local currency for single country - get the actual currency from the data
        if not df.empty and 'Unit' in df.columns:
            # Get the most common unit for this country
            unit = df['Unit'].mode().iloc[0] if len(df['Unit'].mode()) > 0 else 'local currency'
            return ('Value', unit)
        return ('Value', 'local currency')
