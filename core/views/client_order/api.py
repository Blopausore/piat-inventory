from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse 
from django.views.decorators.csrf import csrf_exempt

from core.models import SupplierOrder
from core.mappings.supplier_order import SUPPLIER_ORDER_FIELDS


def orders_json(request, model, display_fields, search_fields=None, default_order_field='date'):
    """Generic DataTables JSON API."""
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))

    # Build ordering
    order_column_index = request.GET.get('order[0][column]')
    order_direction = request.GET.get('order[0][dir]')
    field_map = {index: field for index, (field, _) in enumerate(display_fields)}

    order_column = field_map.get(int(order_column_index), default_order_field) if order_column_index else default_order_field
    if order_direction == 'desc':
        order_column = '-' + order_column

    queryset = model.objects.all()

    # Search
    search_value = request.GET.get('search[value]', '')
    if search_value and search_fields:
        q_objects = Q()
        for field in search_fields:
            q_objects |= Q(**{f"{field}__icontains": search_value})
        queryset = queryset.filter(q_objects)

    queryset = queryset.order_by(order_column)

    paginator = Paginator(queryset, length)
    page_number = start // length + 1
    page = paginator.page(page_number)

    data = []
    for obj in page.object_list:
        row = []
        for field, _ in display_fields:
            value = getattr(obj, field, '')
            if field == "date" and value:
                value = value.strftime('%Y-%m-%d')
            row.append(str(value) if value is not None else '')
        data.append(row)

    return JsonResponse({
        'draw': draw,
        'recordsTotal': model.objects.count(),
        'recordsFiltered': queryset.count(),
        'data': data
    })
    

def supplier_orders_json(request):
    return order_json(
        request,
        model=SupplierOrder,
        display_fields=SUPPLIER_ORDER_FIELDS,
        search_fields=["order_no", "supplier", "stone", "color", "shape", "size"],
        default_order_field="date"
    )

@csrf_exempt
def order_update(request, order_model, order_fields):
    if request.method == "POST":
        order_no = request.POST.get('order_id')
        field_index = int(request.POST.get('field_index'))
        new_value = request.POST.get('new_value')

        # Mapping of column indexes to model fields
        field_map = {index: field for index, (field, title) in enumerate(order_fields)}

        field_name = field_map.get(field_index)
        if not field_name:
            return JsonResponse({"error": "Invalid field index"}, status=400)

        try:
            order = order_model.objects.get(order_no=order_no)
            setattr(order, field_name, new_value)
            order.save()
            return JsonResponse({"success": True})
        except order_model.DoesNotExist:
            return JsonResponse({"error": "Order not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def supplier_order_update(request):
    return order_update(
        request=request,
        order_model=SupplierOrder,
        order_fields=SUPPLIER_ORDER_FIELDS
    )
