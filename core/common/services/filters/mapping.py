from core.common.services.filters.base import BaseTransformFilter

from core.common.tools.row import get_value_mapped

class FieldMappingFilter(BaseTransformFilter):
    stage = BaseTransformFilter.FilterLevel.FIRST_STAGE

    def __init__(self, field_mapping):
        self.field_mapping = field_mapping

    def apply(self, ctx):
        for field in ctx.attrs.keys():
            ctx.attrs[field] = get_value_mapped(ctx.raw.data, field, self.field_mapping) 
                    
        return True


class ValueMappingFilter(BaseTransformFilter):
    # TODO : mapping of 
    
    
    def map_order_number(self, value):
        if value is None:
            ...
        
    
    
    def apply(self, ctx):
        return super().apply(ctx)
    