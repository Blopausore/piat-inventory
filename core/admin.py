from django.contrib import admin
from core.order_raw.models import OrderRaw, SupplierOrderRaw
from core.supplier_order.models import SupplierOrder
from core.client_order.models import ClientOrder


# admin.site.register(SupplierOrderRaw)


class InterpretedFilter(admin.SimpleListFilter):
    title = 'Interpreted'
    parameter_name = 'interpreted'

    def lookups(self, request, model_admin):
        return (
            ('1', 'Yes'),
            ('0', 'No'),
        )

    def queryset(self, request, queryset):
        val = self.value()
        if val == '1':
            return queryset.filter(interpreted__isnull=False)
        if val == '0':
            return queryset.filter(interpreted__isnull=True)
        return queryset

@admin.register(SupplierOrderRaw)
class SupplierOrderRawAdmin(admin.ModelAdmin):
    list_display = (
        'source_file',
        'sheet_name',
        'row_index',
        'is_interpreted',
    )
    list_filter = (
        'source_file',
        'sheet_name',
        InterpretedFilter,
    )
    search_fields = ('source_file', 'sheet_name', 'row_index')
    ordering = ('source_file', 'sheet_name', 'row_index')

    def is_interpreted(self, obj):
        return hasattr(obj, 'interpreted') and obj.interpreted is not None
    is_interpreted.boolean = True
    is_interpreted.short_description = 'Interpreted'

@admin.register(SupplierOrder)
class SupplierOrderAdmin(admin.ModelAdmin):
    list_display = (
        'date', 'book_no', 'supplier', 'order_no', 'stone', 'shape', 'color',
        'carats', 'weight_per_piece', 'price_usd_per_piece', 'price_usd_per_ct', 'total_usd'
    )
    search_fields = ('date', 'supplier', 'order_no', 'stone', 'color', 'shape')
    list_filter = ('supplier', 'stone', 'shape', 'color')
    ordering = ('-date',)
    date_hierarchy = 'date'