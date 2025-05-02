from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from core.models.supplier_order import SupplierOrder
from core.services.tools.order_pricing import MissingPriceFiller

def supplier_orders_list(request):
    """Work but bad memory management."""
    orders = SupplierOrder.objects.all().order_by('-date')
    return render(request, 'core/supplier_order/table.html', {'orders': orders})


def supplier_orders_import_page(request):
    return render(request, 'core/supplier_order/import.html')

@csrf_exempt
def fill_missing_prices(request):
    """
    Endpoint pour déclencher le remplissage des prix USD manquants.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    # On récupère le paramètre dry_run si besoin (ou toujours False)
    dry_run = request.POST.get("dry_run") == "true"
    verbose = request.POST.get("verbose") == "true"

    service = MissingPriceFiller(dry_run=dry_run, verbose=verbose)
    report = service.run()

    return JsonResponse(report)