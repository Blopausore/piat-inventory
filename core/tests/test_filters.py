# core/services/filters/tests/test_filters.py

from decimal import Decimal
from datetime import datetime

from django.db import models
from django.test import SimpleTestCase
from django.test.utils import isolate_apps

from core.services.filters.context import TransformContext
from core.services.filters.mapping import FieldMappingFilter
from core.services.filters.type_parsing import TypeParsingFilter
from core.services.filters.validity import SupplierValidityFilter
from core.models.order_raw import OrderRaw

@isolate_apps("core")
class FieldMappingFilterTest(SimpleTestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        class OrderTest(models.Model):
            class Meta:
                app_label = 'core'  # pas de migration réelle
            book_no               = models.CharField(max_length=50)
            date                  = models.DateTimeField()
            order_no              = models.CharField(max_length=50)
            supplier              = models.CharField(max_length=50)
            number                = models.IntegerField()
            stone                 = models.CharField(max_length=50)
            price_usd_per_piece   = models.DecimalField(max_digits=10, decimal_places=2)
            total_usd             = models.DecimalField(max_digits=10, decimal_places=2)
        cls.TestModel = OrderTest
        
    def setUp(self):
        self.order_mapping = {
                'date':                 ['Date'],
                'book_no':              ['Book No.', 'Book No'],
                'order_no':             ['No.', 'Order No', 'No'],
                'supplier':             ['CLIENT', 'Client', 'Supplier'],
                'number':               ['PC', 'Pieces', 'Qty'],
                'stone':                ['Stone', '  Stone'],
                'price_usd_per_piece':  ['price/$ per piece', 'Price/$ per Piece'],
                'total_usd':            ['Total $', 'USD Total'],
                
        }
        
    def test_mapping_filter_picks_correct_columns(self):
        raw = {
            'Book No.': '123',
            'Date': '2025-05-02T15:30:00',
            'Supplier': 'GemCo'
        }
    
        ctx = TransformContext(raw, self.TestModel)
        filt = FieldMappingFilter(field_mapping=self.order_mapping)
        filt.apply(ctx)
        self.assertEqual(ctx.attrs['book_no'], '123')
        self.assertEqual(ctx.attrs['date'], '2025-05-02T15:30:00')
        self.assertEqual(ctx.attrs['supplier'], 'GemCo')

    def test_mapping_filter_with_alternatives(self):
        raw = { 'No.': '456', 'Order No': '789' }
        ctx = TransformContext(raw, self.TestModel)
        filt = FieldMappingFilter(field_mapping=self.order_mapping)
        filt.apply(ctx)
        self.assertEqual(ctx.attrs['order_no'], '456')


@isolate_apps("core")
class TypeParsingFilterTest(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        class OrderTest(models.Model):
            class Meta:
                app_label = 'core' 
            book_no               = models.CharField(max_length=50)
            date                  = models.DateTimeField()
            order_no              = models.CharField(max_length=50)
            supplier              = models.CharField(max_length=50)
            number                = models.IntegerField()
            stone                 = models.CharField(max_length=50)
            price_usd_per_piece   = models.DecimalField(max_digits=10, decimal_places=2)
            total_usd             = models.DecimalField(max_digits=10, decimal_places=2)
        cls.TestModel = OrderTest

    def setUp(self):
        self.ctx = TransformContext({}, self.TestModel)
        self.parser = TypeParsingFilter()

    def test_parse_int_and_decimal_and_date(self):
        self.ctx.attrs['book_no'] = '42'
        self.ctx.attrs['carats'] = '1.234'
        self.ctx.attrs['date'] = '2025-01-01'
        self.parser.apply(self.ctx)
        # int
        self.assertIsInstance(self.ctx.attrs['book_no'], int)
        self.assertEqual(self.ctx.attrs['book_no'], 42)
        # Decimal
        self.assertIsInstance(self.ctx.attrs['carats'], Decimal)
        self.assertEqual(str(self.ctx.attrs['carats']), '1.234')
        # DateTimeField → datetime
        self.assertIsInstance(self.ctx.attrs['date'], datetime)
        self.assertEqual(self.ctx.attrs['date'].date(), datetime(2025, 1, 1).date())

@isolate_apps('core')
class SupplierValidityFilterTest(SimpleTestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        class OrderTest(models.Model):
            class Meta:
                app_label = 'core'  # pas de migration réelle
                unique_together = ('date','supplier','order_no')
                constraints = [
                models.UniqueConstraint(
                    fields=list(('date','supplier','order_no')),
                    name='unique_supplier_lot'
                )
        ]
            book_no               = models.CharField(max_length=50, blank=True, null=True)
            date                  = models.DateTimeField()
            order_no              = models.CharField(max_length=50)
            supplier              = models.CharField(max_length=50)
            number                = models.IntegerField(blank=True, null=True)
            stone                 = models.CharField(max_length=50, blank=True, null=True)
            price_usd_per_piece   = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
            total_usd             = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
        cls.TestModel = OrderTest
    
    def setUp(self):
        self.ctx = TransformContext({}, self.TestModel)
        self.filt = SupplierValidityFilter()

    def test_missing_required_fields(self):
        ok = self.filt.apply(self.ctx)
        self.assertFalse(ok)
        self.assertIn('date', self.ctx.error)
        self.assertIn('supplier', self.ctx.error)   

    def test_all_required_present(self):
        for f in ['date','supplier','order_no']:
            self.ctx.attrs[f] = 'dummy'
        ok = self.filt.apply(self.ctx)
        self.assertTrue(ok)
        self.assertIsNone(self.ctx.error)

