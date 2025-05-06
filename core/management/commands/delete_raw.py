from django.core.management.base import BaseCommand
from core.order_raw.models import OrderRaw, SupplierOrderRaw, ClientOrderRaw

class Command(BaseCommand):
    help = "Delete supplier orders database."
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            help="Type of order [supplier, client, other].",
            default="other"
        )
    def handle(self, *args, **kwargs):
        if kwargs['type'] == 'supplier':
            order_model = SupplierOrderRaw
        elif kwargs['type'] == 'client':
            order_model = ClientOrderRaw
        else:
            order_model = OrderRaw
            kwargs['type'] = ""
        size = len(order_model.objects.all())
        order_model.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"[DONE] Raw orders {kwargs['type']} has been cleared ({size} elements have been deleted)."))
        
