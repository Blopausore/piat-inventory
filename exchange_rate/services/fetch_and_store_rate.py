import requests
from decimal import Decimal
from datetime import date
from django.conf import settings
from exchange_rate.models import ExchangeRate

API_URL = "https://api.apilayer.com/exchangerates_data/"

def fetch_and_store_exchange_rate(target_date: date, base_currency="USD"):
    formatted_date = target_date.isoformat()
    api_key = settings.EXCHANGE_RATE_API_KEY

    if not api_key:
        raise ValueError("Missing API key for exchange rate service.")

    url = f"{API_URL}{formatted_date}?base={base_currency}&symbols=THB"
    headers = {"apikey": api_key}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise ValueError(f"API Error: {response.status_code} - {response.text}")

    data = response.json()
    try:
        usd_to_thb = Decimal(data["rates"]["THB"])
        thb_to_usd = Decimal("1.0") / usd_to_thb
    except Exception as e:
        raise ValueError(f"Invalid response format: {data}") from e

    ExchangeRate.objects.update_or_create(
        date=target_date,
        base_currency=base_currency,
        defaults={
            "price": usd_to_thb,
            "open": usd_to_thb,
            "high": usd_to_thb,
            "low": usd_to_thb,
            "change_percent": None,
            "usd_to_thb": usd_to_thb,
            "thb_to_usd": thb_to_usd
        }
    )
