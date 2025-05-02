# core/services/supplier_order_raw_import.py

import pandas as pd
from django.db import transaction
from core.models.order_raw import OrderRaw
from core.models.supplier_order_raw import SupplierOrderRaw

class OrderRawImportService:
    """
    Import all rows from an Excel into OrderRaw.
    """

    def __init__(self, file_path: str, order_type: str):
        self.file_path = file_path
        if order_type == 'supplier':
            self.order_model = SupplierOrderRaw 
        elif order_type == 'client':
            ...
        else:
            self.order_model = OrderRaw

    def run(self) -> dict:
        report = {'imported': 0, 'failed': []}

        try:
            sheets = pd.read_excel(self.file_path, sheet_name=None)
        except Exception as e:
            raise RuntimeError(f"Could not read Excel: {e}")

        for sheet_name, df in sheets.items():
            for idx, row in df.iterrows():
                payload = row.to_dict()
                try:
                    with transaction.atomic():
                        self.order_model.objects.create(
                            source_file=self.file_path,
                            sheet_name=sheet_name,
                            row_index=idx,
                            data=payload,
                            success=True
                        )
                    report['imported'] += 1
                except Exception as e:
                    self.order_model.objects.create(
                        source_file=self.file_path,
                        sheet_name=sheet_name,
                        row_index=idx,
                        data=payload,
                        success=False,
                        error=str(e)
                    )
                    report['failed'].append({
                        'sheet': sheet_name,
                        'row': idx,
                        'error': str(e)
                    })

        return report
