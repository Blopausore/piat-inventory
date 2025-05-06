from django.core.management.base import BaseCommand
from exchange_rate.models import ExchangeRate
from datetime import datetime
from decimal import Decimal
import csv

class Command(BaseCommand):
    help = 'Import full exchange rate CSV (no volume)'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to the CSV file to import'
        )
        parser.add_argument(
            '--currency',
            type=str,
            default='THB',
            help='Base currency code (e.g. USD or THB)'
        )
        parser.add_argument(
            '--batch_size',
            type=int,
            default=500,
            help='Number of entries to process per batch'
        )
        parser.add_argument(
            '--verbose',
            type=int,
            default=0,
            help='Verbose (0, 1)')
        
    def handle(self, *args, **kargs):
        file_path = kargs['csv_file']
        base_currency = kargs['currency']
        batch_size = kargs['batch_size']
        verbose = kargs['verbose']
        instances = []
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            reader.fieldnames = [field.strip().replace('\ufeff', '').replace('"', '') for field in reader.fieldnames]

            count = 0
            for row in reader:
                try:
                    date = datetime.strptime(row.get('Date', '').strip(), '%m/%d/%Y').date()
                    price = Decimal(row.get('Price', '0').replace(',', ''))
                    open_ = Decimal(row.get('Open', '0').replace(',', ''))
                    high = Decimal(row.get('High', '0').replace(',', ''))
                    low = Decimal(row.get('Low', '0').replace(',', ''))
                    change_percent = row.get('Change %', '').strip() if 'Change %' in row else None
                    if ExchangeRate.objects.filter(
                        date=date,
                        base_currency=base_currency
                    ).exists():
                        raise ValueError(f"This exchange rate already exist : {base_currency} {date}")
                    
                    exchange_rate = ExchangeRate(
                            base_currency=base_currency,
                            date=date,
                            price=price,
                            open=open_,
                            high=high,
                            low=low,
                            change_percent=change_percent
                            
                        )    
                    instances.append(exchange_rate)
                   
                except Exception as e:
                    if verbose > 0:
                        self.stderr.write(self.style.WARNING(f"Error on row {row}: {e}"))
                
                if len(instances) > batch_size:
                    ExchangeRate.objects.bulk_create(
                        instances,
                        batch_size=batch_size)
                    count += len(instances)
                    instances.clear()
            if len(instances) > 0:
                ExchangeRate.objects.bulk_create(
                    instances,
                    batch_size=batch_size)
                count += len(instances)
                instances.clear()
                    
            _style = self.style.SUCCESS if count>0 else self.style.ERROR
            self.stdout.write(_style(f"Imported {count} exchange rate entries."))
