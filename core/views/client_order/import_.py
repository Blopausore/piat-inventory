from django.contrib import messages
from django.shortcuts import redirect

from core.services.imports.supplier_order import import_supplier_orders


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
    
