from decimal import Decimal
from django.db import models

ONE = Decimal('1')

class ExchangeRate(models.Model):
    
    class Meta:
        unique_together = ('base_currency', 'date')
        constraints = [
            models.UniqueConstraint(
                fields=['base_currency', 'date'],
                name='unique_rate_exchange'
            )
        ]
    base_currency = models.CharField(max_length=3) #USD, EUR, THB, ...
    date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=4)   # 1 USD = price base_currency
    open = models.DecimalField(max_digits=10, decimal_places=4)
    high = models.DecimalField(max_digits=10, decimal_places=4)
    low = models.DecimalField(max_digits=10, decimal_places=4)
    change_percent = models.CharField(max_length=10, blank=True, null=True)  

    @property
    def inverse_price(self):
        return ONE / self.price

    def __str__(self):
        return f"{self.date} | 1 USD = {self.price} {self.base_currency}"
