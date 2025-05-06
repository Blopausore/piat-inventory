from django.core.management.base import BaseCommand
from core.order_raw.models import SupplierOrderRaw
from core.supplier_order.services.transform import SupplierOrderTransformer

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
        if stats["orders_created"] == 0:
            self.stdout.write(self.style.ERROR(
                f"Transform error (0 orders created) :\n"
                f"  total raws : {stats['total_raws']}\n"
                f"  orders created : {stats['orders_created']}\n"
                f"  raws errors : {stats['raws_failed']}"
            ))
            errors = list(sorted(stats['errors'].values(), key= lambda e: e[0], reverse=True))
            self.stdout.write(self.style.ERROR("First 10 samples of errors\n"))
            for _, error in zip(range(10), errors):
                self.stdout.write(self.style.ERROR(f"Occured {error[0]} times | {error[1]}\n"))

        else:
            self.stdout.write(self.style.SUCCESS(
                f"Transform done :\n"
                f"  total raws : {stats['total_raws']}\n"
                f"  orders created : {stats['orders_created']}\n"
                f"  raws errors : {stats['raws_failed']}"
            ))
            errors = list(sorted(stats['errors'].values(), key= lambda e: e[0], reverse=True))
            self.stdout.write(self.style.WARNING("First 10 samples of errors\n"))
            for _, error in zip(range(10), errors):
                self.stdout.write(self.style.WARNING(f"Occured {error[0]} times | {error[1]}\n"))

