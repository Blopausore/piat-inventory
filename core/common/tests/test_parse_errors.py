# core/common/tests/test_parse_error_messages.py

from django.test import SimpleTestCase
from core.common.tools.parse import parse_date, parse_unit

class ParseErrorMessagesTests(SimpleTestCase):
    def test_parse_date_invalid_string(self):
        with self.assertRaises(ValueError) as cm:
            parse_date("31-02-2025")

    def test_parse_date_none_returns_none(self):
        self.assertIsNone(parse_date(None))

    def test_parse_unit_unknown_raises_informative_error(self):
        with self.assertRaises(ValueError) as cm:
            parse_unit("XYZ")
