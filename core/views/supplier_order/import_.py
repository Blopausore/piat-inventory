from django.contrib import messages
from django.shortcuts import redirect

from core.services.imports.supplier_order import import_supplier_orders
from core.views.wrapper_order import orders_import_upload

def supplier_orders_import_upload(request):
    return orders_import_upload(
        request=request,
        import_order_func=import_supplier_orders,
        order_name="supplier"
    )
