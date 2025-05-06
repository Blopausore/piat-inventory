import math
from decimal import Decimal, InvalidOperation
from django.utils import timezone
import pandas as pd

from core.common.models import Currency
from core.common.mappings.units import UNIT_MAPPING
from core.common.mappings.currency import CURRENCY_MAPPING

# def parse_int(value): 
    
#     if isinstance(value, str):
#         value = ''.join(d for d in value if d.isdigit())
#         if value == '':
#             return None
#     return int(value)

def parse_int(value):
    if isinstance(value, str):
        try:
            return int(float(value))
        except ValueError:
            digits = ''.join(ch for ch in value if ch.isdigit())
            return int(digits) if digits else None
    return int(value)

def parse_date(value, expected_year=None):
    """Safely parse a date value and make it timezone-aware if needed."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    # Special handling if the value is a float (Excel day number)
    if isinstance(value, (float, int)):
        parsed = pd.to_datetime(value, origin='1899-12-30', unit='D', errors='coerce')
    else:
        parsed = pd.to_datetime(value, errors='coerce')

    if pd.isna(parsed):
        raise ValueError(f"Invalid date format '{value}'. ")

    # Convert pandas Timestamp to native Python datetime
    if isinstance(parsed, pd.Timestamp):
        parsed = parsed.to_pydatetime()

    # Ensure timezone-awareness
    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed)
    
    # If the value is a string like "20-Jul", append the expected year
    if parsed is None and expected_year is not None:
        return parse_date(f"{expected_year}-{value}", None)
        
    return parsed

def parse_decimal(value, default=Decimal('0.0')):
    """Convert to Decimal safely. Return default if value is invalid."""
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    try:
        if isinstance(value, str):
            value = ''.join(c for c in value if (c.isdigit() or c in '.-'))  # keep only digits, dot, minus
        elif isinstance(value, float):
            value = str(round(value, ndigits=5))
        return Decimal(value)
    except (InvalidOperation, ValueError):
        return None

def parse_currency(raw: str) -> Currency:
    """
    Normalize a notation for a currency
    """
    if not raw:
        raise ValueError("No currency provided")
    txt = raw.strip().upper()

    if txt in CURRENCY_MAPPING.keys():
        return Currency(txt)

    for canon, aliases in CURRENCY_MAPPING.items():
        if txt in aliases:
            return Currency(canon)
    raise ValueError(f"Unknown currency: '{raw}'")



def parse_unit(raw: str) -> str:
    """
    Clean `raw` and send back a canonical unit :
      CT, G, KG, PC, TOTAL

    Raises:
      ValueError if `raw` is empty or not recognize.
    """
    if not raw:
        raise ValueError("No unit provided")
    txt = raw.strip() 

    for canon, aliases in UNIT_MAPPING.items():
        if txt in aliases:
            return canon

    raise ValueError(f"Unknown unit: '{raw}'")
