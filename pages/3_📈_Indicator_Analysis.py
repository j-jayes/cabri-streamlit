"""Indicator Analysis Page - Cross-country comparisons."""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'utils'))

from utils.data_loader import load_budget_data, filter_dataframe, INDICATOR_INFO, get_value_column
from utils.filters import create_single_indicator_selector, create_year_range_filter, create_country_filter
from utils.charts import create_time_series_chart, create_bar_chart, create_scatter_plot

st.set_page_config(page_title="Indicator Analysis", page_icon="📈", layout="wide")

# Load data
@st.cache_data
def get_data():
    return load_budget_data()

df = get_data()

if df.empty:
    st.error("No data available")
    st.stop()

# Header
st.title("📈 Indicator Analysis")
st.markdown("Compare countries on specific budget indicators")

# Sidebar filters
st.sidebar.header("🎛️ Filters")

with st.sidebar:
    selected_indicator = create_single_indicator_selector(df, key="indicator_analysis_indicator")
    year_range = create_year_range_filter(df, key="indicator_analysis_year")
    selected_countries = create_country_filter(df, key="indicator_analysis_country")
    
    # Add currency toggle for cross-country comparisons
    st.markdown("---")
    st.markdown("### 💱 Display Currency")
    force_usd = st.checkbox(
        "Force USD for all comparisons",
        value=False,
        key="force_usd_indicator",
        help="When checked, always use USD even for single country. When unchecked, uses local currency for single country, USD for multiple countries."
    )

# Filter data
indicator_data = filter_dataframe(
    df,
    countries=selected_countries,
    indicators=[selected_indicator],
    year_range=year_range
)

# Determine which value column to use (USD for cross-country, local for single country)
if force_usd:
    value_col, unit_label = 'ValueUSD', 'million USD'
else:
    value_col, unit_label = get_value_column(indicator_data, selected_countries)

# Indicator info card
indicator_key = indicator_data['Indicator'].iloc[0] if not indicator_data.empty else None
indicator_info = INDICATOR_INFO.get(indicator_key, {})

st.markdown(f"### 📊 {selected_indicator}")
st.markdown(f"*{indicator_info.get('description', 'Budget indicator')}*")

col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_value = indicator_data[value_col].mean()
    st.metric("📊 Average Value", f"{avg_value:,.0f} {unit_label}" if pd.notna(avg_value) else "N/A")

with col2:
    max_country = indicator_data.loc[indicator_data[value_col].idxmax(), 'Country'] if not indicator_data.empty and indicator_data[value_col].max() > 0 else "N/A"
    st.metric("🏆 Highest", max_country)

with col3:
    min_country = indicator_data.loc[indicator_data[value_col].idxmin(), 'Country'] if not indicator_data.empty and indicator_data[value_col].min() > 0 else "N/A"
    st.metric("📉 Lowest", min_country)

with col4:
    countries_with_data = indicator_data['Country'].nunique()
    st.metric("🌍 Countries", f"{countries_with_data}/5")

st.markdown("---")

# Cross-country time series
st.markdown("### 📈 Time Series Comparison")

if not indicator_data.empty:
    fig = create_time_series_chart(
        indicator_data,
        x_col='FiscalYear',
        y_col=value_col,
        color_col='Country',
        title=f'{selected_indicator} - Cross-Country Comparison ({unit_label})',
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data available for selected filters")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🏅 Latest Year Ranking")
    
    latest_year = indicator_data['FiscalYear'].max()
    latest_data = indicator_data[indicator_data['FiscalYear'] == latest_year]
    latest_data = latest_data.sort_values(value_col, ascending=False)
    
    if not latest_data.empty:
        fig = create_bar_chart(
            latest_data,
            x_col=value_col,
            y_col='Country',
            title=f'{selected_indicator} - {latest_year} ({unit_label})',
            orientation='h',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data for latest year")

with col2:
    st.markdown("### 📊 Average Annual Growth Rate")
    
    # Calculate average growth rate per country
    growth_rates = []
    for country in indicator_data['Country'].unique():
        country_df = indicator_data[indicator_data['Country'] == country].sort_values('FiscalYear')
        if len(country_df) >= 2:
            first_val = country_df.iloc[0][value_col]
            last_val = country_df.iloc[-1][value_col]
            years = country_df.iloc[-1]['FiscalYear'] - country_df.iloc[0]['FiscalYear']
            if first_val > 0 and years > 0:
                avg_growth = ((last_val / first_val) ** (1/years) - 1) * 100
                growth_rates.append({'Country': country, 'Avg Growth %': round(avg_growth, 2)})
    
    if growth_rates:
        growth_df = pd.DataFrame(growth_rates).sort_values('Avg Growth %', ascending=False)
        fig = create_bar_chart(
            growth_df,
            x_col='Avg Growth %',
            y_col='Country',
            title='Average Annual Growth Rate',
            orientation='h',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data to calculate growth rates")

st.markdown("---")

# Budgeted vs Actual scatter (if applicable)
if 'budgeted' in indicator_key or 'actual' in indicator_key:
    st.markdown("### 🎯 Budgeted vs Actual Alignment")
    
    # Get corresponding budgeted/actual data
    base_indicator = indicator_key.replace('_actual', '').replace('_budgeted', '')
    budgeted_indicator = f'{base_indicator}_budgeted'
    actual_indicator = f'{base_indicator}_actual'
    
    # Use USD for cross-country comparison (or local if force_usd is false and single country)
    value_col_to_use = 'ValueUSD' if (len(selected_countries) > 1 or force_usd) else 'Value'
    comparison_unit = 'million USD' if value_col_to_use == 'ValueUSD' else 'local currency'
    
    budgeted_data = df[df['Indicator'] == budgeted_indicator][['Country', 'FiscalYear', value_col_to_use]].rename(columns={value_col_to_use: 'Budgeted'})
    actual_data = df[df['Indicator'] == actual_indicator][['Country', 'FiscalYear', value_col_to_use]].rename(columns={value_col_to_use: 'Actual'})
    
    scatter_data = pd.merge(budgeted_data, actual_data, on=['Country', 'FiscalYear'], how='inner')
    scatter_data = scatter_data[(scatter_data['FiscalYear'] >= year_range[0]) & (scatter_data['FiscalYear'] <= year_range[1])]
    scatter_data = scatter_data[scatter_data['Country'].isin(selected_countries)]
    
    if not scatter_data.empty and len(scatter_data) > 1:
        fig = create_scatter_plot(
            scatter_data,
            x_col='Budgeted',
            y_col='Actual',
            color_col='Country',
            title=f'Budgeted vs Actual Values - All Years ({comparison_unit})',
            height=450
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("📌 Points above the diagonal line indicate actual values exceeded budgeted amounts")
    else:
        st.info("Not enough budgeted/actual pair data available")

# Export
st.markdown("---")
csv = indicator_data.to_csv(index=False).encode('utf-8')
st.download_button(
    label=f"📥 Download {selected_indicator} data as CSV",
    data=csv,
    file_name=f"cabri_{indicator_key}_comparison.csv",
    mime="text/csv"
)
