# core/services/tools/order_pricing.py

import logging
from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Q

from core.models.supplier_order import SupplierOrder
from core.tools.parse import parse_unit
from exchange_rate.services.conversion import convert_to_usd, CurrencyConversionError


logger = logging.getLogger(__name__)

CARAT_IN_GRAM = Decimal('0.2')

class MissingPriceFiller:
    """
    Service pour remplir les champs price_usd_per_ct, price_usd_per_piece, total_usd
    sur les SupplierOrder où ils sont manquants.
    """

    def __init__(self, dry_run: bool = False, verbose: bool = False):
        self.dry_run = dry_run
        self.verbose = verbose

    def run(self) -> dict:
        """Exécute le processus et renvoie un rapport."""
        qs = SupplierOrder.objects.filter(
            Q(price_usd_per_ct__isnull=True)
            | Q(price_usd_per_piece__isnull=True)
            | Q(total_usd__isnull=True)
        )
        report = {
            "to_update": qs.count(),
            "updated": 0,
            "errors": [],
        }

        for order in qs.order_by("date"):
            try:
                self._fill_order(order)
                if not self.dry_run:
                    order.save(update_fields=[
                        "price_usd_per_ct",
                        "price_usd_per_piece",
                        "total_usd",
                    ])
                report["updated"] += 1
                if self.verbose:
                    logger.info(f"Filled prices for order {order.id}")
            except CurrencyConversionError as e:
                report["errors"].append({
                    "order_id": order.id,
                    "error": str(e),
                })
                if self.verbose:
                    logger.warning(f"Conversion failed for order {order.id}: {e}")
                continue
            except Exception as e:
                report["errors"].append({
                    "order_id": order.id,
                    "error": f"Unexpected error: {e}",
                })
                logger.exception(f"Unexpected error on order {order.id}")
                continue

        return report

    def _normalize_local_price(self, order: SupplierOrder) -> Decimal:
        """
        Return the standardized local price per carat based on order.unit,
        now handling CT, PC, TOTAL, G (gram) and KG (kilogram).
        """
        unit = parse_unit(order.unit)
        price = Decimal(order.price_cur_per_unit)

        if unit == 'CT':
            # already price per carat
            per_ct = price

        elif unit == 'PC':
            # price per piece → price per carat
            if not order.weight_per_piece:
                raise ValueError(f"Missing weight_per_piece for unit '{unit}' on order {order.id}")
            per_ct = price / Decimal(order.weight_per_piece)

        elif unit == 'TOTAL':
            # total price → price per carat
            if order.carats == 0:
                raise ValueError(f"Missing carats for TOTAL unit on order {order.id}")
            per_ct = price / Decimal(order.carats)

        elif unit == 'G':
            # price per gram → price per carat
            per_ct = price * CARAT_IN_GRAM

        elif unit == 'KG':
            # price per kilogram → price per carat
            # price per gram = price / 1000
            per_ct = (price / Decimal('1000')) * CARAT_IN_GRAM

        else:
            raise ValueError(f"Unknown unit '{unit}' on order {order.id}")

        return per_ct.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def _to_usd(self, local_amount: Decimal, order: SupplierOrder) -> Decimal:
        """
        Convert a local currency amount to USD, rounded to 2 decimals.
        """
        if order.currency.upper() == 'USD':
            return local_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        usd_amount = convert_to_usd(local_amount, order.date, from_currency=order.currency)
        return usd_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def _fill_order(self, order: SupplierOrder):
        """
        Populate price_usd_per_ct, price_usd_per_piece, and total_usd fields.
        """
        # 1) Compute local price per carat
        local_per_ct = self._normalize_local_price(order)

        # 2) Convert to USD per carat
        usd_per_ct = self._to_usd(local_per_ct, order)
        order.price_usd_per_ct = usd_per_ct

        # 3) Compute USD price per piece if weight_per_piece is provided
        if order.weight_per_piece:
            usd_per_piece = usd_per_ct * Decimal(order.weight_per_piece)
            order.price_usd_per_piece = usd_per_piece.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        else:
            order.price_usd_per_piece = None

        # 4) Compute total USD based on carats
        total_usd = usd_per_ct * Decimal(order.carats)
        order.total_usd = total_usd.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)