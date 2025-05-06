from django.core.management.base import BaseCommand
from core.supplier_order.models import SupplierOrder

class Command(BaseCommand):
    help = "Delete supplier orders database."

    def handle(self, *args, **kwargs):
        size = len(SupplierOrder.objects.all())
        SupplierOrder.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"[DONE] Supplier orders database has been cleared ({size} elements have been deleted)."))
        
