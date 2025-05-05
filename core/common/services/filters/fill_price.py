# core/services/transforms/filters/type_parsing.py

from django.db import models
from core.common.tools.parse import (
    parse_int, parse_decimal, parse_date,
)
from .base import BaseTransformFilter

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
