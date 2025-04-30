import io
import warnings

from datetime import datetime
import pandas as pd

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse

from core.models import SupplierOrder

class SupplierOrderTests(TestCase):
    def setUp(self):
        warnings.filterwarnings("ignore", category=RuntimeWarning, message="DateTimeField .* received a naive datetime")
  
        self.client = Client()
        self.order = SupplierOrder.objects.create(
            client_memo="P",
            date=datetime(2024, 1, 10),
            book_no=86,
            order_no=4280,
            tax_invoice="072/3566",
            supplier="Kstone",
            number=5,
            stone="Ruby",
            heating="H",
            color="Red",
            shape="Oct",
            cutting="Good",
            size="6x4",
            carats=2.97,
            currency="THB",
            price_cur_per_unit=7000,
            unit="CT",
            total_thb=20790,
            weight_per_piece=0.59,
            price_usd_per_ct=200,
            price_usd_per_piece=118.8,
            total_usd=611.47,
            rate_avg_2019=48.29,
            remarks="Tiffany",
            credit_term="2 months",
            target_size="6x4"
        )

    def test_json_view_returns_data(self):
        response = self.client.get(reverse("supplier_orders_json"))
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertGreater(json_data["recordsTotal"], 0)
        self.assertGreater(len(json_data["data"]), 0)

    def test_export_excel_content(self):
        response = self.client.get(reverse("supplier_orders_export"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", response["Content-Type"])
        df = pd.read_excel(io.BytesIO(response.content))
        self.assertFalse(df.empty)
        self.assertIn("Stone", df.columns)

    def test_update_field_successfully(self):
        response = self.client.post(reverse("supplier_order_update"), {
            "order_id": self.order.id,
            "field_index": 6,  # index of "stone" if ordering is kept
            "new_value": "Sapphire",
            "csrfmiddlewaretoken": "dummy"
        })
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.stone, "Sapphire")

    def test_import_from_excel(self):
        df = pd.DataFrame([{
            "Date": "2024-03-13",
            "Book No.": 86,
            "No.": 4281,
            "TAX INVOICE": "072/9999",
            "CLIENT": "TestSupplier",
            "PC": 3,
            "Stone": "Sapphire",
            "H/NH": "NH",
            "Color": "Blue",
            "Shape": "Oct",
            "Cutting": "Good",
            "Size": "5x4",
            "Carats": 1.20,
            "US/THB": "THB",
            "price": 7000,
            "PER": "CT",
            "Total": 8400,
            "Weight per piece": 0.40,
            "price $/ct ": 200,
            "price/$ per piece": 80,
            "Total $": 247.06,
            "Rate $ average 2019": 48.29,
            "Remarks": "Tiffany",
            "CREDIT TERM": "2 months",
            "Target size": "5x4"
        }])
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        buffer.seek(0)
        upload = SimpleUploadedFile("test_import.xlsx", buffer.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response = self.client.post(reverse("supplier_orders_import_upload"), {'file': upload})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(SupplierOrder.objects.count(), 2)
