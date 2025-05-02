import os
import tempfile
from decimal import Decimal
from datetime import datetime
import pandas as pd
import numpy as np

from django.test import TestCase
from core.services.imports.order_raw import OrderRawImportService
from core.models.order_raw import OrderRaw, SupplierOrderRaw, ClientOrderRaw

class OrderRawImportServiceTest(TestCase):
    def setUp(self):
        self.tmpfile = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        df1 = pd.DataFrame([
            {"A": np.nan, "B": None},
            {"A": 1,     "B": "foo"},
        ])
        df2 = pd.DataFrame([
            {"X": 0, "Y": 0.0, "Z": ""},   
            {"X": 5, "Y": 3.14, "Z": "bar"},
        ])
        with pd.ExcelWriter(self.tmpfile.name, engine="openpyxl") as writer:
            df1.to_excel(writer, sheet_name="Feuille1", index=False)
            df2.to_excel(writer, sheet_name="Feuille2", index=False)
        self.tmpfile.close()

    def tearDown(self):
        os.unlink(self.tmpfile.name)

    def test_serialize_value(self):
        svc = OrderRawImportService(self.tmpfile.name, order_type="supplier")
        self.assertIsNone(svc._serialize_value(np.nan))
        ts = pd.Timestamp("2025-05-02T13:45:00")
        iso = svc._serialize_value(ts)
        self.assertIsInstance(iso, str)
        self.assertTrue(iso.startswith("2025-05-02T13:45"))
        self.assertEqual(svc._serialize_value(np.int64(7)), 7)
        self.assertEqual(svc._serialize_value("abc"), "abc")
        self.assertEqual(svc._serialize_value(3.21), 3.21)

    def test_has_meaningful_data(self):
        svc = OrderRawImportService(self.tmpfile.name, order_type="client")
        self.assertFalse(svc._has_meaningful_data({
            "a": None, "b": "", "c": 0, "d": 0.0
        }))
        self.assertTrue(svc._has_meaningful_data({
            "a": None, "b": "", "c": 1, "d": 0.0
        }))

    def test_run_creates_and_skips(self):
        svc = OrderRawImportService(self.tmpfile.name, order_type="supplier")
        report = svc.run()
        self.assertEqual(report["imported"], 2)
        self.assertEqual(report["skipped"], 2)
        self.assertEqual(SupplierOrderRaw.objects.count(), 2)
        raws = list(SupplierOrderRaw.objects.order_by("row_index"))
        self.assertEqual(raws[0].sheet_name, "Feuille1")
        self.assertEqual(raws[1].sheet_name, "Feuille2")

        # svc_cli = OrderRawImportService(self.tmpfile.name, order_type="client")
        # report_cli = svc_cli.run()
        # self.assertEqual(report_cli["imported"], 2)
        # self.assertEqual(ClientOrderRaw.objects.count(), 2)

    def test_default_order_model(self):
        svc = OrderRawImportService(self.tmpfile.name, order_type="other")
        report = svc.run()
        self.assertEqual(report["imported"], 2)
        self.assertEqual(OrderRaw.objects.count(), 2)
