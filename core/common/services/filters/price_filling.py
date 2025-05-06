from decimal import Decimal

from exchange_rate.services.conversion import convert_to_usd

from core.common.services.filters.base import BaseTransformFilter
from core.common.mappings.currency import CURRENCY_MAPPING

class UsdConverterFilter(BaseTransformFilter):
    """
    Convert THB-denominated prices into USD, rewriting even non-blank fields:
      - price_cur_per_unit → price_usd_per_piece
      - price_usd_per_piece & carats → price_usd_per_ct
      - total_thb → total_usd
    """
    # place this filter after parsing, before validation
    stage = 35

    def __init__(self):
        # no init arguments
        pass
    
    def _get_currency(self, currency):
        upp_cur = currency.upper()
        for currency, set_curr in CURRENCY_MAPPING.items():
            if upp_cur in set_curr:
                return currency
            
    def _convert_price_per_piece(self, ctx):
        """
        Always convert price_cur_per_unit (in ctx.attrs) to USD
        and store in price_usd_per_piece.
        """
        amount = ctx.attrs.get('price_cur_per_unit')
        currency = ctx.attrs.get('currency')
        date = ctx.attrs.get('date')
        if amount is None or currency is None or date is None:
            return True
        try:
            
            usd = convert_to_usd(amount, date, from_currency=currency)
            ctx.attrs['price_usd_per_piece'] = usd
            return True
        except Exception as e:
            ctx.error = f"Error converting price_cur_per_unit: {e}"
            return False

    def _convert_price_per_ct(self, ctx):
        piece = ctx.attrs.get('price_usd_per_piece')
        carats = ctx.attrs.get('carats')
        if piece is None or carats in (None, 0):
            return True
        try:
            # divide and round to 4 decimals
            per_ct = (piece / Decimal(carats)).quantize(Decimal('0.0001'))
            ctx.attrs['price_usd_per_ct'] = per_ct
            return True
        except Exception as e:
            ctx.error = f"Error computing price_usd_per_ct: {e}"
            return False

    def _convert_total(self, ctx):
        total_thb = ctx.attrs.get('total_thb')
        currency = ctx.attrs.get('currency')
        date = ctx.attrs.get('date')
        if total_thb is None or currency is None or date is None:
            return True
        try:
            total_usd = convert_to_usd(total_thb, date, from_currency=currency)
            ctx.attrs['total_usd'] = total_usd
            return True
        except Exception as e:
            ctx.error = f"Error converting total_thb: {e}"
            return False

    def apply(self, ctx):
        # Convert price_per_piece
        if not self._convert_price_per_piece(ctx):
            return False
        # Compute price per carat
        if not self._convert_price_per_ct(ctx):
            return False
        # Convert total THB → USD
        if not self._convert_total(ctx):
            return False
        return True
