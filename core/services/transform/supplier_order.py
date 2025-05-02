# core/services/transforms/supplier_order_transform.py
from core.services.filters.mapping import MappingFilter
from core.services.filters.type_parsing import TypeParsingFilter
    

class TransformContext:
    def __init__(self, raw, fields):
        self.raw = raw
        self.fields = [f for f,_ in SUPPLIER_ORDER_FIELDS]
        self.attrs = {}
        self.order = None
        self.error = None

    def instantiate_order(self):
        self.order = SupplierOrder(raw=self.raw, **self.attrs)


class SupplierOrderTransformer:
    def __init__(self, dry_run=False):
        # injecter les filtres dans l'ordre voulu
        self.filters = [
            MappingFilter(),
            TypeParsingFilter(),
            # ... d'autres filtres (ValidationFilter, etc.)
            PriceFillerFilter(dry_run=dry_run),
            # SaveFilter(), etc.
        ]

    def transform_one(self, raw):
        ctx = TransformContext(raw)
        try:
            # étape : instanciation de l'objet (sans save)
            ctx.instantiate_order()
            for filt in self.filters:
                filt.apply(ctx)
                if ctx.error:
                    raise ctx.error
            # si tout s'est bien passé, on sauvegarde
            ctx.order.full_clean()
            ctx.order.save()
            raw.success, raw.error = True, ""
        except Exception as e:
            raw.success, raw.error = False, str(e)
        raw.save(update_fields=["success", "error"])
        return ctx

    def run(self, queryset=None):
        # idem qu'avant…
        pass


