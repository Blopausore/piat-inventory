from core.supplier_order.models import SupplierOrder
from core.supplier_order.mapping import SUPPLIER_ORDER_FIELDS
from core.common.views.export import orders_export

def supplier_orders_export(request):
    return orders_export(
        request=request, 
        order_model=SupplierOrder,
        order_fields=SUPPLIER_ORDER_FIELDS,
        order_name="supplier"
    )
