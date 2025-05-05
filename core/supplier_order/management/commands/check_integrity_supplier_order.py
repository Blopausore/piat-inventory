# core/management/commands/check_data_integrity.py

import json
from datetime import date
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Count, Q

from core.supplier_order.models import SupplierOrder
from core.client_order.models import ClientOrder
from exchange_rate.models import ExchangeRate

class Command(BaseCommand):
    help = "Check data integrity across key models and report anomalies."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            type=str,
            help="Optional path to write full JSON report"
        )
        parser.add_argument(
            "--details",
            action="store_true",
            help="Also print detailed records for each anomaly type"
        )

    def handle(self, *args, **options):
        now = timezone.now()
        today = now.date()
        report = {}

        # 1) DUPLICATE SupplierOrder
        dup_so = (
            SupplierOrder.objects
            .values(
                "supplier", "order_no", "number",
                "stone", "shape", "color",
                "size", "carats"
            )
            .annotate(cnt=Count("id"))
            .filter(cnt__gt=1)
        )
        report["duplicate_supplier_orders"] = []
        for entry in dup_so:
            filters = {
                k: entry[k] for k in entry.keys() if k != "cnt"
            }
            qs = SupplierOrder.objects.filter(**filters)
            for so in qs:
                report["duplicate_supplier_orders"].append({
                    "id": so.id,
                    "order_no": so.order_no,
                    "fields": filters
                })

        # 2) DUPLICATE ClientOrder
        dup_co = (
            ClientOrder.objects
            .values("date", "order_no")
            .annotate(cnt=Count("id"))
            .filter(cnt__gt=1)
        )
        report["duplicate_client_orders"] = []
        for entry in dup_co:
            qs = ClientOrder.objects.filter(
                date=entry["date"], order_no=entry["order_no"]
            )
            for co in qs:
                report["duplicate_client_orders"].append({
                    "id": co.id,
                    "order_no": co.order_no,
                    "fields": {"date": str(co.date), "order_no": co.order_no}
                })

        # 3) FUTURE DATES
        report["future_supplier_orders"] = []
        for so in SupplierOrder.objects.filter(date__gt=now):
            report["future_supplier_orders"].append({
                "id": so.id,
                "order_no": so.order_no,
                "fields": {"date": str(so.date)}
            })
        report["future_client_orders"] = []
        for co in ClientOrder.objects.filter(date__gt=now):
            report["future_client_orders"].append({
                "id": co.id,
                "order_no": co.order_no,
                "fields": {"date": str(co.date)}
            })
        report["future_exchange_rates"] = []
        for er in ExchangeRate.objects.filter(date__gt=today):
            report["future_exchange_rates"].append({
                "id": er.id,
                "fields": {"base_currency": er.base_currency, "date": str(er.date)}
            })

        # 4) MISSING USD PRICES on SupplierOrder
        report["supplier_orders_missing_usd"] = []
        qs_missing = SupplierOrder.objects.filter(
            Q(price_usd_per_ct__isnull=True) |
            Q(price_usd_per_piece__isnull=True) |
            Q(total_usd__isnull=True)
        )
        for so in qs_missing:
            missing = []
            if so.price_usd_per_ct is None:
                missing.append("price_usd_per_ct")
            if so.price_usd_per_piece is None:
                missing.append("price_usd_per_piece")
            if so.total_usd is None:
                missing.append("total_usd")
            report["supplier_orders_missing_usd"].append({
                "id": so.id,
                "order_no": so.order_no,
                "missing_fields": missing
            })

        # 5) ORDERS WITHOUT MATCHING RATE
        report["orders_without_exchange_rate"] = []
        combos = (
            SupplierOrder.objects
            .exclude(currency="USD")
            .values("currency", "date")
            .distinct()
        )
        for combo in combos:
            if not ExchangeRate.objects.filter(
                base_currency=combo["currency"], date=combo["date"]
            ).exists():
                # lister toutes les commandes posant problème
                for so in SupplierOrder.objects.filter(
                    currency=combo["currency"], date=combo["date"]
                ):
                    report["orders_without_exchange_rate"].append({
                        "id": so.id,
                        "order_no": so.order_no,
                        "fields": {"currency": so.currency, "date": str(so.date)}
                    })

        # 6) NEGATIVE OR ZERO VALUES
        report["supplier_orders_invalid_values"] = []
        qs_bad = SupplierOrder.objects.filter(
            Q(price_cur_per_unit__lte=0) |
            Q(total_thb__lte=0) |
            Q(carats__lte=0)
        )
        for so in qs_bad:
            bad = {}
            if so.price_cur_per_unit <= 0:
                bad["price_cur_per_unit"] = str(so.price_cur_per_unit)
            if so.total_thb <= 0:
                bad["total_thb"] = str(so.total_thb)
            if so.carats <= 0:
                bad["carats"] = str(so.carats)
            report["supplier_orders_invalid_values"].append({
                "id": so.id,
                "order_no": so.order_no,
                "invalid_fields": bad
            })

        # --- Output summary ---
        self.stdout.write(self.style.MIGRATE_HEADING("Integrity Check Summary:"))
        for key, items in report.items():
            self.stdout.write(f"  {key}: {len(items)} issue{'s' if len(items) != 1 else ''}")

        # Details?
        if options["details"]:
            self.stdout.write(self.style.MIGRATE_LABEL("\nDetails:"))
            for key, items in report.items():
                if not items:
                    continue
                self.stdout.write(self.style.NOTICE(f"\n{key}"))
                for item in items:
                    self.stdout.write(f"  - ID {item['id']} | order_no={item.get('order_no')} | fields={item.get('fields') or item.get('missing_fields') or item.get('invalid_fields')}")

        # Full JSON dump?
        if options.get("output"):
            path = options["output"]
            with open(path, "w") as f:
                json.dump(report, f, default=str, indent=2)
            self.stdout.write(self.style.SUCCESS(f"\nFull report written to {path}"))
