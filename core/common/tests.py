import unittest
import pandas as pd
import numpy as np
from decimal import Decimal
from datetime import datetime
from django.test import SimpleTestCase
from django.utils import timezone

from core.common.tools.parse import (
    parse_int, parse_decimal, parse_date, parse_currency, parse_unit
)
from core.common.tools.row import get_value_mapped, is_fully_invalid_row
from core.common.models import Currency


class ParseIntTests(SimpleTestCase):
    def test_simple_digits(self):
        self.assertEqual(parse_int('42'), 42)

    def test_mixed_characters(self):
        self.assertEqual(parse_int('a1b2c3'), 123)

    def test_empty_string_returns_none(self):
        self.assertIsNone(parse_int(''))

    def test_no_digits_returns_none(self):
        self.assertIsNone(parse_int('abc'))


class ParseDecimalTests(SimpleTestCase):
    def test_string_input(self):
        self.assertEqual(parse_decimal('1.234'), Decimal('1.234'))

    def test_float_input(self):
        self.assertEqual(parse_decimal(3.21), Decimal('3.21'))

    def test_invalid_string_returns_default(self):
        self.assertEqual(parse_decimal('abc'), Decimal('0.0'))

    def test_none_returns_default(self):
        self.assertEqual(parse_decimal(None), Decimal('0.0'))


class ParseDateTests(SimpleTestCase):
    def test_iso_string(self):
        dt = parse_date('2025-05-05')
        self.assertIsNotNone(dt)
        self.assertEqual(dt.date(), datetime(2025, 5, 5).date())
        self.assertTrue(timezone.is_aware(dt))

    def test_timestamp_like_numeric(self):
        # Excel float date for 2025-05-05: days since 1899-12-30 ~ 44100+?
        # Use pandas Timestamp to simulate numeric handling
        ts = pd.Timestamp('2025-05-05')
        float_val = ts.to_pydatetime()
        # parse_date should accept numeric timestamp gracefully
        dt = parse_date(ts)
        self.assertEqual(dt.date(), datetime(2025, 5, 5).date())

    def test_none_returns_none(self):
        self.assertIsNone(parse_date(None))


class ParseCurrencyTests(SimpleTestCase):
    def test_canonical_code(self):
        self.assertEqual(parse_currency('USD'), Currency.USD)

    def test_lowercase_alias(self):
        self.assertEqual(parse_currency('us$'), Currency.USD)

    def test_symbol_alias(self):
        self.assertEqual(parse_currency('$'), Currency.USD)

    def test_euro_alias(self):
        self.assertEqual(parse_currency('EURO'), Currency.EUR)

    def test_unknown_raises(self):
        with self.assertRaises(ValueError):
            parse_currency('UNKNOWN')


class ParseUnitTests(SimpleTestCase):
    def test_carat_variants(self):
        for raw in ['CT', 'Ct', 'ct']:
            self.assertEqual(parse_unit(raw), 'CT')

    def test_gram_variants(self):
        for raw in ['G', 'Gram', 'g']:
            self.assertEqual(parse_unit(raw), 'G')

    def test_kg_variants(self):
        for raw in ['KG', 'kg', 'Kg']:
            self.assertEqual(parse_unit(raw), 'KG')

    def test_piece_variants(self):
        for raw in ['PC', 'Pc', 'pc', 'P']:
            self.assertEqual(parse_unit(raw), 'PC')

    def test_total_variants(self):
        for raw in ['T', 'TOTAL', 'total', 'lot']:
            self.assertEqual(parse_unit(raw), 'TOTAL')

    def test_unknown_unit_raises(self):
        with self.assertRaises(ValueError):
            parse_unit('UNKNOWN_UNIT')


class RowToolsTests(SimpleTestCase):
    def test_get_value_mapped_returns_first_match(self):
        row = {'A': 1, 'B': 2, 'C': 3}
        mapping = {'field': {'B', 'C'}}
        self.assertEqual(get_value_mapped(row, 'field', mapping), 2)

    def test_get_value_mapped_missing_returns_none(self):
        row = {'X': 5}
        mapping = {'field': {'A', 'B'}}
        self.assertIsNone(get_value_mapped(row, 'field', mapping))

    def test_is_fully_invalid_all_na(self):
        series = pd.Series({'x': np.nan, 'y': None})
        self.assertTrue(is_fully_invalid_row(series))

    def test_is_fully_invalid_false_if_one_valid(self):
        series = pd.Series({'x': np.nan, 'y': 1})
        self.assertFalse(is_fully_invalid_row(series))


if __name__ == '__main__':
    unittest.main()
