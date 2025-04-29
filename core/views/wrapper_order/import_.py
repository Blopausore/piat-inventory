from django.contrib import messages
from django.shortcuts import redirect

def orders_import_upload(request, import_order_func, order_name):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        try:
            report = import_order_func(file)
            messages.success(request, f"Import completed: {report['imported']} orders added.")
            return redirect(f'{order_name}_orders_list')  
        except Exception as e:
            messages.error(request, f"Import failed: {str(e)}")
            return redirect(f'{order_name}_orders_import_page')
    else:
        messages.error(request, "No file selected.")
        return redirect(f'{order_name}_orders_import_page')
    
