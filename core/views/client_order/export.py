from datetime import datetime
import pandas as pd

from django.http import HttpResponse 
from django.utils.timezone import is_aware

from core.models import SupplierOrder
from core.mappings.supplier_order import SUPPLIER_ORDER_FIELDS


def supplier_orders_export(request):
    orders = SupplierOrder.objects.all()

    data = []
    for order in orders:
        row = {}
        for field, column_title in SUPPLIER_ORDER_FIELDS:
            value = getattr(order, field, None)

            if field == "date" and value and is_aware(value):
                value = value.astimezone(None).replace(tzinfo=None)
            if isinstance(value, datetime):
                value = value.date()
            row[column_title] = value

        data.append(row)    

    df = pd.DataFrame(data)
    for col in df.select_dtypes(include=['datetimetz']).columns:
        df[col] = df[col].dt.tz_localize(None)
    now = datetime.now().strftime("%Y%m%d_%H%M%S")  # e.g., 20250429_153045
    filename = f"supplier_orders_export_{now}.xlsx"

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)

    return response
