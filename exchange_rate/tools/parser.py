from decimal import Decimal

def parse_decimal(number):
    if isinstance(number, Decimal):
        return number
    return Decimal(str(number))
    