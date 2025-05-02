from django.contrib import admin
from core.models.order_raw import SupplierOrderRaw
from core.models.supplier_order import SupplierOrder
from core.models.client_order import ClientOrder


admin.site.register(SupplierOrderRaw)

# @admin.register(SupplierOrder)
# class SupplierOrderAdmin(admin.ModelAdmin):
#     list_display = (
#         'date', 'supplier', 'order_no', 'stone', 'shape', 'color',
#         'carats', 'price_cur_per_unit', 'currency', 'total_thb'
#     )
#     search_fields = ('supplier', 'order_no', 'stone', 'color', 'shape', 'remarks')
#     list_filter = ('currency', 'supplier', 'shape', 'color', 'unit')
#     ordering = ('-date',)
#     date_hierarchy = 'date'