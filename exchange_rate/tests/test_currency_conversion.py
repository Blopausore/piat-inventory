from decimal import Decimal
from datetime import date

from django.test import TestCase
from exchange_rate.models import ExchangeRate
from exchange_rate.services.conversion import (
    convert_from_usd,
    convert_to_usd,
    convert,
    CurrencyConversionError,
)

class CurrencyConversionTests(TestCase):
    def setUp(self):
        # Define two imaginary currencies on the same date
        # 1 USD = 2 ABC
        ExchangeRate.objects.create(
            base_currency='ABC',
            date=date(2025, 5, 1),
            price=Decimal('2.0000'),
            open=Decimal('1.9000'),
            high=Decimal('2.1000'),
            low=Decimal('1.8000'),
            change_percent='0.00%'
        )
        # 1 USD = 4 XYZ
        ExchangeRate.objects.create(
            base_currency='XYZ',
            date=date(2025, 5, 1),
            price=Decimal('4.0000'),
            open=Decimal('3.9000'),
            high=Decimal('4.1000'),
            low=Decimal('3.8000'),
            change_percent='0.00%'
        )

    def test_convert_from_usd_to_abc(self):
        # 5 USD -> 10 ABC
        result = convert_from_usd(Decimal('5'), date(2025, 5, 1), to_currency='ABC')
        self.assertEqual(result, Decimal('10.0000'))

    def test_convert_to_usd_from_abc(self):
        # 10 ABC -> 5 USD
        result = convert_to_usd(Decimal('10'), date(2025, 5, 1), from_currency='ABC')
        self.assertEqual(result, Decimal('5.0000'))

    def test_cross_conversion_abc_to_xyz(self):
        # 10 ABC -> 5 USD -> 20 XYZ
        result = convert(Decimal('10'), date(2025, 5, 1), from_currency='ABC', to_currency='XYZ')
        self.assertEqual(result, Decimal('20.0000'))

    def test_cross_conversion_xyz_to_abc(self):
        # 20 XYZ -> 5 USD -> 10 ABC
        result = convert(Decimal('20'), date(2025, 5, 1), from_currency='XYZ', to_currency='ABC')
        self.assertEqual(result, Decimal('10.0000'))

    def test_identity_conversion_usd(self):
        # USD to USD remains unchanged
        amount = Decimal('123.45')
        self.assertEqual(convert(amount, date(2025, 5, 1), from_currency='USD', to_currency='USD'), amount)

    def test_missing_rate_raises_for_imaginary(self):
        # No rate defined for currency 'FOO' on that date
        with self.assertRaises(CurrencyConversionError):
            convert_from_usd(Decimal('1'), date(2025, 5, 1), to_currency='FOO')
        with self.assertRaises(CurrencyConversionError):
            convert_to_usd(Decimal('1'), date(2025, 5, 1), from_currency='FOO')
