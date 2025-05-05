import unittest
from decimal import Decimal
from django.test import TestCase
from core.common.tools.parse import parse_unit
from core.services.tools.order_pricing import MissingPriceFiller
from core.models.supplier_order import SupplierOrder
from django.utils import timezone
from exchange_rate.models import ExchangeRate

class ParseUnitTests(TestCase):
    def test_parse_unit_carat_variants(self):
        for raw in ['CT', 'Ct', 'ct']:
            self.assertEqual(parse_unit(raw), 'CT')

    def test_parse_unit_piece_variants(self):
        for raw in ['PC', 'Pc', 'p', 'P', 'pc']:
            self.assertEqual(parse_unit(raw), 'PC')

    def test_parse_unit_gram_variants(self):
        for raw in ['G', 'Gram', 'g']:
            self.assertEqual(parse_unit(raw), 'G')

    def test_parse_unit_kg_variants(self):
        for raw in ['KG', 'kg', 'Kg']:
            self.assertEqual(parse_unit(raw), 'KG')

    def test_parse_unit_total_variants(self):
        for raw in ['T', 'TOTAL', 'total', 'lot']:
            self.assertEqual(parse_unit(raw), 'TOTAL')

    def test_parse_unit_unknown_raises(self):
        with self.assertRaises(ValueError):
            parse_unit('unknown')

class MissingPriceFillerTests(TestCase):
    def setUp(self):
        # create USD rate stub (not used for USD conversion)
        ExchangeRate.objects.create(
            base_currency='THB', date=timezone.now().date(),
            price=Decimal('40.0000'), open=Decimal('39'), high=Decimal('41'), low=Decimal('38'), change_percent=None
        )
        self.filler = MissingPriceFiller(dry_run=False, verbose=False)

    def make_order(self, **kwargs):
        defaults = {
            'unit': 'CT', 'currency': 'USD', 'price_cur_per_unit': Decimal('10.00'),
            'weight_per_piece': Decimal('0.50'), 'carats': Decimal('1.00'),
            'date': timezone.now(), 'client_memo': 'P', 'book_no': 1, 'order_no': 1,
            'supplier': 'Test', 'number': 1, 'stone': 'TestStone', 'heating': None,
            'color': None, 'shape': None, 'size': None,
            'total_thb': Decimal('10.00'), 'price_usd_per_ct': None,
            'price_usd_per_piece': None, 'total_usd': None, 'rate_avg_2019': None,
            'remarks': '', 'credit_term': '', 'target_size': ''
        }
        defaults.update(kwargs)
        return SupplierOrder(**defaults)

    def test_normalize_local_price_ct(self):
        order = self.make_order(unit='ct', price_cur_per_unit=Decimal('5.00'))
        per_ct = self.filler._normalize_local_price(order)
        self.assertEqual(per_ct, Decimal('5.00'))

    def test_normalize_local_price_pc(self):
        order = self.make_order(unit='pc', price_cur_per_unit=Decimal('10.00'), weight_per_piece=Decimal('2.00'))
        per_ct = self.filler._normalize_local_price(order)
        self.assertEqual(per_ct, Decimal('5.00'))

    def test_normalize_local_price_total(self):
        order = self.make_order(unit='TOTAL', price_cur_per_unit=Decimal('20.00'), carats=Decimal('4.00'))
        per_ct = self.filler._normalize_local_price(order)
        self.assertEqual(per_ct, Decimal('5.00'))

    def test_normalize_local_price_gram(self):
        order = self.make_order(unit='g', price_cur_per_unit=Decimal('100.00'))
        per_ct = self.filler._normalize_local_price(order)
        # 100 per gram → per carat: 100 * 0.2 = 20.00
        self.assertEqual(per_ct, Decimal('20.00'))

    def test_normalize_local_price_kg(self):
        order = self.make_order(unit='kg', price_cur_per_unit=Decimal('1000.00'))
        # 1000 per kg → per gram: 1000/1000=1 → per carat: 1*0.2=0.20
        per_ct = self.filler._normalize_local_price(order)
        self.assertEqual(per_ct, Decimal('0.20'))

    def test_fill_order_usd(self):
        order = self.make_order(unit='PC', price_cur_per_unit=Decimal('10.00'), weight_per_piece=Decimal('2.00'))
        self.filler._fill_order(order)
        # local per ct = 5, USD per ct = 5, per piece = 5*2=10, total_usd = 5*1=5
        self.assertEqual(order.price_usd_per_ct, Decimal('5.00'))
        self.assertEqual(order.price_usd_per_piece, Decimal('10.00'))
        self.assertEqual(order.total_usd, Decimal('5.00'))

    def test_fill_order_non_usd(self):
        # Use THB currency with rate 40 THB = 1 USD → 1 THB = 0.025 USD
        order = self.make_order(unit='CT', price_cur_per_unit=Decimal('40.00'), currency='THB')
        self.filler._fill_order(order)
        # local per ct =40 → usd per ct =1.00, per piece & total
        self.assertEqual(order.price_usd_per_ct, Decimal('1.00'))
        self.assertEqual(order.price_usd_per_piece, Decimal('0.50'))
        self.assertEqual(order.total_usd, Decimal('1.00'))

if __name__ == '__main__':
    unittest.main()
