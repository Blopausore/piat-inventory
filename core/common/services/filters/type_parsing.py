# core/services/filters/type_parsing.py
from decimal import Decimal, ROUND_HALF_UP
import re

from django.db import models
from core.common.services.filters.base import BaseTransformFilter
from core.common.tools.parse import (
    parse_int, parse_decimal, parse_date,
)

def to_decimal(cleaned: str, field: models.DecimalField) -> Decimal:
    """Nettoie, convertit et quantize selon field.decimal_places."""
    # on enlève tout sauf chiffres, point et signe
    s = re.sub(r"[^\d\.\-]", "", cleaned)
    dec = Decimal(s or "0")
    quantum = Decimal("1").scaleb(-field.decimal_places)
    
    return dec.quantize(quantum, rounding=ROUND_HALF_UP)

class TypeParsingFilter(BaseTransformFilter):
    """Sparse the value of the 'context'."""
    def __init__(self, order_model):
        self._opts = order_model._meta

    def apply(self, ctx):
        for field_name, raw_val in list(ctx.attrs.items()):
            if raw_val is None:
                continue

            model_field = self._opts.get_field(field_name)

            if isinstance(model_field, models.IntegerField):
                ctx.attrs[field_name] = parse_int(raw_val)

            # DecimalField
            elif isinstance(model_field, models.DecimalField):
                if isinstance(raw_val, str):
                    ctx.attrs[field_name] = to_decimal(raw_val, model_field)
                else:
                    ctx.attrs[field_name] = parse_decimal(raw_val)

            elif isinstance(model_field, (models.DateTimeField, models.DateField)):
                ctx.attrs[field_name] = parse_date(raw_val)

            # FloatField
            elif isinstance(model_field, models.FloatField):
                try:
                    ctx.attrs[field_name] = float(raw_val)
                except (TypeError, ValueError):
                    ctx.attrs[field_name] = None
            else:
                ctx.attrs[field_name] = raw_val
        return True