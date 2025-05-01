# core/services/tools/order_pricing.py

import logging
from decimal import Decimal
from django.db.models import Q

from exchange_rate.services.conversion import convert_to_usd, CurrencyConversionError
from core.models import SupplierOrder

logger = logging.getLogger(__name__)

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

    def _fill_order(self, order: SupplierOrder):
        """
        Calcule et assigne :
         - price_usd_per_ct
         - price_usd_per_piece = price_usd_per_ct * weight_per_piece (ou nombre)
         - total_usd = price_usd_per_ct * carats (ou price_usd_per_piece * number)
        """
        # 1) USD price per unit
        if order.currency.upper() == "USD":
            usd_per_ct = order.price_cur_per_unit
        else:
            usd_per_ct = convert_to_usd(
                order.price_cur_per_unit,
                order.date,
                from_currency=order.currency,
            )
        order.price_usd_per_ct = usd_per_ct

        # 2) USD price per piece (si weight_per_piece renseigné)
        if order.weight_per_piece:
            order.price_usd_per_piece = (usd_per_ct * Decimal(order.weight_per_piece)).quantize(Decimal('0.01'))
        else:
            order.price_usd_per_piece = None

        # 3) total USD
        # on calcule sur carats si price_usd_per_ct, sinon sur price_usd_per_piece * number
        if order.price_usd_per_ct is not None:
            order.total_usd = (usd_per_ct * order.carats).quantize(Decimal('0.01'))
        elif order.price_usd_per_piece is not None:
            order.total_usd = (order.price_usd_per_piece * order.number).quantize(Decimal('0.01'))
        else:
            order.total_usd = None
