from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q

from core.models import SupplierOrder

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
    order_column_map = {
        0: 'date',
        1: 'book_no',
        2: 'order_no',
        3: 'tax_invoice',
        4: 'supplier',
        5: 'number',
        6: 'stone',
        7: 'heating',
        8: 'color',
        9: 'shape',
        10: 'cutting',
        11: 'size',
        12: 'carats',
        13: 'currency',
        14: 'price_cur_per_unit',
        15: 'unit',
        16: 'total_thb',
        17: 'weight_per_piece',
        18: 'price_usd_per_ct',
        19: 'price_usd_per_piece',
        20: 'total_usd',
        21: 'rate_avg_2019',
        22: 'remarks',
        23: 'credit_term',
        24: 'target_size',
    }
    
    if order_column_index is not None:
        order_column = order_column_map.get(int(order_column_index), 'date')
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
        data.append([
            order.date.strftime('%Y-%m-%d') if order.date else '',
            order.book_no,
            order.order_no,
            order.tax_invoice,
            order.supplier,
            order.number,
            order.stone,
            order.heating,
            order.color,
            order.shape,
            order.cutting,
            order.size,
            str(order.carats),
            order.currency,
            str(order.price_cur_per_unit),
            order.unit,
            str(order.total_thb),
            str(order.weight_per_piece),
            str(order.price_usd_per_ct),
            str(order.price_usd_per_piece),
            str(order.total_usd),
            str(order.rate_avg_2019),
            order.remarks,
            order.credit_term,
            order.target_size,
        ])

    return JsonResponse({
        'draw': draw,
        'recordsTotal': SupplierOrder.objects.count(),
        'recordsFiltered': queryset.count(),
        'data': data
    })
