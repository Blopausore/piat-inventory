# core/management/commands/import_supplier_raw.py

from django.core.management.base import BaseCommand, CommandError
from core.services.imports.order_raw import OrderRawImportService

class Command(BaseCommand):
    help = "Import raw supplier orders from an Excel file."

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help="Path to the supplier Excel file to import."
        )
        parser.add_argument(
            '--type',
            type=str,
            help="Type of order [supplier, client].",
            default="supplier"
        )

    def handle(self, *args, **kargs):
        file_path = kargs['file_path']
        order_type = kargs['file_path']
        service = OrderRawImportService(file_path, order_type)
        try:
            report = service.run()
        except RuntimeError as e:
            raise CommandError(str(e))

        self.stdout.write(self.style.SUCCESS(
            f"Imported {report['imported']} raw supplier rows."
        ))
        if report['failed']:
            self.stdout.write(self.style.ERROR(
                f"{len(report['failed'])} rows failed to import:"
            ))
            for f in report['failed']:
                self.stdout.write(f"  [Sheet {f['sheet']} row {f['row']}] {f['error']}")
