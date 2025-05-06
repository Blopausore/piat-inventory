
SUPPLIER_ORDER_FIELDS = [
    ("date", "Date"),
    ("book_no", "Book No."),
    ("order_no", "Order No."),
    ("tax_invoice", "Tax Invoice"),
    ("supplier", "Supplier"),
    ("number", "PC"),
    ("stone", "Stone"),
    ("heating", "H/NH"),
    ("color", "Color"),
    ("shape", "Shape"),
    ("size", "Size"),
    ("carats", "Carats"),
    ("currency", "Currency (US/THB)"),
    ("price_cur_per_unit", "Price per Unit"),
    ("unit", "PER"),
    ("total_thb", "Total THB"),
    ("weight_per_piece", "Weight per Piece"),
    ("price_usd_per_ct", "Price $/ct"),
    ("price_usd_per_piece", "Price $ per Piece"),
    ("total_usd", "Total USD"),
    ("rate_avg_2019", "Rate Avg 2019"),
    ("remarks", "Remarks"),
    ("credit_term", "Credit Term"),
    ("target_size", "Target Size"),
]


RAW_SUPPLIER_COLUMN_MAPPING = {
    'client_memo':          ['Client Memo', 'Purchase (P) Memo (M) Bargain (B)', 'Purchase(P)\nMemo (M)\nBargain (B)'],
    'date':                 ['Date'],
    'book_no':              ['Book No.', 'Book No'],
    'order_no':             ['No.', 'Order No', 'No'],
    'tax_invoice':          ['TAX INVOICE', 'Tax Invoice'],
    'supplier':             ['CLIENT', 'Client', 'Supplier'],
    'number':               ['PC', 'Pieces', 'Qty'],
    'stone':                ['Stone', '  Stone'],
    'heating':              ['H/NH', 'Heat/No Heat'],
    'color':                ['Color', 'Colour'],
    'shape':                ['Shape'],
    'size':                 ['Size', 'Dimensions'],
    'carats':               ['Carats', 'Weight (ct)'],
    'currency':             ['US/THB', 'Currency'],
    'price_cur_per_unit':   ['price', 'Price'],
    'unit':                 ['PER', 'Unit'],
    'total_thb':            ['Total', 'Total THB', 'THB Total'],
    'weight_per_piece':     ['Weight per piece', 'Weight/Piece'],
    'price_usd_per_ct':     ['price $/ct ', 'Price $/ct', 'Price per ct $'],
    'price_usd_per_piece':  ['price/$ per piece', 'Price/$ per Piece'],
    'total_usd':            ['Total $', 'USD Total'],
    'rate_avg_2019':        ['Rate $ average 2019', '2019 Rate'],
    'remarks':              ['Remarks', 'Notes'],
    'credit_term':          ['CREDIT TERM', 'Credit Term'],
    'target_size':          ['Target size', 'Target Size'],
}

SUPPLIER_COLUMN_MAPPING = {
    'date':                 ['Date'],
    'book_no':              ['Book No.', 'Book No'],
    'order_no':             ['No.', 'Order No', 'No'],
    'supplier':             ['CLIENT', 'Client', 'Supplier'],
    'number':               ['PC', 'Pieces', 'Qty'],
    'stone':                ['Stone', '  Stone'],
    'heating':              ['H/NH', 'Heat/No Heat'],
    'color':                ['Color', 'Colour'],
    'shape':                ['Shape'],
    'size':                 ['Size', 'Dimensions'],
    'carats':               ['Carats', 'Weight (ct)'],
    'weight_per_piece':     ['Weight per piece', 'Weight/Piece'],
    'price_usd_per_ct':     ['price $/ct ', 'Price $/ct', 'Price per ct $', 'price/$ '],
    'price_usd_per_piece':  ['price/$ per piece', 'Price/$ per Piece'],
    'total_usd':            ['Total $', 'USD Total'],
}


INVERSE_SUPPLIER_COLUMN_MAPPING = {
    alias: field
    for field, aliases in SUPPLIER_COLUMN_MAPPING.items()
    for alias in aliases
}
