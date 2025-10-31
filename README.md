# CABRI Budget Data Explorer

An interactive dashboard for exploring budget data across African countries.

## Features

- 📊 **Overview Dashboard**: High-level summary and trends across all countries
- 🌍 **Country Explorer**: Deep dive into country-specific budget data
- 📈 **Indicator Analysis**: Cross-country comparisons on specific indicators
- 🔍 **Data Table**: Browse, search, and export raw data
- 💱 **Currency Conversion**: Automatic USD conversion for cross-country comparisons

## Countries Covered

- 🇨🇫 Central African Republic (CAR)
- 🇬🇭 Ghana (GHA)
- 🇰🇪 Kenya (KEN)
- 🇲🇬 Madagascar (MDG)
- 🇿🇦 South Africa (ZAF)

## Data Coverage

- **Time Period**: 2020-2025 (fiscal years)
- **Indicators**: 14 budget indicators including:
  - Total Revenue & Expenditure (Actual & Budgeted)
  - Capital & Recurrent Expenditure
  - Health & Agriculture Allocations
  - Debt Service Costs

## Technology Stack

- **Frontend**: Streamlit
- **Visualization**: Plotly
- **Data Processing**: Pandas
- **Currency Conversion**: Historical exchange rates (IMF/World Bank)

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## Data Sources

Budget data extracted from official government budget documents for each country,
processed and cleaned for analysis.

## License

Data is sourced from public government documents. This application is for
research and educational purposes.
