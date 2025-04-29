from datetime import datetime
import pandas as pd

from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse, JsonResponse 
from django.utils.timezone import is_aware
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from core.models import SupplierOrder
from core.mappings.supplier_order import SUPPLIER_ORDER_FIELDS
from core.services.imports.supplier_order import import_supplier_orders

def supplier_orders_list(request):
    """Work but bad memory management."""
    orders = SupplierOrder.objects.all().order_by('-date')
    return render(request, 'core/supplier_orders_table.html', {'orders': orders})


def supplier_orders_json(request):
    """"""
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))

    # Order
    order_column_index = request.GET.get('order[0][column]')
    order_direction = request.GET.get('order[0][dir]')
    field_map = {index: field for index, (field, title) in enumerate(SUPPLIER_ORDER_FIELDS)}

    if order_column_index is not None:
        order_column = field_map.get(int(order_column_index), 'date')
    else:
        order_column = 'date'  
    # default ordering
    if order_direction == 'desc':
        order_column = '-' + order_column
    
    # Search
    search_value = request.GET.get('search[value]', '')

    queryset = SupplierOrder.objects.all()

    if search_value:
        queryset = queryset.filter(
            Q(order_no__icontains=search_value) |
            Q(supplier__icontains=search_value) |
            Q(stone__icontains=search_value) |
            Q(color__icontains=search_value) |
            Q(shape__icontains=search_value) |
            Q(size__icontains=search_value)
        )

    queryset = queryset.order_by(order_column)

    paginator = Paginator(queryset, length)
    page_number = start // length + 1
    page = paginator.page(page_number)

    data = []
    for order in page.object_list:
        row = []
        for (field, _) in SUPPLIER_ORDER_FIELDS:
            value = getattr(order, field)
            if field == "date":
                value = value.strftime('%Y-%m-%d') if order.date else ''
            
            row.append(str(value) if value is not None else '')
        data.append(row)

    return JsonResponse({
        'draw': draw,
        'recordsTotal': SupplierOrder.objects.count(),
        'recordsFiltered': queryset.count(),
        'data': data
    })

@csrf_exempt
def supplier_order_update(request):
    if request.method == "POST":
        order_no = request.POST.get('order_id')
        field_index = int(request.POST.get('field_index'))
        new_value = request.POST.get('new_value')

        # Mapping of column indexes to model fields
        field_map = {index: field for index, (field, title) in enumerate(SUPPLIER_ORDER_FIELDS)}

        field_name = field_map.get(field_index)
        if not field_name:
            return JsonResponse({"error": "Invalid field index"}, status=400)

        try:
            order = SupplierOrder.objects.get(order_no=order_no)
            setattr(order, field_name, new_value)
            order.save()
            return JsonResponse({"success": True})
        except SupplierOrder.DoesNotExist:
            return JsonResponse({"error": "Order not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)



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

def supplier_orders_import_page(request):
    return render(request, 'core/supplier_orders_import.html')


def supplier_orders_import_upload(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        try:
            report = import_supplier_orders(file)
            messages.success(request, f"Import completed: {report['imported']} orders added.")
            return redirect('supplier_orders_list')  
        except Exception as e:
            messages.error(request, f"Import failed: {str(e)}")
            return redirect('supplier_orders_import_page')
    else:
        messages.error(request, "No file selected.")
        return redirect('supplier_orders_import_page')