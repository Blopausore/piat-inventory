CANONICAL = {'USD', 'THB', 'EUR', 'GBP', 'JPY'}


CURRENCY_MAPPING = {
    'USD': {'US', '$', 'US$'},
    'THB': {'TH', '฿', 'THBAHT'},
    'EUR': {'EU', '€', 'EURO'},
    
}


def normalize_currency(raw: str) -> str:
    """
    Nettoie et renvoie la forme canonique (trois lettres majuscules) d'une devise.
    Lève ValueError si impossible.
    """
    if not raw:
        raise ValueError("No currency provided")
    txt = raw.strip().upper()
    # correspondance directe
    if txt in CANONICAL:
        return txt
    # correspondance par alias
    for canon, aliases in ALIASES.items():
        if txt in aliases:
            return canon
    raise ValueError(f"Unknown currency: '{raw}'")