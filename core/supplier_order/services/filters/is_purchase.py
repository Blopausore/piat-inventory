import pandas as pd

from django.db.models import Field

from core.common.tools.row import get_value_mapped
from core.common.services.filters.base import BaseTransformFilter
from core.supplier_order.mapping import RAW_SUPPLIER_COLUMN_MAPPING
    
    
class IsPurchaseFilter(BaseTransformFilter):
    """Filter the 'Order' that are actual purchased."""
    def apply(self, ctx):
        memo = get_value_mapped(ctx.raw.data, "client_memo", RAW_SUPPLIER_COLUMN_MAPPING) or ""
        memo = memo.strip().upper()
        if memo in {"", "P"}:
            return True
        ctx.error = f"Not a purchase : client memo [{memo}]"
        return False
        
        