# core/services/filters/tests/test_filters.py

from decimal import Decimal
from datetime import datetime
from django.test import SimpleTestCase
from core.services.filters.context import TransformContext
from core.services.filters.mapping import MappingFilter
from core.services.filters.type_parsing import TypeParsingFilter
from core.services.filters.validity import SupplierValidityFilter
from core.mappings.supplier_order import SUPPLIER_COLUMN_MAPPING
from core.models.supplier_order import SupplierOrder

class MappingFilterTest(SimpleTestCase):
    def test_mapping_filter_picks_correct_columns(self):
        raw = {
            'Book No.': '123',
            'Date': '2025-05-02T15:30:00',
            'Supplier': 'GemCo'
        }
        ctx = TransformContext(raw, SupplierOrder)
        filt = MappingFilter(field_mapping=SUPPLIER_COLUMN_MAPPING)
        filt.apply(ctx)
        self.assertEqual(ctx.attrs['book_no'], '123')
        self.assertEqual(ctx.attrs['date'], '2025-05-02T15:30:00')
        self.assertEqual(ctx.attrs['supplier'], 'GemCo')

    def test_mapping_filter_with_alternatives(self):
        raw = { 'No.': '456', 'Order No': '789' }
        ctx = TransformContext(raw, SupplierOrder)
        filt = MappingFilter(field_mapping=SUPPLIER_COLUMN_MAPPING)
        filt.apply(ctx)
        # doit prendre la première correspondance trouvée dans la liste
        self.assertEqual(ctx.attrs['order_no'], '456')


class TypeParsingFilterTest(SimpleTestCase):
    def setUp(self):
        # on initialise un contexte minimal
        self.ctx = TransformContext({}, SupplierOrder)
        self.parser = TypeParsingFilter()

    def test_parse_int_and_decimal_and_date(self):
        self.ctx.attrs = {
            'book_no': '42',
            'carats': '1.234',
            'date': '2025-05-02'
        }
        self.parser.apply(self.ctx)
        # int
        self.assertIsInstance(self.ctx.attrs['book_no'], int)
        self.assertEqual(self.ctx.attrs['book_no'], 42)
        # Decimal
        self.assertIsInstance(self.ctx.attrs['carats'], Decimal)
        self.assertEqual(str(self.ctx.attrs['carats']), '1.234')
        # DateTimeField → datetime
        self.assertIsInstance(self.ctx.attrs['date'], datetime)
        self.assertEqual(self.ctx.attrs['date'].date(), datetime(2025, 5, 2).date())

    def test_parse_float_field(self):
        # on force un champ FloatField dans SupplierOrder
        # on ajoute dynamiquement un faux champ pour le test
        from django.db import models
        from core.services.filters.base import BaseTransformFilter

        class DummyContext(TransformContext):
            pass

        # Simule un FloatField
        field = models.FloatField()
        field.name = 'dummy_float'
        # monkey-patch dans _meta
        self.ctx.model_class._meta.local_fields.append(field)

        self.ctx.attrs = {'dummy_float': '3.14'}
        self.parser.apply(self.ctx)
        self.assertIsInstance(self.ctx.attrs['dummy_float'], float)
        self.assertEqual(self.ctx.attrs['dummy_float'], 3.14)


class SupplierValidityFilterTest(SimpleTestCase):
    def setUp(self):
        self.ctx = TransformContext({}, SupplierOrder)
        self.filt = SupplierValidityFilter()

    def test_missing_required_fields(self):
        # sans aucun attrs, on doit détecter les champs requis manquants
        ok = self.filt.apply(self.ctx)
        self.assertFalse(ok)
        # doit mentionner au moins 'date' et 'book_no'
        self.assertIn('date', self.ctx.error)
        self.assertIn('book_no', self.ctx.error)

    def test_all_required_present(self):
        for f in ['date','book_no','order_no','supplier','number','stone',
                  'price_usd_per_piece','total_usd']:
            self.ctx.attrs[f] = 'dummy'
        ok = self.filt.apply(self.ctx)
        self.assertTrue(ok)
        self.assertIsNone(self.ctx.error)

