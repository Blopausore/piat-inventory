from django.core.management.base import BaseCommand
from core.services.order_pricing import MissingPriceFiller

class Command(BaseCommand):
    help = "Fill missing USD price fields on SupplierOrder."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be updated, without saving."
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Verbose logging of each order processed."
        )

    def handle(self, *args, **options):
        service = MissingPriceFiller(
            dry_run=options["dry_run"],
            verbose=options["verbose"],
        )
        report = service.run()

        self.stdout.write(self.style.SUCCESS(
            f"Processed {report['to_update']} orders, updated {report['updated']}."
        ))
        if report["errors"]:
            self.stdout.write(self.style.WARNING(
                f"{len(report['errors'])} orders failed to convert:"
            ))
            for err in report["errors"]:
                self.stdout.write(f" - Order {err['order_id']}: {err['error']}")
