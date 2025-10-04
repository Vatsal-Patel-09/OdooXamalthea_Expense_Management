"""
Currency and Country Utilities
Handles country data and currency conversions
"""

import requests
from typing import Dict, List, Optional
from functools import lru_cache

# =====================================================
# COUNTRY & CURRENCY DATA
# =====================================================

@lru_cache(maxsize=1)
def get_countries_with_currencies() -> List[Dict]:
    """
    Fetch all countries with their currencies from REST Countries API
    Cached to avoid repeated API calls
    
    Returns:
        List of countries with name and currency info
        [
            {
                "name": "United States",
                "currencies": ["USD"],
                "currency_names": ["United States dollar"]
            },
            ...
        ]
    """
    try:
        response = requests.get(
            'https://restcountries.com/v3.1/all?fields=name,currencies',
            timeout=10
        )
        response.raise_for_status()
        
        countries_data = response.json()
        countries = []
        
        for country in countries_data:
            country_name = country.get('name', {}).get('common', '')
            currencies_obj = country.get('currencies', {})
            
            if country_name and currencies_obj:
                currency_codes = list(currencies_obj.keys())
                currency_names = [
                    currencies_obj[code].get('name', '') 
                    for code in currency_codes
                ]
                
                countries.append({
                    'name': country_name,
                    'currencies': currency_codes,
                    'currency_names': currency_names,
                    'primary_currency': currency_codes[0] if currency_codes else 'USD'
                })
        
        # Sort by country name
        countries.sort(key=lambda x: x['name'])
        return countries
        
    except Exception as e:
        print(f"Error fetching countries: {str(e)}")
        # Return fallback with major countries
        return get_fallback_countries()


def get_fallback_countries() -> List[Dict]:
    """
    Fallback country list if API fails
    Major countries with their currencies
    """
    return [
        {'name': 'United States', 'currencies': ['USD'], 'currency_names': ['US Dollar'], 'primary_currency': 'USD'},
        {'name': 'United Kingdom', 'currencies': ['GBP'], 'currency_names': ['British Pound'], 'primary_currency': 'GBP'},
        {'name': 'India', 'currencies': ['INR'], 'currency_names': ['Indian Rupee'], 'primary_currency': 'INR'},
        {'name': 'Canada', 'currencies': ['CAD'], 'currency_names': ['Canadian Dollar'], 'primary_currency': 'CAD'},
        {'name': 'Australia', 'currencies': ['AUD'], 'currency_names': ['Australian Dollar'], 'primary_currency': 'AUD'},
        {'name': 'Japan', 'currencies': ['JPY'], 'currency_names': ['Japanese Yen'], 'primary_currency': 'JPY'},
        {'name': 'Germany', 'currencies': ['EUR'], 'currency_names': ['Euro'], 'primary_currency': 'EUR'},
        {'name': 'France', 'currencies': ['EUR'], 'currency_names': ['Euro'], 'primary_currency': 'EUR'},
        {'name': 'China', 'currencies': ['CNY'], 'currency_names': ['Chinese Yuan'], 'primary_currency': 'CNY'},
        {'name': 'Singapore', 'currencies': ['SGD'], 'currency_names': ['Singapore Dollar'], 'primary_currency': 'SGD'},
    ]


def get_currency_list() -> List[Dict]:
    """
    Get unique list of currencies from all countries
    
    Returns:
        [
            {"code": "USD", "name": "US Dollar"},
            {"code": "EUR", "name": "Euro"},
            ...
        ]
    """
    countries = get_countries_with_currencies()
    currencies = {}
    
    for country in countries:
        for i, code in enumerate(country['currencies']):
            if code not in currencies:
                name = country['currency_names'][i] if i < len(country['currency_names']) else code
                currencies[code] = name
    
    # Convert to list and sort
    currency_list = [
        {'code': code, 'name': name}
        for code, name in currencies.items()
    ]
    currency_list.sort(key=lambda x: x['code'])
    
    return currency_list


# =====================================================
# CURRENCY CONVERSION
# =====================================================

def get_exchange_rates(base_currency: str = 'USD') -> Optional[Dict]:
    """
    Get current exchange rates for a base currency
    Uses exchangerate-api.com
    
    Args:
        base_currency: Base currency code (e.g., 'USD')
    
    Returns:
        {
            "base": "USD",
            "rates": {
                "EUR": 0.85,
                "GBP": 0.73,
                "INR": 74.50,
                ...
            },
            "date": "2025-10-04"
        }
    """
    try:
        response = requests.get(
            f'https://api.exchangerate-api.com/v4/latest/{base_currency}',
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        return {
            'base': data.get('base'),
            'rates': data.get('rates', {}),
            'date': data.get('date')
        }
        
    except Exception as e:
        print(f"Error fetching exchange rates: {str(e)}")
        return None


def convert_currency(
    amount: float, 
    from_currency: str, 
    to_currency: str, 
    rates: Optional[Dict] = None
) -> Optional[float]:
    """
    Convert amount from one currency to another
    
    Args:
        amount: Amount to convert
        from_currency: Source currency code
        to_currency: Target currency code
        rates: Optional pre-fetched rates dict (for batch operations)
    
    Returns:
        Converted amount or None if conversion fails
    """
    if from_currency == to_currency:
        return amount
    
    try:
        # Fetch rates if not provided
        if rates is None:
            exchange_data = get_exchange_rates(from_currency)
            if not exchange_data:
                return None
            rates = exchange_data['rates']
        
        # Convert
        if to_currency in rates:
            return round(amount * rates[to_currency], 2)
        else:
            print(f"Exchange rate not found for {to_currency}")
            return None
            
    except Exception as e:
        print(f"Currency conversion error: {str(e)}")
        return None


def convert_to_company_currency(
    amount: float,
    expense_currency: str,
    company_currency: str
) -> Dict:
    """
    Convert expense amount to company's base currency
    Returns detailed conversion info
    
    Args:
        amount: Original expense amount
        expense_currency: Currency the expense was in
        company_currency: Company's base currency
    
    Returns:
        {
            "original_amount": 100.00,
            "original_currency": "EUR",
            "converted_amount": 117.50,
            "company_currency": "USD",
            "exchange_rate": 1.175,
            "conversion_date": "2025-10-04"
        }
    """
    # Same currency, no conversion needed
    if expense_currency == company_currency:
        return {
            'original_amount': amount,
            'original_currency': expense_currency,
            'converted_amount': amount,
            'company_currency': company_currency,
            'exchange_rate': 1.0,
            'conversion_date': None,
            'needs_conversion': False
        }
    
    # Get exchange rates
    exchange_data = get_exchange_rates(expense_currency)
    
    if not exchange_data:
        return {
            'original_amount': amount,
            'original_currency': expense_currency,
            'converted_amount': None,
            'company_currency': company_currency,
            'exchange_rate': None,
            'conversion_date': None,
            'error': 'Failed to fetch exchange rates',
            'needs_conversion': True
        }
    
    rates = exchange_data['rates']
    
    if company_currency not in rates:
        return {
            'original_amount': amount,
            'original_currency': expense_currency,
            'converted_amount': None,
            'company_currency': company_currency,
            'exchange_rate': None,
            'conversion_date': exchange_data['date'],
            'error': f'Exchange rate not available for {company_currency}',
            'needs_conversion': True
        }
    
    exchange_rate = rates[company_currency]
    converted_amount = round(amount * exchange_rate, 2)
    
    return {
        'original_amount': amount,
        'original_currency': expense_currency,
        'converted_amount': converted_amount,
        'company_currency': company_currency,
        'exchange_rate': exchange_rate,
        'conversion_date': exchange_data['date'],
        'needs_conversion': True
    }


# =====================================================
# VALIDATION
# =====================================================

def validate_currency_code(currency_code: str) -> bool:
    """
    Check if currency code is valid
    
    Args:
        currency_code: Currency code to validate (e.g., 'USD')
    
    Returns:
        True if valid, False otherwise
    """
    currencies = get_currency_list()
    valid_codes = [c['code'] for c in currencies]
    return currency_code.upper() in valid_codes


def get_currency_symbol(currency_code: str) -> str:
    """
    Get currency symbol for a currency code
    
    Args:
        currency_code: Currency code (e.g., 'USD')
    
    Returns:
        Currency symbol (e.g., '$')
    """
    symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'INR': '₹',
        'JPY': '¥',
        'CNY': '¥',
        'CAD': 'C$',
        'AUD': 'A$',
        'CHF': 'Fr',
        'SGD': 'S$',
    }
    return symbols.get(currency_code.upper(), currency_code)
