# core/services/transforms/supplier_order_transform.py
from django.db.models import F
from django.db import transaction

from core.services.filters.mapping import MappingFilter
from core.services.filters.type_parsing import TypeParsingFilter
from core.services.filters.context import TransformContext
from core.services.filters.validity import SupplierValidityFilter

from core.models.order_raw import SupplierOrderRaw
from core.models.supplier_order import SupplierOrder
from core.mappings.supplier_order import SUPPLIER_COLUMN_MAPPING

class SupplierContext(TransformContext):
    """
    Fields in attrs
    'client_memo':          
    'date':                 
    'book_no':              
    'order_no':             
    'tax_invoice':          
    'supplier':             
    'number':               
    'stone':                
    'heating':              
    'color':                
    'shape':                
    'size':                 
    'carats':               
    'currency':             
    'price_cur_per_unit':   
    'unit':                 
    'total_thb':            
    'weight_per_piece':     
    'price_usd_per_ct':     
    'price_usd_per_piece':  
    'total_usd':            
    'rate_avg_2019':        
    'remarks':              
    'credit_term':          
    'target_size':          
    """
    def __init__(self, raw):
        super().__init__(raw, SupplierOrder)
        

class SupplierOrderTransformer:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        # mapping → parsing → validité
        self.filters = [
            MappingFilter(field_mapping=SUPPLIER_COLUMN_MAPPING),
            TypeParsingFilter(),
            SupplierValidityFilter(),
        ]

    def transform_one(self, raw):
        
        ctx = TransformContext(raw, SupplierOrder)
        
        # # Fill attrs
        # for field in ctx.fields:
        #     for potential_column_name in self.field_mapping[field]:
        #         if ctx.raw.get(potential_column_name):
        #             self.attrs[field] = ctx.raw.get(potential_column_name)
            
        try:
            for filt in self.filters:
                if not filt.apply(ctx):
                    raise ValueError(ctx.error)

            ctx.instantiate_order()
            ctx.order.full_clean()
            
            return ctx

        except Exception as e:
            return ctx

    def run(self, queryset=None, batch_size=1000):
        orders_to_create = []
        stats = {'total_raws': 0, 'orders_created': 0, 'raws_failed': 0}

        for raw in queryset.iterator():
            stats['total_raws'] += 1
            ctx = self.transform_one(raw)

            if ctx.error is None:
                orders_to_create.append(ctx.order)
                stats['orders_created'] += 1
            else:
                stats['raws_failed'] += 1

            if len(orders_to_create) >= batch_size:
                if not self.dry_run:
                    with transaction.atomic():
                        SupplierOrder.objects.bulk_create(
                            orders_to_create, batch_size
                        )
                orders_to_create.clear()

        if not self.dry_run and orders_to_create:
            with transaction.atomic():
                SupplierOrder.objects.bulk_create(
                        orders_to_create, batch_size
                    )

        return stats