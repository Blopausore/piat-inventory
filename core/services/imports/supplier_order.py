import sys
import pandas as pd
from django.utils.dateparse import parse_date
from django.db import IntegrityError

from core.mappings.supplier_order import SUPPLIER_COLUMN_MAPPING
from core.models import SupplierOrder
from core.tools.parse import safe_parse_date, safe_decimal, safe_parse_int
from core.tools.row import get_value_mapped, is_fully_invalid_row, is_duplicate_object


COLUMN_REQUIRED = {
    'order_no',
    'supplier',
    'number',
    'stone',
    'date'
}

def get_value(row, field_name):
    return get_value_mapped(row, field_name, SUPPLIER_COLUMN_MAPPING)

MAPPING_CANCELED = {
    'canceled',
    'cancel ',
    'cancel'
}

def is_canceled(row):
    # Filtering invalid line
    for field in COLUMN_REQUIRED:
        v = get_value(row, field)
        if v is None or pd.isna(v):
            return True
        if type(v) is str and str.lower(v) in MAPPING_CANCELED:
            return True
    return False

def check_field(df: pd.DataFrame):
    return "Date" in df.columns
    
# Main Function

def import_supplier_orders(file_path):
    """Import the suppliers orders that are in 'file_path'."""
    report = {
        "imported": 0,
        "skipped_invalid": 0,
        "skipped_canceled": 0,
        "skipped_not_p": 0,
        "failed_rows": [],
        "messages": [],
        "total": 0,
    }

    sheets = pd.read_excel(file_path, sheet_name=None)
    achats = []

    for sheet_name, df in sheets.items():
        sheet_valid_order_counter = 0
        if not check_field(df):
            report['messages'].append(f"[SKIP] Sheet '{sheet_name}' does not have required fields : {df.columns} ")
            continue

        report['messages'].append(f"[RUN] Processing sheet: {sheet_name}")

        for index, row in df.iterrows():
            if is_fully_invalid_row(row):
                continue

            if get_value(row, 'client_memo') in {"M", "B"}:
                report['skipped_not_p'] += 1
                continue

            if is_canceled(row):
                report['skipped_canceled'] += 1
                continue
            
            date_value=safe_parse_date(get_value(row, 'date'))
            
            try:
                if date_value is None:
                    raise Exception("No date value or misread {}".format(date_value))
                
                achat = SupplierOrder(
                    client_memo=get_value(row, 'client_memo') or "P",
                    date=safe_parse_date(get_value(row, 'date'), sheet_name),
                    book_no=safe_parse_int(get_value(row, 'book_no') or 0),
                    order_no=safe_parse_int(get_value(row, 'order_no') or 0),
                    tax_invoice=get_value(row, 'tax_invoice'),
                    supplier=get_value(row, 'supplier'),
                    number=safe_parse_int(get_value(row, 'number') or 0),
                    stone=get_value(row, 'stone'),
                    heating=get_value(row, 'heating'),
                    color=get_value(row, 'color'),
                    shape=get_value(row, 'shape'),
                    cutting=get_value(row, 'cutting'),
                    size=get_value(row, 'size'),
                    carats=safe_decimal(get_value(row, 'carats')) or 0,
                    currency=get_value(row, 'currency') or "THB",
                    price_cur_per_unit=safe_decimal(get_value(row, 'price_cur_per_unit')) or 0,
                    unit=get_value(row, 'unit') or "CT",
                    total_thb=safe_decimal(get_value(row, 'total_thb')) or 0,
                    weight_per_piece=get_value(row, 'weight_per_piece'),
                    price_usd_per_ct=get_value(row, 'price_usd_per_ct'),
                    price_usd_per_piece=get_value(row, 'price_usd_per_piece'),
                    total_usd=get_value(row, 'total_usd'),
                    rate_avg_2019=get_value(row, 'rate_avg_2019'),
                    remarks=get_value(row, 'remarks'),
                    credit_term=get_value(row, 'credit_term'),
                    target_size=get_value(row, 'target_size'),
                )
                if is_duplicate_object(achat):
                    raise IntegrityError
                achats.append(achat)
                report["imported"] += 1
                sheet_valid_order_counter += 1

            except Exception as e:
                report['skipped_invalid'] += 1
                report['failed_rows'].append({
                    "sheet": sheet_name,
                    "row_index": index,
                    "error": str(e),
                    "row_data": row.values.tolist(),
                })
                report['messages'].append(
                    f"[WARNING] Failed to import row {index} in sheet {sheet_name}: {str(e)}"
                )

        report['messages'].append(
            f"[DONE] Finished processing sheet {sheet_name}: {sheet_valid_order_counter} rows added."
        )
    report["total"] = (
        report['imported'] +
        report["skipped_canceled"] +
        report["skipped_invalid"] +
        report['skipped_not_p']
    )
    try:
        SupplierOrder.objects.bulk_create(achats, ignore_conflicts=True)

    except Exception as e:
        sys.stdout.write(f"[INFO] {report['imported']} rows imported on.\n")
        sys.stdout.write(f"[INFO] {len(report['failed_rows'])} rows failed to import.\n")
        sys.stdout.write(f"[INFO] {report['skipped_canceled']} canceled orders skipped.\n")
        sys.stdout.write(f"[INFO] {report['skipped_not_p']} non-purchase orders skipped.\n")
        
        for message in report['messages']:
            sys.stdout.write(message+"\n")
        raise e

    return report
