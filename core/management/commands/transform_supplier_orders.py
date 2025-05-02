from django.core.management.base import BaseCommand
from core.models.order_raw import SupplierOrderRaw
from core.services.transform.supplier_order import SupplierOrderTransformer

class Command(BaseCommand):
    help = "Transforme les raws fournisseurs en SupplierOrder."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simulate the command without saving it."
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1000,
            help="Size of the flunch (higher is quicker but use more memory)."
        )


    def handle(self, *args, **kwargs):
        transformer = SupplierOrderTransformer(dry_run=kwargs["dry_run"])
        qs = SupplierOrderRaw.objects.filter(interpreted__isnull=True)
        stats = transformer.run(queryset=qs, batch_size=kwargs["batch_size"])
        self.stdout.write(self.style.SUCCESS(
            f"Transform done :\n"
            f"  total raws : {stats['total_raws']}\n"
            f"  orders created : {stats['orders_created']}\n"
            f"  raws errors : {stats['raws_failed']}"
        ))
