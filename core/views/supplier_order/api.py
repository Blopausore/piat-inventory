
from django.views.decorators.csrf import csrf_exempt

from core.models import SupplierOrder
from core.mappings.supplier_order import SUPPLIER_ORDER_FIELDS

from core.views.wrapper_order.api import orders_json, order_update


def supplier_orders_json(request):
    return orders_json(
        request,
        model=SupplierOrder,
        display_fields=SUPPLIER_ORDER_FIELDS,
        search_fields=["order_no", "supplier", "stone", "color", "shape", "size"],
        default_order_field="date"
    )

@csrf_exempt
def supplier_order_update(request):
    return order_update(
        request=request,
        order_model=SupplierOrder,
        order_fields=SUPPLIER_ORDER_FIELDS
    )

