import math
from decimal import Decimal, InvalidOperation
from django.utils import timezone
import pandas as pd


def safe_parse_date(value, expected_year=None):
    """Safely parse a date value and make it timezone-aware if needed."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None

    # Special handling if the value is a float (Excel day number)
    if isinstance(value, (float, int)):
        parsed = pd.to_datetime(value, origin='1899-12-30', unit='D', errors='coerce')
    else:
        parsed = pd.to_datetime(value, errors='coerce')

    if pd.isna(parsed):
        return None

    # Convert pandas Timestamp to native Python datetime
    if isinstance(parsed, pd.Timestamp):
        parsed = parsed.to_pydatetime()

    # Ensure timezone-awareness
    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed)
    
    # If the value is a string like "20-Jul", append the expected year
    if parsed is None and expected_year is not None:
        return safe_parse_date(f"{expected_year}-{value}", None)
    
    # if parsed.year < 2000:
    #     parsed.year = expected_year
        
    return parsed

def safe_decimal(value, default=Decimal('0.0')):
    """Convert to Decimal safely. Return default if value is invalid."""
    if value is None:
        return default
    if isinstance(value, float) and math.isnan(value):
        return default
    try:
        if isinstance(value, str):
            value = ''.join(c for c in value if (c.isdigit() or c in '.-'))  # keep only digits, dot, minus
        return Decimal(value)
    except (InvalidOperation, ValueError):
        return default

