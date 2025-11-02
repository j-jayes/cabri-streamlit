"""Overview / Dashboard Page - High-level summary and trends."""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'utils'))

from utils.data_loader import load_budget_data, filter_dataframe, COUNTRY_INFO, get_value_column
from utils.filters import create_year_range_filter, create_country_filter, create_category_filter
from utils.charts import create_time_series_chart, create_bar_chart, create_heatmap

st.set_page_config(page_title="Overview", page_icon="📊", layout="wide")

# Load data
@st.cache_data
def get_data():
    return load_budget_data()

df = get_data()

if df.empty:
    st.error("No data available")
    st.stop()

# Header
st.title("📊 Overview Dashboard")
st.markdown("High-level summary of budget data across all countries")

# Sidebar filters
st.sidebar.header("🎛️ Filters")

with st.sidebar:
    year_range = create_year_range_filter(df, key="overview_year")
    selected_countries = create_country_filter(df, key="overview_country")
    selected_categories = create_category_filter(df, key="overview_category")
    
    # Add currency toggle
    st.markdown("---")
    st.markdown("### 💱 Display Currency")
    force_usd = st.checkbox(
        "Show values in USD",
        value=len(selected_countries) > 1,
        key="force_usd_overview",
        help="When checked, displays all values in USD for easier comparison. When unchecked, uses local currency for single country views."
    )

# Apply filters
filtered_df = filter_dataframe(
    df,
    countries=selected_countries,
    year_range=year_range,
    categories=selected_categories
)

# Determine which value column to use based on user preference
if force_usd:
    value_col, unit_label = 'ValueUSD', 'million USD'
else:
    value_col, unit_label = get_value_column(filtered_df, selected_countries)

# KPI Cards
st.markdown("### 🎯 Key Metrics")
latest_year = filtered_df['FiscalYear'].max()
latest_data = filtered_df[filtered_df['FiscalYear'] == latest_year]

col1, col2, col3, col4 = st.columns(4)

# Total Revenue
revenue_data = latest_data[latest_data['IndicatorLabel'].str.contains('Total Revenue')]
total_revenue = revenue_data[value_col].sum()

with col1:
    st.metric(
        label=f"💵 Total Revenue (Latest)",
        value=f"{total_revenue:,.0f} {unit_label}",
        help=f"Sum of total revenue across selected countries ({latest_year})"
    )

# Total Expenditure
expenditure_data = latest_data[latest_data['IndicatorLabel'].str.contains('Total Expenditure')]
total_expenditure = expenditure_data[value_col].sum()

with col2:
    st.metric(
        label=f"💸 Total Expenditure (Latest)",
        value=f"{total_expenditure:,.0f} {unit_label}",
        help=f"Sum of total expenditure across selected countries ({latest_year})"
    )

# Health Allocation
health_data = latest_data[latest_data['IndicatorLabel'].str.contains('Health')]
avg_health = health_data[value_col].mean()

with col3:
    st.metric(
        label=f"🏥 Avg Health Allocation",
        value=f"{avg_health:,.0f} {unit_label}" if pd.notna(avg_health) else "N/A",
        help=f"Average health sector allocation ({latest_year})"
    )

# Debt Service
debt_data = latest_data[latest_data['IndicatorLabel'].str.contains('Debt Service')]
avg_debt = debt_data[value_col].mean()

with col4:
    st.metric(
        label=f"📊 Avg Debt Service Cost",
        value=f"{avg_debt:,.0f} {unit_label}" if pd.notna(avg_debt) else "N/A",
        help=f"Average debt service cost ({latest_year})"
    )

st.markdown("---")

# Main charts
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📈 Revenue & Expenditure Trends")
    
    # Get revenue and expenditure data
    trend_indicators = ['Total Revenue (Actual)', 'Total Expenditure (Actual)']
    trend_data = filtered_df[filtered_df['IndicatorLabel'].isin(trend_indicators)]
    
    if not trend_data.empty:
        # Aggregate by year and indicator using appropriate currency
        agg_trend = trend_data.groupby(['FiscalYear', 'IndicatorLabel'])[value_col].sum().reset_index()
        
        fig = create_time_series_chart(
            agg_trend,
            x_col='FiscalYear',
            y_col=value_col,
            color_col='IndicatorLabel',
            title=f'Total Revenue vs Expenditure Over Time ({unit_label})',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No revenue/expenditure data available for selected filters")

with col2:
    st.markdown("### 🌍 Data Coverage by Country")
    
    # Count data points per country
    coverage = filtered_df.groupby('Country').size().reset_index(name='DataPoints')
    coverage = coverage.sort_values('DataPoints', ascending=True)
    
    fig = create_bar_chart(
        coverage,
        x_col='DataPoints',
        y_col='Country',
        title='Number of Data Points',
        orientation='h',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Bottom row
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🗺️ Data Completeness Heatmap")
    
    # Create pivot for completeness
    completeness = filtered_df.groupby(['Country', 'FiscalYear']).size().reset_index(name='Count')
    
    if not completeness.empty:
        fig = create_heatmap(
            completeness,
            x_col='FiscalYear',
            y_col='Country',
            value_col='Count',
            title='Number of Indicators by Country and Year',
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for heatmap")

with col2:
    st.markdown("### 📊 Top Indicators (Latest Year)")
    
    # Get top indicators by value using appropriate currency
    top_indicators = latest_data.groupby('IndicatorLabel')[value_col].sum().reset_index()
    top_indicators = top_indicators.sort_values(value_col, ascending=False).head(10)
    
    if not top_indicators.empty:
        fig = create_bar_chart(
            top_indicators,
            x_col=value_col,
            y_col='IndicatorLabel',
            title=f'Top 10 Indicators by Total Value ({latest_year}, {unit_label})',
            orientation='h',
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for top indicators")

# Data summary
st.markdown("---")
st.markdown("### 📋 Data Summary")
col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"**Showing:** {len(filtered_df)} data points")

with col2:
    st.success(f"**Countries:** {filtered_df['Country'].nunique()}")

with col3:
    st.warning(f"**Indicators:** {filtered_df['IndicatorLabel'].nunique()}")

# Download filtered data
st.markdown("---")
st.markdown("### 💾 Export Data")
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download filtered data as CSV",
    data=csv,
    file_name=f"cabri_budget_data_{latest_year}.csv",
    mime="text/csv"
)
