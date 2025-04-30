
from django.http import JsonResponse 
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def order_update(request, order_model, order_fields):
    if request.method == "POST":
        order_id = request.POST.get('order_id')
        if not order_id:
            return JsonResponse({"error": "Missing order ID"}, status=400)

        field_index = int(request.POST.get('field_index'))
        new_value = request.POST.get('new_value')

        # Mapping of column indexes to model fields
        field_map = {index: field for index, (field, title) in enumerate(order_fields)}

        field_name = field_map.get(field_index)
        if not field_name:
            return JsonResponse({"error": "Invalid field index"}, status=400)

        try:
            order = order_model.objects.get(id=order_id)
            setattr(order, field_name, new_value)
            order.save()
            return JsonResponse({"success": True})
        except order_model.DoesNotExist:
            return JsonResponse({"error": "Order not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


