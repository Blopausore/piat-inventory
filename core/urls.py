from django.urls import path
from core.views.supplier_order import *

urlpatterns = [
    path('supplier-orders/', supplier_orders_list, name='supplier_orders_list'),
    path('supplier-orders/data/', supplier_orders_json, name='supplier_orders_json'),
    path('supplier-orders/update/', supplier_order_update, name='supplier_order_update'),
    path('supplier-orders/export/', supplier_orders_export, name='supplier_orders_export'),
    path('supplier-orders/import/', supplier_orders_import_page, name='supplier_orders_import_page'),
    path('supplier-orders/import/upload/', supplier_orders_import_upload, name='supplier_orders_import_upload'),
    
    
    
]
