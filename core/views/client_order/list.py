from django.shortcuts import render
from core.models import SupplierOrder

def supplier_orders_list(request):
    """Work but bad memory management."""
    orders = SupplierOrder.objects.all().order_by('-date')
    return render(request, 'core/supplier_orders_table.html', {'orders': orders})


def supplier_orders_import_page(request):
    return render(request, 'core/supplier_orders_import.html')
