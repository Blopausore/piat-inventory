from datetime import datetime
import pandas as pd

from django.http import HttpResponse 
from django.utils.timezone import is_aware

from core.models.supplier_order import SupplierOrder
from core.mappings.supplier_order import SUPPLIER_ORDER_FIELDS
from core.views.wrapper_order.export import orders_export

def supplier_orders_export(request):
    return orders_export(
        request=request, 
        order_model=SupplierOrder,
        order_fields=SUPPLIER_ORDER_FIELDS,
        order_name="supplier"
    )
