from decimal import Decimal
from datetime import date

from django.test import TestCase
from exchange_rate.models import ExchangeRate
from core.models.supplier_order import SupplierOrder
from core.services.tools.order_pricing import MissingPriceFiller
from exchange_rate.services.conversion import CurrencyConversionError

class MissingPriceFillerTests(TestCase):
    def setUp(self):
        # Define a fictional currency IMC: 1 USD = 2 IMC
        ExchangeRate.objects.create(
            base_currency='IMC',
            date=date(2025, 5, 1),
            price=Decimal('2.0000'),
            open=Decimal('1.9000'),
            high=Decimal('2.1000'),
            low=Decimal('1.8000'),
            change_percent='0.00%'
        )

    def make_order(self, **kwargs):
        defaults = {
            'client_memo': 'P',
            'date': date(2025, 5, 1),
            'book_no': 1,
            'order_no': 100,
            'tax_invoice': 'T1',
            'supplier': 'ImaginarySup',
            'number': 1,
            'stone': 'FictionStone',
            'heating': None,
            'color': None,
            'shape': None,
            'size': None,
            'carats': Decimal('1.00'),
            'currency': 'IMC',
            'price_cur_per_unit': Decimal('10.00'),
            'unit': 'CT',
            'total_thb': Decimal('10.00'),
            'weight_per_piece': Decimal('0.50'),
            'price_usd_per_ct': None,
            'price_usd_per_piece': None,
            'total_usd': None,
            'rate_avg_2019': None,
            'remarks': '',
            'credit_term': '',
            'target_size': '',
        }
        defaults.update(kwargs)
        return SupplierOrder.objects.create(**defaults)

    def test_fill_single_order_imc(self):
        order = self.make_order(
            price_cur_per_unit=Decimal('10.00'),
            carats=Decimal('2.00'),
            weight_per_piece=Decimal('0.25'),
            currency='IMC',
        )
        service = MissingPriceFiller(dry_run=False, verbose=False)
        report = service.run()

        # Should process one order and update it
        self.assertEqual(report['to_update'], 1)
        self.assertEqual(report['updated'], 1)
        self.assertEqual(report['errors'], [])

        order.refresh_from_db()
        # price_usd_per_ct = 10 IMC → 5 USD
        self.assertEqual(order.price_usd_per_ct, Decimal('5.00'))
        # price_usd_per_piece = 5.00 * 0.25 = 1.25
        self.assertEqual(order.price_usd_per_piece, Decimal('1.25'))
        # total_usd = 5.00 * 2.00 = 10.00
        self.assertEqual(order.total_usd, Decimal('10.00'))

    def test_fill_single_order_usd(self):
        # Even with fictional currency, USD orders pass-through
        order = self.make_order(
            price_cur_per_unit=Decimal('7.00'),
            carats=Decimal('3.00'),
            weight_per_piece=Decimal('1.00'),
            currency='USD',
        )
        service = MissingPriceFiller(dry_run=False, verbose=False)
        report = service.run()

        self.assertEqual(report['to_update'], 1)
        self.assertEqual(report['updated'], 1)
        self.assertEqual(report['errors'], [])

        order.refresh_from_db()
        self.assertEqual(order.price_usd_per_ct, Decimal('7.00'))
        self.assertEqual(order.price_usd_per_piece, Decimal('7.00'))
        self.assertEqual(order.total_usd, Decimal('21.00'))

    def test_dry_run_does_not_persist(self):
        order = self.make_order(price_cur_per_unit=Decimal('8.00'))
        service = MissingPriceFiller(dry_run=True, verbose=False)
        report = service.run()

        self.assertEqual(report['to_update'], 1)
        self.assertEqual(report['updated'], 1)

        order.refresh_from_db()
        self.assertIsNone(order.price_usd_per_ct)
        self.assertIsNone(order.total_usd)

    def test_missing_rate_reports_error(self):
        order = self.make_order(currency='FOO', price_cur_per_unit=Decimal('5.00'))
        service = MissingPriceFiller(dry_run=False, verbose=True)
        report = service.run()

        self.assertEqual(report['to_update'], 1)
        self.assertEqual(report['updated'], 0)
        self.assertEqual(len(report['errors']), 1)
        err = report['errors'][0]
        self.assertEqual(err['order_id'], order.id)
        self.assertIn('No exchange rate available', err['error'])
