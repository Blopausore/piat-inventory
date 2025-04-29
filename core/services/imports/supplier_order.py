import math
from decimal import Decimal, InvalidOperation
from core.models import SupplierOrder
from django.utils.dateparse import parse_date
import pandas as pd


def safe_decimal(value, default=Decimal('0.0')):
    """Convert to Decimal safely. Return default if value is invalid."""
    if value is None:
        return default
    if isinstance(value, float) and math.isnan(value):
        return default
    try:
        if isinstance(value, str):
            value = ''.join(c for c in value if (c.isdigit() or c in '.-'))  # keep only digits, dot, minus
        return Decimal(value)
    except (InvalidOperation, ValueError):
        return default
    
COLUMN_REQUIRED = {
    'order_no',
    'supplier',
    'number',
    'stone'
}

COLUMN_MAPPING = {
    'client_memo': ['Client Memo', 'Purchase (P) Memo (M) Bargain (B)'],
    'date': ['Date'],
    'book_no': ['Book No.', 'Book No'],
    'order_no': ['No.', 'Order No', 'No'],
    'tax_invoice': ['TAX INVOICE', 'Tax Invoice'],
    'supplier': ['CLIENT', 'Client', 'Supplier'],
    'number': ['PC', 'Pieces', 'Qty'],
    'stone': ['Stone'],
    'heating': ['H/NH', 'Heat/No Heat'],
    'color': ['Color', 'Colour'],
    'shape': ['Shape'],
    'cutting': ['Cutting'],
    'size': ['Size', 'Dimensions'],
    'carats': ['Carats', 'Weight (ct)'],
    'currency': ['US/THB', 'Currency'],
    'price_cur_per_unit': ['price', 'Price'],
    'unit': ['PER', 'Unit'],
    'total_thb': ['Total', 'Total THB', 'THB Total'],
    'weight_per_piece': ['Weight per piece', 'Weight/Piece'],
    'price_usd_per_ct': ['price $/ct ', 'Price $/ct', 'Price per ct $'],
    'price_usd_per_piece': ['price/$ per piece', 'Price/$ per Piece'],
    'total_usd': ['Total $', 'USD Total'],
    'rate_avg_2019': ['Rate $ average 2019', '2019 Rate'],
    'remarks': ['Remarks', 'Notes'],
    'credit_term': ['CREDIT TERM', 'Credit Term'],
    'target_size': ['Target size', 'Target Size'],
}

def get_value(row, field_name):
    possible_columns = COLUMN_MAPPING.get(field_name, [])
    for col in possible_columns:
        if col in row:
            
            if type(row[col]) in {int, float} and pd.isna(row[col]):
                return None
            return row[col]
    return None

MAPPING_CANCELED = {
    'canceled',
    'cancel ',
    'cancel'
}

def is_fully_invalid_row(row):
    return all(pd.isna(value) for value in row.values)

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
    return "Stone" in df.columns
    # for field in COLUMN_REQUIRED:
    #     for mapped_field in COLUMN_MAPPING.get(field, []):
    #         if mapped_field in df.columns
    #     if any(
    #         (mapped_field in df.columns) for mapped_field in COLUMN_MAPPING.get(field)
    #     ):
    #         return False
    
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
            report['messages'].append(f"[SKIP] Sheet '{sheet_name}' does not have required fields. Skipped.")
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

            try:
                achat = SupplierOrder(
                    client_memo=get_value(row, 'client_memo') or "P",
                    date=pd.to_datetime(get_value(row, 'date'), errors='coerce'),
                    book_no=int(get_value(row, 'book_no') or 0),
                    order_no=int(get_value(row, 'order_no') or 0),
                    tax_invoice=get_value(row, 'tax_invoice'),
                    supplier=get_value(row, 'supplier'),
                    number=int(get_value(row, 'number') or 0),
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

    SupplierOrder.objects.bulk_create(achats)

    report["total"] = (
        report['imported'] +
        report["skipped_canceled"] +
        report["skipped_invalid"] +
        report['skipped_not_p']
    )

    return report
