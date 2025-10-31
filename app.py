"""
CABRI Budget Data Explorer - Main Application

An interactive dashboard for exploring budget data across African countries.
"""

import streamlit as st
import sys
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent / 'utils'))

from utils.data_loader import load_budget_data, compute_summary_stats

# Page configuration
st.set_page_config(
    page_title="CABRI Budget Explorer",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #2E75B6;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
    }
    .stat-label {
        font-size: 1rem;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def get_data():
    """Load and cache the budget data."""
    return load_budget_data()

df = get_data()

# Main content
st.markdown('<div class="main-header">💰 CABRI Budget Data Explorer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Interactive analysis of budget data across African countries</div>', unsafe_allow_html=True)

if df.empty:
    st.error("⚠️ No data loaded. Please check the data directory path.")
    st.stop()

# Compute summary statistics
stats = compute_summary_stats(df)

# Display key metrics
st.markdown("### 📊 Quick Stats")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{stats['total_countries']}</div>
        <div class="stat-label">Countries</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{stats['total_indicators']}</div>
        <div class="stat-label">Indicators</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{stats['year_range']}</div>
        <div class="stat-label">Year Range</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{stats['data_completeness']}%</div>
        <div class="stat-label">Data Complete</div>
    </div>
    """, unsafe_allow_html=True)

# Navigation guide
st.markdown("---")
st.markdown("### 🗺️ Explore the Data")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("""
    **📊 Overview**
    
    Get a high-level summary with trends, KPIs, and data completeness across all countries.
    """)

with col2:
    st.success("""
    **🌍 Country Explorer**
    
    Deep dive into a specific country's budget data with interactive time series and comparisons.
    """)

with col3:
    st.warning("""
    **📈 Indicator Analysis**
    
    Compare countries on specific indicators and analyze cross-country patterns.
    """)

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.info("""
    **🔍 Data Table**
    
    Browse, search, and export the raw data with filters and sorting.
    """)

with col2:
    st.success("""
    **ℹ️ About**
    
    Learn about the data sources, methodology, and indicator definitions.
    """)

# Sidebar info
st.sidebar.markdown("### 💰 CABRI Budget Explorer")
st.sidebar.markdown(f"""
**Data Summary:**
- 📍 {stats['total_countries']} countries
- 📊 {stats['total_indicators']} indicators
- 📅 {stats['year_range']}
- 📈 {stats['total_data_points']} data points

**Latest data:** {stats['latest_year']}
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🚀 Quick Links")
st.sidebar.markdown("""
- [Overview](#)
- [Country Explorer](#)
- [Indicator Analysis](#)
- [Data Table](#)
- [About](#)
""")

st.sidebar.markdown("---")
st.sidebar.info("""
💡 **Tip:** Use the sidebar on each page to filter data by country, indicator, and year range.
""")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p>CABRI Budget Data Explorer | Built with Streamlit & Plotly</p>
    <p style="font-size: 0.9rem;">Data sourced from government budget documents | Last updated: 2025-10-31</p>
</div>
""", unsafe_allow_html=True)
