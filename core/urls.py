from django.urls import path
from .views import supplier_orders_list, supplier_orders_json
urlpatterns = [
    path('supplier-orders/', supplier_orders_list, name='supplier_orders_list'),
    path('supplier-orders/data/', supplier_orders_json, name='supplier_orders_json'),
]
