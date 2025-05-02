# core/services/supplier_order_interpret.py

import logging
from decimal import Decimal
from django.db import transaction

from core.models.supplier_order import SupplierOrder
from core.models.supplier_order_raw import SupplierOrderRaw
from core.tools.parse import (
    parse_date, parse_int, parse_decimal,
    parse_currency, parse_unit
)
from core.tools.row import get_value_mapped, is_duplicate_object
from core.mappings.supplier_order import SUPPLIER_COLUMN_MAPPING

logger = logging.getLogger(__name__)

def get_value(value, field):
    return get_value_mapped(value, field, SUPPLIER_COLUMN_MAPPING)

class SupplierOrderInterpretService:
    """
    Service that transforms imported SupplierOrderRaw rows
    into cleaned SupplierOrder instances.
    """

    def run(self) -> dict:
        report = {
            'created': 0,
            'skipped_dup': 0,
            'errors': []
        }

        # only raws successfully imported and not yet interpreted
        raws = SupplierOrderRaw.objects.filter(
            success=True,
            interpreted__isnull=True
        )

        for raw in raws:
            data = raw.data
            try:
                # build the kwargs for SupplierOrder
                kwargs = {
                    'raw':                  raw,
                    'date':                 parse_date(get_value(data, 'date')),
                    'book_no':              parse_int(get_value(data, 'book_no') or 0),
                    'order_no':             parse_int(get_value(data, 'order_no') or 0),
                    'tax_invoice':          get_value(data, 'tax_invoice'),
                    'supplier':             get_value(data, 'supplier').strip(),
                    'number':               parse_int(get_value(data, 'number') or 0),
                    'stone':                get_value(data, 'stone'),
                    'heating':              get_value(data, 'heating'),
                    'color':                get_value(data, 'color').strip().capitalize(),
                    'shape':                get_value(data, 'shape').strip().upper(),
                    'cutting':              get_value(data, 'cutting'),
                    'size':                 get_value(data, 'size'),
                    'carats':               parse_decimal(get_value(data, 'carats') or 0),
                    'price_cur_per_unit':   parse_decimal(get_value(data, 'price_cur_per_unit') or 0),
                    'total_thb':            parse_decimal(get_value(data, 'total_thb') or 0),
                    'weight_per_piece':     parse_decimal(get_value(data, 'weight_per_piece') or 0),
                }

                # instantiate without saving
                order = SupplierOrder(**kwargs)

                # skip duplicates
                if is_duplicate_object(order):
                    report['skipped_dup'] += 1
                    continue

                # validate and save within a transaction
                with transaction.atomic():
                    order.full_clean()
                    order.save()

                report['created'] += 1

            except Exception as exc:
                logger.exception(f"Interpretation failed for raw #{raw.id}")
                report['errors'].append({
                    'raw_id': raw.id,
                    'error': str(exc)
                })
                # mark raw error
                raw.error = str(exc)
                raw.save(update_fields=['error'])
                continue

        return report
