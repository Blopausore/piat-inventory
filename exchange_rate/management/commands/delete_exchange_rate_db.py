# core/management/commands/import_supplier_orders.py

from django.core.management.base import BaseCommand
from exchange_rate.models import ExchangeRate

class Command(BaseCommand):
    help = "Delete supplier orders database."

    def handle(self, *args, **kwargs):
        size = len(ExchangeRate.objects.all())
        ExchangeRate.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"[DONE] Supplier orders database has been cleared ({size} elements have been deleted)."))
        
