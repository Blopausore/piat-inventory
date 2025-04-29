# core/management/commands/import_supplier_orders.py

from django.core.management.base import BaseCommand
from core.services.imports.supplier_order import import_supplier_orders 

class Command(BaseCommand):
    help = "Import supplier orders from an Excel file (.xls/.xlsx)."

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help="The path to the Excel file containing the supplier orders."
        )

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']

        self.stdout.write(self.style.WARNING(f"Importing supplier orders from {file_path}..."))

        try:
            report = import_supplier_orders(file_path)
            
            self.stdout.write(self.style.SUCCESS(
                f"[DONE] Import completed. {report['imported']}/{report['total']} supplier orders inserted."
            ))

            self.stdout.write(f"[INFO] {len(report['failed_rows'])} rows failed to import.")
            self.stdout.write(f"[INFO] {report['skipped_canceled']} canceled orders skipped.")
            self.stdout.write(f"[INFO] {report['skipped_not_p']} non-purchase orders skipped.")

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"[ERROR] An error occurred during import: {str(e)}"))
