
from core.supplier_order.services.old_imports import import_supplier_orders
from core.common.views.import_ import orders_import_upload

def supplier_orders_import_upload(request):
    return orders_import_upload(
        request=request,
        import_order_func=import_supplier_orders,
        order_name="supplier"
    )
