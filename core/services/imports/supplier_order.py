import sys
import pandas as pd
from django.db import IntegrityError

from core.mappings.supplier_order import SUPPLIER_COLUMN_MAPPING
from core.models.supplier_order import SupplierOrder
from core.tools.parse import parse_date, parse_decimal, parse_int, parse_currency, parse_unit
from core.tools.row import get_value_mapped, is_fully_invalid_row, is_duplicate_object

# fields that define uniqueness for SupplierOrder
UNIQUE_FIELDS = [
    'supplier', 'order_no', 'number',
    'stone', 'shape', 'color',
    'size', 'carats', 'weight_per_piece'
]

COLUMN_REQUIRED = {
    'order_no',
    'supplier',
    'number',
    'stone',
    'date'
}

MAPPING_CANCELED = {
    'canceled',
    'cancel ',
    'cancel'
}


def get_value(row, field_name):
    return get_value_mapped(row, field_name, SUPPLIER_COLUMN_MAPPING)

def is_canceled(row):
    for field in COLUMN_REQUIRED:
        v = get_value(row, field)
        if v is None or pd.isna(v):
            return True
        if isinstance(v, str) and v.strip().lower() in MAPPING_CANCELED:
            return True
    return False

def check_field(df: pd.DataFrame):
    return "Date" in df.columns

def import_supplier_orders(file_path):
    """Import supplier orders from `file_path`, skipping duplicates (DB and in-memory)."""
    report = {
        "imported": 0,
        "skipped_invalid": 0,
        "skipped_canceled": 0,
        "skipped_not_p": 0,
        "skipped_duplicates": 0,
        "failed_rows": [],
        "messages": [],
        "total": 0,
    }

    # to track in-memory duplicates
    seen_keys = set()
    sheets = pd.read_excel(file_path, sheet_name=None)
    achats = []

    for sheet_name, df in sheets.items():
        valid_count = 0
        if not check_field(df):
            report['messages'].append(
                f"[SKIP] Sheet '{sheet_name}' missing required columns: {list(df.columns)}"
            )
            continue
        report['messages'].append(f"[RUN] Processing sheet: {sheet_name}")

        for idx, row in df.iterrows():
            if is_fully_invalid_row(row):
                continue
            if get_value(row, 'client_memo') in {"M", "B"}:
                report['skipped_not_p'] += 1
                continue
            if is_canceled(row):
                report['skipped_canceled'] += 1
                continue

            try:
                raw_date = get_value(row, 'date')
                date_val = parse_date(raw_date)
                if date_val is None:
                    raise ValueError(f"Invalid date: {raw_date}")

                # build a dict of init kwargs
                kwargs = {
                    'client_memo': get_value(row, 'client_memo') or "P",
                    'date': date_val,
                    'book_no': parse_int(get_value(row, 'book_no') or 0),
                    'order_no': parse_int(get_value(row, 'order_no') or 0),
                    'tax_invoice': get_value(row, 'tax_invoice'),
                    'supplier': get_value(row, 'supplier'),
                    'number': parse_int(get_value(row, 'number') or 0),
                    'stone': get_value(row, 'stone'),
                    'heating': get_value(row, 'heating'),
                    'color': get_value(row, 'color'),
                    'shape': get_value(row, 'shape'),
                    'size': get_value(row, 'size'),
                    'carats': parse_decimal(get_value(row, 'carats')) or 0,
                    'currency': parse_currency(get_value(row, 'currency') or "THB"),
                    'price_cur_per_unit': parse_decimal(get_value(row, 'price_cur_per_unit')) or 0,
                    'unit': parse_unit(get_value(row, 'unit') or "CT"),
                    'total_thb': parse_decimal(get_value(row, 'total_thb')) or 0,
                    'weight_per_piece': parse_decimal(get_value(row, 'weight_per_piece')) if get_value(row, 'weight_per_piece') else None,
                    'price_usd_per_ct': get_value(row, 'price_usd_per_ct'),
                    'price_usd_per_piece': get_value(row, 'price_usd_per_piece'),
                    'total_usd': get_value(row, 'total_usd'),
                    'rate_avg_2019': get_value(row, 'rate_avg_2019'),
                    'remarks': get_value(row, 'remarks'),
                    'credit_term': get_value(row, 'credit_term'),
                    'target_size': get_value(row, 'target_size'),
                }

                # compute in-memory uniqueness key
                key = tuple(kwargs[field] for field in UNIQUE_FIELDS)
                if key in seen_keys:
                    report['skipped_duplicates'] += 1
                    continue

                # instantiate but don't save yet
                achat = SupplierOrder(**kwargs)

                # check DB-level duplicates
                if is_duplicate_object(achat):
                    report['skipped_duplicates'] += 1
                    continue

                # mark this key as seen and queue for bulk_create
                seen_keys.add(key)
                achats.append(achat)
                report['imported'] += 1
                valid_count += 1

            except Exception as e:
                report['skipped_invalid'] += 1
                report['failed_rows'].append({
                    "sheet": sheet_name,
                    "row_index": idx,
                    "error": str(e),
                    "row_data": row.to_dict(),
                })
                report['messages'].append(
                    f"[WARNING] Row {idx} in '{sheet_name}' failed: {e}"
                )

        report['messages'].append(
            f"[DONE] Sheet '{sheet_name}': {valid_count} orders queued."
        )

    report["total"] = (
        report['imported']
        + report['skipped_canceled']
        + report['skipped_invalid']
        + report['skipped_not_p']
        + report['skipped_duplicates']
    )

    # bulk insert, ignoring any remaining DB conflicts
    try:
        SupplierOrder.objects.bulk_create(achats, ignore_conflicts=True)
    except Exception as e:
        # in case of unexpected error, log summary then re-raise
        sys.stdout.write(f"[INFO] Imported: {report['imported']}\n")
        sys.stdout.write(f"[INFO] Skipped duplicates: {report['skipped_duplicates']}\n")
        sys.stdout.write(f"[INFO] Skipped invalid: {report['skipped_invalid']}\n")
        sys.stdout.write(f"[INFO] Skipped canceled: {report['skipped_canceled']}\n")
        sys.stdout.write(f"[INFO] Skipped not-purchase: {report['skipped_not_p']}\n")
        for msg in report['messages']:
            sys.stdout.write(msg + "\n")
        raise

    return report
