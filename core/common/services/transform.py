from django.db.models import F
from django.db import transaction

from core.common.services.filters.mapping import FieldMappingFilter
from core.common.services.filters.type_parsing import TypeParsingFilter
from core.common.services.filters.context import TransformContext
from core.common.services.filters.canceled import CanceledFieldFilter
from core.common.services.filters.required import RequiredFieldFilter

from core.supplier_order.mapping import SUPPLIER_COLUMN_MAPPING, RAW_SUPPLIER_COLUMN_MAPPING


class OrderTransformer:
    def __init__(self, order_model, dry_run=False):
        self.dry_run = dry_run
        # mapping → parsing → validité
        self.filters = [
            FieldMappingFilter(field_mapping=RAW_SUPPLIER_COLUMN_MAPPING),
            FieldMappingFilter(field_mapping=SUPPLIER_COLUMN_MAPPING),
            TypeParsingFilter(order_model=order_model),
            CanceledFieldFilter(),
            RequiredFieldFilter(),
        ]

    def transform_one(self, raw):
        
        ctx = TransformContext(raw, self.order_model)
        
        try:
            for filt in self.filters:
                
                if not filt.apply(ctx):
                    raise ValueError(f"{ctx.error} from {filt}")
            
            ctx.instantiate_order()
            ctx.order.full_clean()
            
        except Exception as e:
            ctx.error = str(e)
            return ctx
            
        return ctx


    def run(self, queryset=None, batch_size=1000):
        orders_to_create = []
        stats = {'total_raws': 0, 'orders_created': 0, 'raws_failed': 0, 'errors': {}}
        key = {} # hash key to check doublon
        for raw in queryset.iterator():
            stats['total_raws'] += 1
            ctx = self.transform_one(raw)

            if ctx.error is None:
                orders_to_create.append(ctx.order)
                stats['orders_created'] += 1
            else:
                stats['raws_failed'] += 1
                error_key = ctx.error[:40]
                if not error_key in stats['errors'].keys():
                    print(ctx.error)
                    stats['errors'][error_key] = [f"{ctx.raw.sheet_name} - {ctx.raw.row_index} : {ctx.error}", 1]
                else:
                    stats['errors'][error_key][1] +=1

            if len(orders_to_create) >= batch_size:
                if not self.dry_run:
                    with transaction.atomic():
                        self.order_model.objects.bulk_create(
                            orders_to_create, batch_size
                        )
                orders_to_create.clear()

        if not self.dry_run and orders_to_create:
            with transaction.atomic():
                self.order_model.objects.bulk_create(
                        orders_to_create, batch_size
                    )
        return stats