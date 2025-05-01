from django.db import models
from django.core.exceptions import ValidationError

class Client(models.Model):
    name = models.CharField(max_length=255)

class Supplier(models.Model):
    name = models.CharField(max_length=255)

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



# LATER 

# class Gemstone(models.Model):
#     type = models.CharField(max_length=255)
#     weight = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="weight per piece (ct)")

#     color = models.CharField(max_length=255, null=True)
#     number = models.IntegerField()
    
#     client_order = models.ForeignKey(ClientOrder, null=True, blank=True, on_delete=models.CASCADE)
#     supplier_order = models.ForeignKey(SupplierOrder, null=True, blank=True, on_delete=models.CASCADE)
    
#     def __str__(self):
#         return f"Gemstone {self.color} {self.type} x{self.number} of {self.weight} carats"
#     # Shape, cutting, size, ... 
    
