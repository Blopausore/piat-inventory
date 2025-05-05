# core/views/wrapper_order/api.py

from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from datetime import datetime

def orders_json(
    request,
    model,
    display_fields,
    search_fields=None,
    related_search_fields=None,
    filter_conditions=None,
    date_range_filters=None,
    multi_value_filters=None,
    default_order_field="date"
):
    """
    Generic, production-ready JSON response for DataTables.
    Supports:
    - Pagination
    - Sorting by column
    - Search across fields (including ForeignKey)
    - Custom filtering (exact)
    - Multi-value filtering (e.g., shape=oval&shape=round)
    - Date range filtering (e.g., ?start_date=2023-01-01&end_date=2023-03-01)
    """

    draw = int(request.GET.get("draw", 1))
    start = int(request.GET.get("start", 0))
    length = int(request.GET.get("length", 10))

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

    # Exact match filters
    if filter_conditions:
        for key, value in filter_conditions.items():
            if value:
                queryset = queryset.filter(**{key: value})

    # Multi-value filters (?shape=oval&shape=round)
    if multi_value_filters:
        for field in multi_value_filters:
            values = request.GET.getlist(field)
            if values:
                queryset = queryset.filter(**{f"{field}__in": values})

    # Date range filters
    if date_range_filters:
        for field in date_range_filters:
            start_date_str = request.GET.get("start_date")
            end_date_str = request.GET.get("end_date")
            try:
                if start_date_str:
                    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                    queryset = queryset.filter(**{f"{field}__gte": start_date})
                if end_date_str:
                    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                    queryset = queryset.filter(**{f"{field}__lte": end_date})
            except ValueError:
                pass  # silently ignore bad date

    queryset = queryset.order_by(order_column)
    paginator = Paginator(queryset, length)
    page_number = start // length + 1
    page = paginator.page(page_number)

    data = []
    for obj in page.object_list:
        row = []
        for field, _ in display_fields:
            value = getattr(obj, field, '')
            if hasattr(value, "strftime"):
                value = value.strftime("%Y-%m-%d")
            row.append(str(value) if value is not None else '')
        row.append(obj.id)
        data.append(row)
        
    return JsonResponse({
        "draw": draw,
        "recordsTotal": model.objects.count(),
        "recordsFiltered": queryset.count(),
        "data": data,
    })
