# core/services/transforms/filters/mapping.py
from core.mappings.supplier_order import SUPPLIER_COLUMN_MAPPING
from .base import BaseTransformFilter

class MappingFilter(BaseTransformFilter):
    """Map the field names to normalize them."""

    def apply(self, ctx):
        for field in ctx.fields:
            ctx.attrs[field] = ctx.raw.get_mapped_value(field)
