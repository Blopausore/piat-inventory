from django.db import transaction

from core.common.services.filters.mapping import FieldMappingFilter
from core.common.services.filters.type_parsing import TypeParsingFilter
from core.common.services.filters.context import FilterContext
from core.common.services.filters.canceled import CanceledFieldFilter
from core.common.services.filters.required import RequiredFieldFilter

from core.supplier_order.models import SupplierOrder
from core.supplier_order.mapping import SUPPLIER_COLUMN_MAPPING, RAW_SUPPLIER_COLUMN_MAPPING
from core.supplier_order.services.filters.is_purchase import IsPurchaseFilter

class SupplierContext(FilterContext):
    """
    Contexte de transformation pour SupplierOrder, avec les champs attendus dans `attrs`.
    """
    def __init__(self, raw):
        super().__init__(raw, SupplierOrder)
        
class SupplierOrderTransformer:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.filters = [
            IsPurchaseFilter(),
            FieldMappingFilter(field_mapping=SUPPLIER_COLUMN_MAPPING),
            TypeParsingFilter(order_model=SupplierOrder),
            CanceledFieldFilter(),
            RequiredFieldFilter(),
        ]
        ut = SupplierOrder._meta.unique_together
        if ut:
            first = ut[0] if isinstance(ut[0], (list, tuple)) else ut
            self.unique_fields = list(first)
        else:
            self.unique_fields = []

    def transform_one(self, raw):
        ctx = FilterContext(raw, SupplierOrder)
        try:
            for filt in self.filters:
                if not filt.apply(ctx):
                    raise ValueError(f"{ctx.error} from {filt}")
            ctx.instantiate_order()
            ctx.order.full_clean()
        except Exception as e:
            ctx.error = str(e)
        return ctx

    def _manage_new_error(self, ctx, reports, error_key_lenght):
        error_key = ctx.error[:error_key_lenght]
        if error_key not in reports['errors']:
            reports['errors'][error_key] = [1, f"Sheet {ctx.raw.sheet_name} - Index {ctx.raw.row_index} : {ctx.error}"]
        else:
            reports['errors'][error_key][0] += 1

    def run(self, queryset=None, batch_size=1000, error_key_lenght=40):
        """

        Args:
            queryset (_type_, optional): Iterable of SupplierOrderRaw. Defaults to None.
            batch_size (int, optional): Size of the batch for saving bucket. Defaults to 1000.
            error_ket_lenght (int, optional): Key lenght for report message error : big implies mores keys. Defaults to 40.

        Returns:
            reports (dict) : A report of the transfer
        """
        orders_to_create = []
        reports = {
            'total_raws': 0,
            'orders_created': 0,
            'raws_failed': 0,
            'errors': {}
        }
        seen_keys = set()

        for raw in queryset.iterator():
            reports['total_raws'] += 1
            ctx = self.transform_one(raw)

            if ctx.error is None:
                # Construction de la clé de doublon depuis les champs uniques
                key = tuple(getattr(ctx.order, f) for f in self.unique_fields)
                if key in seen_keys:
                    ctx.error = f"Duplicated row : {key}"
                    self._manage_new_error(ctx, reports, error_key_lenght)
                    reports['raws_failed'] += 1
                else:
                    seen_keys.add(key)
                    orders_to_create.append(ctx.order)
                    reports['orders_created'] += 1
            else:
                reports['raws_failed'] += 1
                self._manage_new_error(ctx, reports, error_key_lenght)
            # Bulk insert par batch
            if len(orders_to_create) >= batch_size:
                if not self.dry_run:
                    with transaction.atomic():
                        SupplierOrder.objects.bulk_create(orders_to_create, batch_size)
                orders_to_create.clear()

        # Flush final
        if not self.dry_run and orders_to_create:
            with transaction.atomic():
                SupplierOrder.objects.bulk_create(orders_to_create, batch_size)

        return reports
