"""
Countries and Currency Routes
Provides country and currency data for frontend
"""

from flask import Blueprint, jsonify
from utils.currency import (
    get_countries_with_currencies,
    get_currency_list,
    get_exchange_rates,
    convert_currency,
    get_currency_symbol
)

countries_bp = Blueprint('countries', __name__)


@countries_bp.route('/countries', methods=['GET'])
def list_countries():
    """
    Get all countries with their currencies
    
    GET /api/countries
    
    Response:
    {
        "success": true,
        "data": [
            {
                "name": "United States",
                "currencies": ["USD"],
                "currency_names": ["US Dollar"],
                "primary_currency": "USD"
            },
            ...
        ]
    }
    """
    try:
        countries = get_countries_with_currencies()
        
        return jsonify({
            'success': True,
            'data': countries,
            'count': len(countries)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to fetch countries: {str(e)}'
        }), 500


@countries_bp.route('/currencies', methods=['GET'])
def list_currencies():
    """
    Get all available currencies
    
    GET /api/currencies
    
    Response:
    {
        "success": true,
        "data": [
            {"code": "USD", "name": "US Dollar", "symbol": "$"},
            {"code": "EUR", "name": "Euro", "symbol": "€"},
            ...
        ]
    }
    """
    try:
        currencies = get_currency_list()
        
        # Add symbols to each currency
        for currency in currencies:
            currency['symbol'] = get_currency_symbol(currency['code'])
        
        return jsonify({
            'success': True,
            'data': currencies,
            'count': len(currencies)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to fetch currencies: {str(e)}'
        }), 500


@countries_bp.route('/exchange-rates/<base_currency>', methods=['GET'])
def get_rates(base_currency):
    """
    Get current exchange rates for a base currency
    
    GET /api/exchange-rates/USD
    
    Response:
    {
        "success": true,
        "data": {
            "base": "USD",
            "rates": {
                "EUR": 0.85,
                "GBP": 0.73,
                ...
            },
            "date": "2025-10-04"
        }
    }
    """
    try:
        base_currency = base_currency.upper()
        rates_data = get_exchange_rates(base_currency)
        
        if not rates_data:
            return jsonify({
                'success': False,
                'message': f'Failed to fetch exchange rates for {base_currency}'
            }), 500
        
        return jsonify({
            'success': True,
            'data': rates_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to fetch exchange rates: {str(e)}'
        }), 500


@countries_bp.route('/convert', methods=['POST'])
def convert():
    """
    Convert amount between currencies
    
    POST /api/convert
    Request Body:
    {
        "amount": 100,
        "from": "USD",
        "to": "EUR"
    }
    
    Response:
    {
        "success": true,
        "data": {
            "original_amount": 100,
            "original_currency": "USD",
            "converted_amount": 85.50,
            "target_currency": "EUR",
            "exchange_rate": 0.855
        }
    }
    """
    from flask import request
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['amount', 'from', 'to']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        amount = float(data['amount'])
        from_currency = data['from'].upper()
        to_currency = data['to'].upper()
        
        # Get exchange rates
        exchange_data = get_exchange_rates(from_currency)
        
        if not exchange_data:
            return jsonify({
                'success': False,
                'message': f'Failed to fetch exchange rates for {from_currency}'
            }), 500
        
        # Convert
        converted_amount = convert_currency(
            amount, 
            from_currency, 
            to_currency, 
            exchange_data['rates']
        )
        
        if converted_amount is None:
            return jsonify({
                'success': False,
                'message': f'Currency conversion failed for {from_currency} to {to_currency}'
            }), 500
        
        # Calculate exchange rate
        exchange_rate = exchange_data['rates'].get(to_currency, 0)
        
        return jsonify({
            'success': True,
            'data': {
                'original_amount': amount,
                'original_currency': from_currency,
                'converted_amount': converted_amount,
                'target_currency': to_currency,
                'exchange_rate': exchange_rate,
                'conversion_date': exchange_data['date']
            }
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': f'Invalid amount value: {str(e)}'
        }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Conversion failed: {str(e)}'
        }), 500
