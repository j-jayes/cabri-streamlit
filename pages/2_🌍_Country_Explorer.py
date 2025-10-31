"""Country Explorer Page - Deep dive into country-specific data."""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'utils'))

from utils.data_loader import load_budget_data, filter_dataframe, COUNTRY_INFO
from utils.filters import create_single_country_selector, create_year_range_filter, create_indicator_filter
from utils.charts import create_time_series_chart, create_grouped_bar_chart, create_pie_chart

st.set_page_config(page_title="Country Explorer", page_icon="🌍", layout="wide")

# Load data
@st.cache_data
def get_data():
    return load_budget_data()

df = get_data()

if df.empty:
    st.error("No data available")
    st.stop()

# Header
st.title("🌍 Country Explorer")
st.markdown("Deep dive into country-specific budget data")

# Sidebar filters
st.sidebar.header("🎛️ Filters")

with st.sidebar:
    selected_country = create_single_country_selector(df, key="country_explorer_country")
    year_range = create_year_range_filter(df, key="country_explorer_year")
    selected_indicators = create_indicator_filter(df, key="country_explorer_indicator")

# Filter data for selected country
country_data = filter_dataframe(
    df,
    countries=[selected_country],
    year_range=year_range,
    indicators=selected_indicators
)

# Get country info
country_iso = country_data['CountryISO'].iloc[0] if not country_data.empty else None
country_info = COUNTRY_INFO.get(country_iso, {})

# Country profile card
st.markdown(f"### {country_info.get('flag', '')} {selected_country}")

latest_year = country_data['FiscalYear'].max()
latest_data = country_data[country_data['FiscalYear'] == latest_year]

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_revenue = latest_data[latest_data['IndicatorLabel'].str.contains('Total Revenue')]['Value'].sum()
    st.metric("💵 Total Revenue", f"{total_revenue:,.0f}" if pd.notna(total_revenue) and total_revenue > 0 else "N/A")

with col2:
    total_exp = latest_data[latest_data['IndicatorLabel'].str.contains('Total Expenditure')]['Value'].sum()
    st.metric("💸 Total Expenditure", f"{total_exp:,.0f}" if pd.notna(total_exp) and total_exp > 0 else "N/A")

with col3:
    indicators_available = country_data['IndicatorLabel'].nunique()
    st.metric("📊 Indicators Available", f"{indicators_available}/14")

with col4:
    years_available = country_data['FiscalYear'].nunique()
    st.metric("📅 Years of Data", f"{years_available}")

st.markdown("---")

# Time series chart
st.markdown("### 📈 Time Series - All Indicators")

if not country_data.empty:
    fig = create_time_series_chart(
        country_data,
        x_col='FiscalYear',
        y_col='Value',
        color_col='IndicatorLabel',
        title=f'{selected_country} - Budget Indicators Over Time',
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data available for selected filters")

st.markdown("---")

# Budgeted vs Actual comparison
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 💰 Budgeted vs Actual (Latest Year)")
    
    # Get budgeted and actual pairs
    budgeted_actual_pairs = []
    for indicator in country_data['Indicator'].unique():
        base_name = indicator.replace('_actual', '').replace('_budgeted', '')
        budgeted_actual_pairs.append(base_name)
    
    # For each unique base indicator, get budgeted and actual
    comparison_data = []
    for base in set(budgeted_actual_pairs):
        budgeted = latest_data[latest_data['Indicator'] == f'{base}_budgeted']['Value'].sum()
        actual = latest_data[latest_data['Indicator'] == f'{base}_actual']['Value'].sum()
        
        if budgeted > 0 or actual > 0:
            label = latest_data[latest_data['Indicator'].str.contains(base)]['IndicatorLabel'].iloc[0] if len(latest_data[latest_data['Indicator'].str.contains(base)]) > 0 else base
            label = label.replace(' (Actual)', '').replace(' (Budgeted)', '')
            comparison_data.append({
                'Indicator': label,
                'Budgeted': budgeted if budgeted > 0 else 0,
                'Actual': actual if actual > 0 else 0
            })
    
    if comparison_data:
        comp_df = pd.DataFrame(comparison_data)
        
        import plotly.graph_objects as go
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Budgeted', x=comp_df['Indicator'], y=comp_df['Budgeted'], marker_color='#4472C4'))
        fig.add_trace(go.Bar(name='Actual', x=comp_df['Indicator'], y=comp_df['Actual'], marker_color='#ED7D31'))
        fig.update_layout(
            title=f'Budgeted vs Actual - {latest_year}',
            barmode='group',
            height=400,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No budgeted/actual comparison data available")

with col2:
    st.markdown("### 🥧 Sectoral Allocation (Latest Year)")
    
    # Get sectoral allocations - separate budgeted from actual
    sector_actual = latest_data[(latest_data['Category'] == 'Sectoral') & (latest_data['IndicatorLabel'].str.contains('Actual'))]
    sector_budgeted = latest_data[(latest_data['Category'] == 'Sectoral') & (latest_data['IndicatorLabel'].str.contains('Budgeted'))]
    
    # Use tabs to show both
    tab1, tab2 = st.tabs(["Actual", "Budgeted"])
    
    with tab1:
        if not sector_actual.empty:
            # Clean labels - remove (Actual) suffix
            labels = [label.replace(' (Actual)', '') for label in sector_actual['IndicatorLabel'].tolist()]
            fig = create_pie_chart(
                values=sector_actual['Value'].tolist(),
                labels=labels,
                title=f'Sectoral Allocation (Actual) - {latest_year}',
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No actual sectoral allocation data available")
    
    with tab2:
        if not sector_budgeted.empty:
            # Clean labels - remove (Budgeted) suffix
            labels = [label.replace(' (Budgeted)', '') for label in sector_budgeted['IndicatorLabel'].tolist()]
            fig = create_pie_chart(
                values=sector_budgeted['Value'].tolist(),
                labels=labels,
                title=f'Sectoral Allocation (Budgeted) - {latest_year}',
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No budgeted sectoral allocation data available")

st.markdown("---")

# Year-over-year growth
st.markdown("### 📊 Year-over-Year Growth Rates")

# Calculate growth rates
growth_data = []
for indicator in country_data['IndicatorLabel'].unique():
    indicator_df = country_data[country_data['IndicatorLabel'] == indicator].sort_values('FiscalYear')
    for i in range(1, len(indicator_df)):
        prev_val = indicator_df.iloc[i-1]['Value']
        curr_val = indicator_df.iloc[i]['Value']
        if prev_val > 0:
            growth = ((curr_val - prev_val) / prev_val * 100)
            growth_data.append({
                'Indicator': indicator,
                'Year': indicator_df.iloc[i]['FiscalYear'],
                'Growth %': round(growth, 2)
            })

if growth_data:
    growth_df = pd.DataFrame(growth_data)
    pivot_growth = growth_df.pivot(index='Indicator', columns='Year', values='Growth %')
    
    # Style the dataframe
    def color_negative_red(val):
        color = 'red' if val < 0 else 'green' if val > 0 else 'black'
        return f'color: {color}'
    
    styled_df = pivot_growth.style.applymap(color_negative_red).format("{:.1f}%", na_rep="N/A")
    st.dataframe(styled_df, use_container_width=True)
else:
    st.info("Not enough data to calculate growth rates")

# Export country data
st.markdown("---")
csv = country_data.to_csv(index=False).encode('utf-8')
st.download_button(
    label=f"📥 Download {selected_country} data as CSV",
    data=csv,
    file_name=f"cabri_{country_iso}_{latest_year}.csv",
    mime="text/csv"
)
