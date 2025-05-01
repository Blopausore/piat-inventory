from decimal import Decimal
from datetime import date

from django.test import TestCase
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from exchange_rate.models import ExchangeRate


class ExchangeRateUniquenessTests(TestCase):
    def setUp(self):
        # 1 USD = 10 IMC (Imaginary Coin) on 2025-05-01
        self.rate = ExchangeRate.objects.create(
            base_currency='IMC',
            date=date(2025, 5, 1),
            price=Decimal('10.0000'),
            open=Decimal('9.5000'),
            high=Decimal('10.5000'),
            low=Decimal('9.0000'),
            change_percent='0.00%'
        )

    def test_duplicate_create_raises_integrity_error(self):
        """
        Tenter de créer une deuxième ligne avec la même base_currency et date
        doit lever un IntegrityError au moment du save()
        """
        with self.assertRaises(IntegrityError):
            ExchangeRate.objects.create(
                base_currency='IMC',
                date=date(2025, 5, 1),
                price=Decimal('11.0000'),
                open=Decimal('10.5000'),
                high=Decimal('11.5000'),
                low=Decimal('10.0000'),
                change_percent='1.00%'
            )

    def test_full_clean_raises_validation_error(self):
        """
        full_clean() doit détecter le doublon (à partir de unique_together)
        et lever un ValidationError avant le save()
        """
        dup = ExchangeRate(
            base_currency='IMC',
            date=date(2025, 5, 1),
            price=Decimal('11.0000'),
            open=Decimal('10.5000'),
            high=Decimal('11.5000'),
            low=Decimal('10.0000'),
            change_percent='1.00%'
        )
        with self.assertRaises(ValidationError):
            dup.full_clean()

    def test_different_currency_same_date_is_allowed(self):
        """
        On peut créer un taux pour une autre devise à la même date sans erreur.
        """
        other = ExchangeRate.objects.create(
            base_currency='XYZ',
            date=date(2025, 5, 1),
            price=Decimal('5.0000'),
            open=Decimal('4.8000'),
            high=Decimal('5.2000'),
            low=Decimal('4.5000'),
            change_percent='0.50%'
        )
        # Vérification que l'objet a bien été sauvegardé
        self.assertEqual(other.base_currency, 'XYZ')
        self.assertEqual(other.date, date(2025, 5, 1))
        self.assertEqual(ExchangeRate.objects.count(), 2)
