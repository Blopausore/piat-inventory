from django.db import models
from django.core.exceptions import ValidationError

from core.common.models import Client

class ClientOrder(models.Model):
    """An Order made by a client.

    ::note:
        The 'total_price_thb' is at the change rate of 'date' 
    """
    order_no = models.IntegerField()
    client:Client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date = models.DateTimeField()
    total_price_usd = models.DecimalField(max_digits=10, decimal_places=2)
    # "At the rate when the command was made"
    total_price_thb = models.DecimalField(max_digits=10, decimal_places=2)
    
    total_weight = models.DecimalField(max_digits=4, decimal_places=2)
    
    def __str__(self):
        return f"Client Order {self.id} - {self.client.name}"
