"""Data Table Page - Browse and export raw data."""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'utils'))

from utils.data_loader import load_budget_data, filter_dataframe
from utils.filters import create_country_filter, create_indicator_filter, create_year_range_filter

st.set_page_config(page_title="Data Table", page_icon="🔍", layout="wide")

# Load data
@st.cache_data
def get_data():
    return load_budget_data()

df = get_data()

if df.empty:
    st.error("No data available")
    st.stop()

# Header
st.title("🔍 Data Table")
st.markdown("Browse, search, and export the raw budget data")

# Sidebar filters
st.sidebar.header("🎛️ Filters")

with st.sidebar:
    selected_countries = create_country_filter(df, key="table_country", default_all=False)
    selected_indicators = create_indicator_filter(df, key="table_indicator", default_all=False)
    year_range = create_year_range_filter(df, key="table_year")
    
    # Add option to show USD values
    st.markdown("---")
    st.markdown("### 💱 Display Currency")
    show_usd = st.checkbox(
        "Include USD values",
        value=False,
        key="show_usd_table",
        help="When checked, adds ValueUSD column to the table for cross-country comparison."
    )

# Apply filters
filtered_df = filter_dataframe(
    df,
    countries=selected_countries if selected_countries else None,
    indicators=selected_indicators if selected_indicators else None,
    year_range=year_range
)

# Search box
search_term = st.text_input("🔎 Search all columns", placeholder="Type to search...")

if search_term:
    mask = filtered_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
    filtered_df = filtered_df[mask]

# Summary stats
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📊 Total Rows", len(filtered_df))

with col2:
    st.metric("🌍 Countries", filtered_df['Country'].nunique())

with col3:
    st.metric("📈 Indicators", filtered_df['IndicatorLabel'].nunique())

with col4:
    avg_val = filtered_df['Value'].mean()
    st.metric("💰 Avg Value", f"{avg_val:,.0f}" if pd.notna(avg_val) else "N/A")

st.markdown("---")

# Display options
col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    show_sources = st.checkbox("Show source details", value=False)

with col2:
    rows_per_page = st.selectbox("Rows per page", [25, 50, 100, 500], index=1)

# Select columns to display
display_cols = ['CountryFlag', 'Country', 'IndicatorLabel', 'Category', 'FiscalYear', 'Value', 'Unit']
if show_usd:
    display_cols.insert(7, 'ValueUSD')  # Add after Unit
if show_sources:
    display_cols.extend(['Source', 'Page'])

# Prepare display dataframe
display_df = filtered_df[display_cols].copy()
display_df = display_df.rename(columns={
    'CountryFlag': '🏳️',
    'IndicatorLabel': 'Indicator',
    'FiscalYear': 'Year'
})

# Pagination
total_rows = len(display_df)
total_pages = (total_rows // rows_per_page) + (1 if total_rows % rows_per_page > 0 else 0)

if total_pages > 1:
    page = st.slider("Page", min_value=1, max_value=total_pages, value=1)
    start_idx = (page - 1) * rows_per_page
    end_idx = start_idx + rows_per_page
    display_df = display_df.iloc[start_idx:end_idx]

# Display table
st.dataframe(
    display_df,
    use_container_width=True,
    height=600,
    hide_index=True
)

st.markdown(f"*Showing rows {start_idx + 1 if total_pages > 1 else 1} to {min(end_idx, total_rows) if total_pages > 1 else total_rows} of {total_rows}*")

# Export options
st.markdown("---")
st.markdown("### 💾 Export Options")

col1, col2 = st.columns(2)

with col1:
    # CSV export
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download as CSV",
        data=csv,
        file_name="cabri_budget_data.csv",
        mime="text/csv",
        use_container_width=True
    )

with col2:
    # Excel export
    import io
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        filtered_df.to_excel(writer, index=False, sheet_name='Budget Data')
    
    st.download_button(
        label="📥 Download as Excel",
        data=buffer.getvalue(),
        file_name="cabri_budget_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

# Data info
with st.expander("ℹ️ Column Descriptions"):
    st.markdown("""
    - **Country**: Country name
    - **Indicator**: Budget indicator name
    - **Category**: Indicator category (Revenue, Expenditure, Sectoral, Debt)
    - **Year**: Fiscal year
    - **Value**: Numeric value of the indicator in local currency
    - **Unit**: Unit of measurement for local currency
    - **ValueUSD**: Value converted to million USD (for cross-country comparison)
    - **Source**: Source document filename
    - **Page**: Page number in source document
    """)
