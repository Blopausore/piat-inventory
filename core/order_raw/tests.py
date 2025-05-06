import os
import tempfile
from decimal import Decimal
from datetime import datetime
import pandas as pd
import numpy as np

from django.test import TestCase

from core.order_raw.services.imports import OrderRawImportService
from core.order_raw.models import OrderRaw, SupplierOrderRaw, ClientOrderRaw


class OrderRawImportServiceTests(TestCase):
    def setUp(self):
        # Create a temporary Excel file with two sheets
        self.tmpfile = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        df1 = pd.DataFrame([
            {"A": np.nan, "B": None}, # Invalid
            {"A": 1,     "B": "foo"}, # Invalid
        ])
        df2 = pd.DataFrame([
            {"X": 5.01, "Y": 3.14, "Z": "bar"}, # Valid
            {"X": 5.02, "Y": 3.14, "Z": "bar"}, # Valid
        ])
        # 2 valid | 2 skipped
        
        with pd.ExcelWriter(self.tmpfile.name, engine="openpyxl") as writer:
            df1.to_excel(writer, sheet_name="Sheet1", index=False)
            df2.to_excel(writer, sheet_name="Sheet2", index=False)
        self.tmpfile.close()

    def tearDown(self):
        os.unlink(self.tmpfile.name)

    def test_serialize_value(self):
        svc = OrderRawImportService(self.tmpfile.name, order_type="supplier")
        # NaN -> empty
        self.assertEqual(svc._serialize_value(np.nan), "")
        
        # Numeric types -> str
        self.assertEqual(svc._serialize_value(np.int64(7)), "7")
        self.assertEqual(svc._serialize_value("abc"), "abc")
        self.assertEqual(svc._serialize_value(3.21), "3.21")

    def test_has_meaningful_data(self):
        svc = OrderRawImportService(self.tmpfile.name, order_type="client")
        # All empty or zeros -> False
        self.assertFalse(svc._has_meaningful_data({"a": None, "b": "1", "c": 0, "d": 0.0}))
        # One non-zero -> True
        self.assertTrue(svc._has_meaningful_data({"a": "SomeOneReallyImportant", "b": "HaveOrder", "c": "SOMETHING", "d": 0.0}))
        self.assertTrue(svc._has_meaningful_data({"a": "SomeOneReallyImportant", "b": "1", "c": "1", "d": 0.0}, N=1))

    def test_run_supplier_import(self):
        svc = OrderRawImportService(self.tmpfile.name, order_type="supplier")
        report = svc.run()
        self.assertEqual(report["imported"], 2)
        self.assertEqual(report["skipped"], 2)
        self.assertEqual(SupplierOrderRaw.objects.count(), 2)

    def test_run_client_import(self):
        svc = OrderRawImportService(self.tmpfile.name, order_type="client")
        report = svc.run()
        self.assertEqual(report["imported"], 2)
        self.assertEqual(report["skipped"], 2)
        self.assertEqual(ClientOrderRaw.objects.count(), 2)

    def test_run_default_import(self):
        svc = OrderRawImportService(self.tmpfile.name, order_type="other")
        report = svc.run()
        self.assertEqual(report["imported"], 2)
        self.assertEqual(report.get("skipped", 0), 2)
        self.assertEqual(OrderRaw.objects.count(), 2)


class OrderRawModelTests(TestCase):
    def test_str_methods(self):
        so = SupplierOrderRaw(source_file="f", sheet_name="S1", row_index=3, data={})
        so.save()
        self.assertEqual(str(so), f"RawSupplier #{so.id} – row {so.row_index}")

        co = ClientOrderRaw(source_file="f", sheet_name="S2", row_index=5, data={})
        co.save()
        self.assertEqual(str(co), f"RawClient #{co.id} – row {co.row_index}")
