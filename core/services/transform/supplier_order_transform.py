# core/services/transforms/supplier_order_transform.py

from core.models.supplier_order import SupplierOrder
from core.models.supplier_order_raw import SupplierOrderRaw
from core.services.transform.context import TransformContext
from core.services.filters.mapping import MappingFilter
from core.services.filters.type_parsing import TypeParsingFilter

class SupplierOrderTransformer:
    def __init__(self, dry_run=False):
        self.filters = [ 
                        ] 
        self.model_class = SupplierOrder

    def transform_one(self, raw: SupplierOrderRaw):
        ctx = TransformContext(raw, self.model_class)
        for filt in self.filters:
            filt.apply(ctx)
            if ctx.error:
                break
        # …
