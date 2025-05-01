from django.contrib import admin
from core.models import SupplierOrder, ClientOrder

@admin.register(SupplierOrder)
class SupplierOrderAdmin(admin.ModelAdmin):
    list_display = (
        'date', 'supplier', 'order_no', 'stone', 'shape', 'color',
        'carats', 'price_cur_per_unit', 'currency', 'total_thb'
    )
    search_fields = ('supplier', 'stone', 'color', 'shape', 'remarks')
    list_filter = ('currency', 'supplier', 'shape', 'color')
    ordering = ('-date',)
    date_hierarchy = 'date'