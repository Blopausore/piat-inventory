from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse 
from django.views.decorators.csrf import csrf_exempt



# core/views/wrapper_order/api.py

from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime

def orders_json(
    request,
    model,
    display_fields,
    search_fields=None,
    related_search_fields=None,
    filter_conditions=None,
    default_order_field="date"
):
    """
    Generic, production-ready JSON response for DataTables.
    Supports:
    - Pagination
    - Sorting by column
    - Search across fields (including ForeignKey)
    - Custom filtering
    """

    draw = int(request.GET.get("draw", 1))
    start = int(request.GET.get("start", 0))
    length = int(request.GET.get("length", 10))

    # Column ordering
    order_column_index = request.GET.get("order[0][column]")
    order_direction = request.GET.get("order[0][dir]")
    field_map = {index: field for index, (field, _) in enumerate(display_fields)}

    order_column = field_map.get(int(order_column_index), default_order_field) if order_column_index else default_order_field
    if order_direction == "desc":
        order_column = f"-{order_column}"

    queryset = model.objects.all()

    # Global search
    search_value = request.GET.get("search[value]", "")
    if search_value:
        q_objects = Q()

        if search_fields:
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": search_value})

        if related_search_fields:
            for related_field in related_search_fields:
                q_objects |= Q(**{f"{related_field}__icontains": search_value})

        queryset = queryset.filter(q_objects)

    # Custom filters (e.g., ?status=paid)
    if filter_conditions:
        for key, value in filter_conditions.items():
            if value:
                queryset = queryset.filter(**{key: value})

    queryset = queryset.order_by(order_column)
    paginator = Paginator(queryset, length)
    page_number = start // length + 1
    page = paginator.page(page_number)

    # Output
    data = []
    for obj in page.object_list:
        row = []
        for field, _ in display_fields:
            value = getattr(obj, field, '')
            if hasattr(value, "strftime"):
                value = value.strftime("%Y-%m-%d")
            row.append(str(value) if value is not None else '')
        data.append(row)

    return JsonResponse({
        "draw": draw,
        "recordsTotal": model.objects.count(),
        "recordsFiltered": queryset.count(),
        "data": data,
    })


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


