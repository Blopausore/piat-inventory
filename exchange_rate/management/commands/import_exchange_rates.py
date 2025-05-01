import csv
from datetime import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from exchange_rate.models import ExchangeRate

# exchange_rate/management/commands/import_exchange_rates.py

from django.core.management.base import BaseCommand
from exchange_rate.models import ExchangeRate
from datetime import datetime
from decimal import Decimal
import csv

class Command(BaseCommand):
    help = 'Import full exchange rate CSV (no volume)'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)
        parser.add_argument('--currency',  type=str, default='THB', help='Base currency, e.g. USD or THB')

    def handle(self, *args, **kargs):
        file_path = kargs['csv_file']
        base_currency = kargs['currency']
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            # if '\ufeffDate' in reader.fieldnames:
            #     reader.fieldnames = [field.replace('\ufeff', '') for field in reader.fieldnames]
            reader.fieldnames = [field.strip().replace('\ufeff', '').replace('"', '') for field in reader.fieldnames]

            count = 0
            for row in reader:
                try:
                    date = datetime.strptime(row.get('Date', '').strip(), '%m/%d/%Y').date()
                    price = Decimal(row.get('Price', '0').replace(',', ''))
                    open_ = Decimal(row.get('Open', '0').replace(',', ''))
                    high = Decimal(row.get('High', '0').replace(',', ''))
                    low = Decimal(row.get('Low', '0').replace(',', ''))
                    change = row.get('Change %', '').strip() if 'Change %' in row else None

                    ExchangeRate.objects.update_or_create(
                        date=date,
                        defaults={
                            'base_currency': base_currency,
                            'price': price,
                            'open': open_,
                            'high': high,
                            'low': low,
                            'change_percent': change,
                            'usd_to_thb': price,
                            'thb_to_usd': Decimal(1) / price
                        }
                    )
                    count += 1
                except Exception as e:
                    self.stderr.write(f"Error on row {row}: {e}")
            self.stdout.write(f"Imported {count} exchange rate entries.")
