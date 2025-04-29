from django.urls import path
from core.views import views

urlpatterns = [
    path('supplier-orders/', views.supplier_orders_list, name='supplier_orders_list'),
    path('supplier-orders/data/', views.supplier_orders_json, name='supplier_orders_json'),
    path('supplier-orders/update/', views.supplier_order_update, name='supplier_order_update'),
    path('supplier-orders/export/', views.supplier_orders_export, name='supplier_orders_export'),
    path('supplier-orders/import/', views.supplier_orders_import_page, name='supplier_orders_import_page'),
    path('supplier-orders/import/upload/', views.supplier_orders_import_upload, name='supplier_orders_import_upload'),

]
