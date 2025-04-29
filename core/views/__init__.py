# core/views/__init__.py

# Supplier Order Views
from .supplier_order.views import supplier_orders_list, supplier_orders_import_page
from .supplier_order.api import supplier_orders_json, supplier_order_update
from .supplier_order.export import supplier_orders_export
from .supplier_order.import_ import supplier_orders_import_upload

# Si besoin : Wrapper generic order views
from .wrapper_order.api import order_json
from .wrapper_order.export import export_orders_generic
from .wrapper_order.import_ import import_orders_generic
