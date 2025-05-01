from datetime import datetime
from decimal import Decimal, InvalidOperation

from exchange_rate.models import ExchangeRate
from exchange_rate.tools.parser import parse_decimal

class CurrencyConversionError(Exception):
    pass

def _to_decimal(amount):
    try:
        return parse_decimal(amount)    
    except (InvalidOperation, ValueError):
        raise CurrencyConversionError(f"Invalid amount for conversion: {amount}")

def _normalize_date(dt):
    return dt.date() if isinstance(dt, datetime) else dt

def convert_from_usd(amount, date, to_currency='THB') -> Decimal:
    amount = _to_decimal(amount)    

    if to_currency.upper() == 'USD':
        return amount
    
    date = _normalize_date(date)

    try:
        rate = ExchangeRate.objects.get(date=date, base_currency=to_currency)
    except ExchangeRate.DoesNotExist:
        raise CurrencyConversionError(f"No exchange rate available for {date} for {to_currency}")
    return (amount * rate.price).quantize(Decimal('0.0001'))


def convert_to_usd(amount, date, from_currency='THB') -> Decimal:
    amount = _to_decimal(amount)    
    
    if from_currency.upper() == 'USD':
        return amount
    
    date = _normalize_date(date)

    try:
        rate = ExchangeRate.objects.get(date=date, base_currency=from_currency)
    except ExchangeRate.DoesNotExist:
        raise CurrencyConversionError(f"No exchange rate available for {date} for {from_currency}")
    return (amount * rate.inverse_price).quantize(Decimal('0.0001'))

def convert(amount, date, from_currency='THB', to_currency='USD') -> Decimal:
    if from_currency == 'USD':
        return convert_from_usd(amount, date, to_currency)
    elif to_currency == 'USD':
        return convert_to_usd(amount, date, from_currency)
    
    usd_amount = convert_to_usd(amount, date, from_currency)
    return convert_from_usd(usd_amount, date, to_currency)

