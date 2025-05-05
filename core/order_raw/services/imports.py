# core/services/supplier_order_raw_import.py
import pandas as pd
import numpy as np
import numbers

from django.db import transaction

from core.order_raw.models import OrderRaw, SupplierOrderRaw, ClientOrderRaw

class OrderRawImportService:
    """
    Import all rows from an Excel into OrderRaw.
    """

    def __init__(self, file_path: str, order_type: str):
        self.file_path = file_path
        if order_type == 'supplier':
            self.order_model = SupplierOrderRaw 
        elif order_type == 'client':
            self.order_model = ClientOrderRaw
        else:
            self.order_model = OrderRaw

    def _serialize_value(self, v):
        if pd.isna(v):
            return ""
        if isinstance(v, pd.Timestamp):
            return v.to_pydatetime().isoformat()
        return str(v)
        
    def _has_meaningful_data(self, payload: dict) -> bool:
        """
        Renvoie True si au moins un champ a une valeur non vide et non nulle.
        Les chaînes '0' et '0.0' sont traitées comme équivalentes à 0.
        """
        for v in payload.values():
            # None ou chaîne vide
            if v is None or (isinstance(v, str) and v == ""):
                continue
            # Chaîne convertible en nombre
            if isinstance(v, str):
                try:
                    if float(v) == 0:
                        continue
                    return True
                except ValueError:
                    # Non convertible → texte non vide ⇒ significatif
                    return True
            # Nombre Python (int, float, numpy scalar…)
            if isinstance(v, numbers.Number):
                if v == 0:
                    continue
                return True
            # Tout autre type (ex: datetime serialisé) → significatif
            return True
        return False
    
    def run(self) -> dict:
        report = {'imported': 0, 'skipped': 0, 'failed': []}
        sheets = pd.read_excel(self.file_path, sheet_name=None)

        for sheet_name, df in sheets.items():
            instances = []
            for idx, row in df.iterrows():
                payload = {k: self._serialize_value(v) for k, v in row.to_dict().items()}
                if self._has_meaningful_data(payload):
                    instances.append(self.order_model(
                        source_file=self.file_path,
                        sheet_name=sheet_name,
                        row_index=idx,
                        data=payload
                    ))
                else:
                    report['skipped']+=1
            with transaction.atomic():
                self.order_model.objects.bulk_create(instances, batch_size=500)
            report['imported'] += len(instances)

        return report


