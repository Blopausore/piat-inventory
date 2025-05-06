
from core.common.services.filters.base import BaseTransformFilter
from core.common.tools.parse import (
    parse_currency
)


class FieldParsingFilter(BaseTransformFilter):
    """Sparse the value of the 'context'."""
    stage = BaseTransformFilter.FilterLevel.FOURTH_STAGE
    
    def __init__(self, order_model):
        self._opts = order_model._meta

    def apply(self, ctx):
        for field_name, raw_val in list(ctx.attrs.items()):
            if raw_val is None:
                continue

            if field_name == 'currency':
                ctx.attrs[field_name] = parse_currency(raw_val)
                
