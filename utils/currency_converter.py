"""
Currency conversion utilities for cross-country budget comparisons.

Exchange rates are historical annual averages from IMF, World Bank, and central banks.
For years 2015-2024: actual historical data
For year 2025: estimated based on current rates (October 2025)
"""

import re
from typing import Dict, Optional, Tuple
import pandas as pd

# Historical exchange rates to USD (local currency per USD, annual averages)
# Sources: IMF International Financial Statistics, World Bank, X-Rates
# Only currencies present in CABRI dataset: GHA, KEN, MDG, ZAF, CAF
EXCHANGE_RATES_BY_YEAR = {
    2020: {
        'ZAR': 16.46,  # South African Rand (South Africa)
        'KES': 106.45, # Kenyan Shilling (Kenya)
        'GHS': 5.60,   # Ghanaian Cedi (Ghana)
        'XOF': 575.0,  # West African CFA Franc
        'XAF': 575.0,  # Central African CFA Franc (Central African Republic)
        'MGA': 3787.0, # Malagasy Ariary (Madagascar)
        # NGN and UGX appear in some MDG files but are likely unit errors
        'NGN': 358.81, # Nigerian Naira (unit error - not used)
        'UGX': 3718.0, # Ugandan Shilling (unit error - not used)
        'USD': 1.0,
    },
    2021: {
        'ZAR': 14.78,
        'KES': 109.64,
        'GHS': 5.81,
        'XOF': 554.0,
        'XAF': 554.0,
        'MGA': 3829.0,
        'NGN': 401.15,
        'UGX': 3587.0,
        'USD': 1.0,
    },
    2022: {
        'ZAR': 16.36,
        'KES': 117.91,
        'GHS': 8.27,
        'XOF': 624.0,
        'XAF': 624.0,
        'MGA': 4112.0,
        'NGN': 416.38,
        'UGX': 3740.0,
        'USD': 1.0,
    },
    2023: {
        'ZAR': 18.45,
        'KES': 138.05,
        'GHS': 11.02,
        'XOF': 606.0,
        'XAF': 606.0,
        'MGA': 4390.0,
        'NGN': 460.68,
        'UGX': 3728.0,
        'USD': 1.0,
    },
    2024: {
        'ZAR': 18.27,
        'KES': 129.42,
        'GHS': 14.74,
        'XOF': 606.0,
        'XAF': 606.0,
        'MGA': 4508.0,
        'NGN': 1483.99,  # Major devaluation
        'UGX': 3725.0,
        'USD': 1.0,
    },
    2025: {
        'ZAR': 17.50,  # Estimated current (October 2025)
        'KES': 129.00,
        'GHS': 15.50,
        'XOF': 610.0,
        'XAF': 610.0,
        'MGA': 4550.0,
        'NGN': 1590.00,
        'UGX': 3750.0,
        'USD': 1.0,
    },
}

# Default rates (2020-2024 average) for fallback when year not specified
EXCHANGE_RATES = {
    'KES': 120.0,    # Kenyan Shilling
    'GHS': 9.0,      # Ghana Cedi
    'XOF': 593.0,    # West African CFA Franc
    'XAF': 593.0,    # Central African CFA Franc (CAF)
    'ZAR': 16.9,     # South African Rand
    'MGA': 4115.0,   # Malagasy Ariary
    # These appear in data but are likely errors:
    'NGN': 644.0,    # Nigerian Naira (not used - likely unit error in MDG)
    'UGX': 3700.0,   # Ugandan Shilling (not used - likely unit error in MDG)
    'USD': 1.0,      # US Dollar
}

# Unit multipliers
UNIT_MULTIPLIERS = {
    'million': 1e6,
    'billion': 1e9,
    'trillion': 1e12,
    'thousand': 1e3,
    '': 1.0,  # No unit specified
}

def parse_unit(unit: str) -> Tuple[str, str]:
    """
    Parse a unit string like 'billion ZAR' into magnitude and currency.
    
    Args:
        unit: Unit string (e.g., 'billion ZAR', 'million GHS', 'ZAR')
        
    Returns:
        Tuple of (magnitude, currency) where magnitude is like 'billion', 'million', etc.
    """
    unit = unit.strip().lower()
    
    # Extract currency code (3 letters, typically uppercase in original)
    currency_match = re.search(r'\b([a-z]{3})\b', unit, re.IGNORECASE)
    currency = currency_match.group(1).upper() if currency_match else 'USD'
    
    # Extract magnitude
    magnitude = ''
    for mag in ['trillion', 'billion', 'million', 'thousand']:
        if mag in unit:
            magnitude = mag
            break
    
    return magnitude, currency

def convert_to_usd(
    value: float, 
    unit: str,
    year: Optional[int] = None,
    custom_rates: Optional[Dict[str, float]] = None
) -> Tuple[float, str]:
    """
    Convert a value in local currency to USD using historical exchange rates.
    
    Args:
        value: The numeric value
        unit: Unit string (e.g., 'billion ZAR', 'million GHS')
        year: Year for exchange rate lookup (uses year-specific rates if available)
        custom_rates: Optional custom exchange rates to override defaults
        
    Returns:
        Tuple of (converted_value_in_millions_usd, 'million USD')
    """
    if pd.isna(value) or value is None:
        return None, None
    
    # Determine which rates to use
    if custom_rates:
        rates = custom_rates
    elif year and year in EXCHANGE_RATES_BY_YEAR:
        rates = EXCHANGE_RATES_BY_YEAR[year]
    else:
        rates = EXCHANGE_RATES  # Use default averages
    
    magnitude, currency = parse_unit(unit)
    
    # Get multipliers
    multiplier = UNIT_MULTIPLIERS.get(magnitude, 1.0)
    exchange_rate = rates.get(currency, 1.0)
    
    # Convert to base currency units (e.g., ZAR, GHS)
    base_value = value * multiplier
    
    # Convert to USD
    usd_value = base_value / exchange_rate
    
    # Convert to millions USD for consistency
    usd_millions = usd_value / 1e6
    
    return usd_millions, 'million USD'

def add_usd_column(df: pd.DataFrame, value_col: str = 'Value', unit_col: str = 'Unit', year_col: str = 'Year') -> pd.DataFrame:
    """
    Add USD conversion columns to a DataFrame using year-specific exchange rates.
    
    Args:
        df: DataFrame with budget data
        value_col: Name of the column containing values
        unit_col: Name of the column containing units
        year_col: Name of the column containing year (for historical exchange rates)
        
    Returns:
        DataFrame with added 'ValueUSD' and 'UnitUSD' columns
    """
    df = df.copy()
    
    # Apply conversion with year-specific rates
    conversions = df.apply(
        lambda row: convert_to_usd(
            row[value_col], 
            row[unit_col],
            year=row.get(year_col) if year_col in row.index else None
        ) if pd.notna(row[value_col]) else (None, None), 
        axis=1
    )
    
    df['ValueUSD'] = [c[0] for c in conversions]
    df['UnitUSD'] = [c[1] for c in conversions]
    
    return df


def get_exchange_rate_info() -> pd.DataFrame:
    """
    Get a DataFrame with exchange rate information for display.
    
    Returns:
        DataFrame with currency codes, rates, and descriptions
    """
    info = []
    for currency, rate in sorted(EXCHANGE_RATES.items()):
        if currency == 'USD':
            continue
        info.append({
            'Currency': currency,
            'Rate': f'{rate:,.2f}',
            'Units per USD': rate,
            'Region': _get_region(currency)
        })
    
    return pd.DataFrame(info)

def _get_region(currency: str) -> str:
    """Get region for a currency code."""
    regions = {
        'KES': 'East Africa (Kenya)',
        'GHS': 'West Africa (Ghana)',
        'XOF': 'West Africa',
        'XAF': 'Central Africa (CAF)',
        'ZAR': 'Southern Africa (South Africa)',
        'MGA': 'Indian Ocean (Madagascar)',
        # These appear in data but are unit errors:
        'NGN': 'West Africa (Nigeria) ⚠️ Unit Error',
        'UGX': 'East Africa (Uganda) ⚠️ Unit Error',
    }
    return regions.get(currency, 'Unknown')

def format_value_with_unit(value: float, unit: str, decimals: int = 2) -> str:
    """
    Format a value with its unit for display.
    
    Args:
        value: Numeric value
        unit: Unit string
        decimals: Number of decimal places
        
    Returns:
        Formatted string like "1,234.56 billion ZAR"
    """
    if pd.isna(value) or value is None:
        return "N/A"
    
    return f"{value:,.{decimals}f} {unit}"

# Example usage and tests
if __name__ == "__main__":
    print("Currency Converter Test\n")
    print("="*60)
    
    # Test cases
    test_cases = [
        (1459.7, "billion KES"),
        (2850.5, "billion KES"),
        (850.0, "million MGA"),
        (250000.0, "million ZAR"),
        (20.35, "billion ZAR"),
        (1500.0, "million GHS"),
    ]
    
    print(f"\n{'Value':<15} {'Unit':<20} {'USD (millions)':<20} {'Formatted':<30}")
    print("-"*85)
    
    for value, unit in test_cases:
        usd_value, usd_unit = convert_to_usd(value, unit)
        formatted = format_value_with_unit(usd_value, usd_unit)
        print(f"{value:<15,.2f} {unit:<20} {usd_value:<20,.2f} {formatted:<30}")
    
    print("\n" + "="*60)
    print("\nExchange Rates Used:")
    print(get_exchange_rate_info().to_string(index=False))
