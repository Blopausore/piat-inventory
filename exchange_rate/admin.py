from django.contrib import admin

from exchange_rate.models import ExchangeRate


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('date', 'base_currency', 'price', 'open', 'high', 'low', 'change_percent')
