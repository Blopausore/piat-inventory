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
            total_imported = import_supplier_orders(file_path)
            self.stdout.write(self.style.SUCCESS(f"[DONE] Import completed. {total_imported} supplier orders inserted."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"[ERROR] An error occurred during import: {str(e)}"))
