from django.contrib import admin
from core.order_raw.models import SupplierOrderRaw
from core.supplier_order.models import SupplierOrder
from core.client_order.models import ClientOrder


admin.site.register(SupplierOrderRaw)

admin.site.register(SupplierOrder)
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