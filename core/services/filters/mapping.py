# core/services/filters/mapping.py
from .base import BaseTransformFilter

class MappingFilter(BaseTransformFilter):
    def __init__(self, field_mapping):
        self.field_mapping = field_mapping

    def apply(self, ctx):
        for field, columns in self.field_mapping.items():
            for col in columns:
                val = ctx.raw.get(col)
                if val not in (None, ""):
                    ctx.attrs[field] = val
                    break
        return True
