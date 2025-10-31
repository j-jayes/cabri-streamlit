"""About Page - Documentation and information."""

import streamlit as st

st.set_page_config(page_title="About", page_icon="ℹ️", layout="wide")

st.title("ℹ️ About CABRI Budget Data Explorer")

# Project description
st.markdown("""
### 📖 About the Project

The **CABRI Budget Data Explorer** is an interactive web application for analyzing government budget data across African countries. This tool provides easy access to fiscal indicators, enabling policy analysts, researchers, and government officials to explore budget trends, compare countries, and identify patterns.

**Data Coverage:**
- 🌍 **5 Countries**: Central African Republic, Ghana, Kenya, Madagascar, South Africa
- 📊 **14 Indicators**: Revenue, expenditure, sectoral allocations, and debt service metrics
- 📅 **Years**: 2020-2025
- 📈 **367+ Data Points** extracted from official government documents

**Built with:**
- [Streamlit](https://streamlit.io/) - Web application framework
- [Plotly](https://plotly.com/) - Interactive visualizations
- [Pandas](https://pandas.pydata.org/) - Data processing
""")

st.markdown("---")

# How to use
st.markdown("### 🚀 How to Use This App")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Navigation:**
    1. Use the sidebar to switch between pages
    2. **Overview** - High-level dashboard with key trends
    3. **Country Explorer** - Deep dive into specific countries
    4. **Indicator Analysis** - Compare countries on indicators
    5. **Data Table** - Browse and export raw data
    
    **Filtering:**
    - Use sidebar filters on each page
    - Select countries, indicators, and year ranges
    - Filters update charts instantly
    """)

with col2:
    st.markdown("""
    **Chart Interactions:**
    - 🖱️ **Hover** over charts for detailed values
    - 🔍 **Zoom** by dragging on charts
    - 📸 **Download** charts using the camera icon
    - 👁️ **Hide/Show** series by clicking legend items
    
    **Exporting:**
    - Download filtered data as CSV or Excel
    - Export charts as PNG images
    - Copy data for use in other tools
    """)

st.markdown("---")

# Indicator definitions
st.markdown("### 📊 Indicator Definitions")

indicators_info = {
    "Revenue Indicators": {
        "Total Revenue (Actual)": "Total government revenue actually collected during the fiscal year",
        "Total Revenue (Budgeted)": "Total government revenue projected/budgeted for the fiscal year"
    },
    "Expenditure Indicators": {
        "Total Expenditure (Actual)": "Total government spending actually incurred during the fiscal year",
        "Total Expenditure (Budgeted)": "Total government spending planned/budgeted for the fiscal year",
        "Capital Expenditure (Actual)": "Actual spending on infrastructure, assets, and long-term investments",
        "Capital Expenditure (Budgeted)": "Budgeted spending on infrastructure, assets, and long-term investments",
        "Recurrent Expenditure (Actual)": "Actual operational and recurring expenses (salaries, supplies, etc.)",
        "Recurrent Expenditure (Budgeted)": "Budgeted operational and recurring expenses"
    },
    "Sectoral Indicators": {
        "Health Allocation (Actual)": "Actual budget allocation to the health sector",
        "Health Allocation (Budgeted)": "Planned budget allocation to the health sector",
        "Agriculture Allocation (Actual)": "Actual budget allocation to the agriculture sector",
        "Agriculture Allocation (Budgeted)": "Planned budget allocation to the agriculture sector"
    },
    "Debt Indicators": {
        "Debt Service Cost (Actual)": "Actual cost of servicing government debt (principal + interest payments)",
        "Debt Service Cost (Budgeted)": "Projected cost of servicing government debt"
    }
}

for category, indicators in indicators_info.items():
    with st.expander(f"**{category}**"):
        for indicator, definition in indicators.items():
            st.markdown(f"- **{indicator}**: {definition}")

st.markdown("---")

# Data sources
st.markdown("### 📚 Data Sources & Methodology")

st.markdown("""
**Source Documents:**
- Government budget speeches
- Mid-year budget reviews
- Annual financial statements
- Ministry of Finance reports

**Extraction Method:**
- Documents processed using Google Document AI
- Multi-agent LLM system for data extraction
- Automated validation and sense-checking
- Manual verification against source documents

**Data Quality:**
- Values extracted from official tables and text
- Source document and page number recorded for each data point
- Time series coherence validation
- Budgeted vs actual alignment checks

**Last Updated:** October 31, 2025
""")

st.markdown("---")

# Contact and feedback
st.markdown("### 📧 Contact & Feedback")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("""
    **GitHub Repository**
    
    [CABRI-extractor-ADK](https://github.com/j-jayes/CABRI-extractor-ADK)
    
    View source code, report issues, contribute
    """)

with col2:
    st.success("""
    **Documentation**
    
    Check the repository README for:
    - Setup instructions
    - Data extraction pipeline
    - API documentation
    """)

with col3:
    st.warning("""
    **Feedback**
    
    Found an issue or have suggestions?
    
    Open an issue on GitHub or contact the development team
    """)

st.markdown("---")

# Technical details
with st.expander("🔧 Technical Details"):
    st.markdown("""
    **Technology Stack:**
    - Frontend: Streamlit 1.28+
    - Visualization: Plotly 5.17+
    - Data Processing: Pandas 2.0+
    - Deployment: Local / Streamlit Cloud
    
    **Performance Optimizations:**
    - Data caching with `@st.cache_data`
    - Lazy loading for heavy computations
    - Efficient filtering and aggregation
    - Responsive design for mobile devices
    
    **Browser Compatibility:**
    - Chrome/Edge (recommended)
    - Firefox
    - Safari
    - Mobile browsers supported
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p><strong>CABRI Budget Data Explorer</strong></p>
    <p>Developed for budget transparency and policy analysis</p>
    <p style="font-size: 0.9rem;">© 2025 | Built with ❤️ using Streamlit</p>
</div>
""", unsafe_allow_html=True)
