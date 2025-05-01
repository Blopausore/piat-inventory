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


class SupplierOrder(models.Model):
    """An order made to a supplier.
    
    ::note:
        - THB rate at 'date'
    """
    class Meta:
        unique_together = (
            'supplier','order_no','number',
            'stone','shape','color',
            'cutting','size','carats',
        )
        constraints = [
            models.UniqueConstraint(
                fields=['supplier','order_no','number','stone','shape','color','cutting','size','carats'],
                name='unique_supplier_lot'
            )
        ]
    # class Meta:
    #     unique_together = ('supplier', 'order_no', 'number', 'stone', 'shape', 'color', 'cutting', 'size', 'carats')

    client_memo = models.CharField(max_length=10, default="P", verbose_name="Purchase (P), Memo (M), Bargain (B)") # Purchase (P), Memo (M), Bargain (B) 
    date = models.DateTimeField()
    book_no = models.IntegerField()
    order_no = models.IntegerField()
    tax_invoice = models.CharField(max_length=50, blank=True, null=True)
    # supplier:Supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    supplier = models.CharField(max_length=50)
    
    # Stones 
    number = models.IntegerField()
    stone = models.CharField(max_length=50)
    heating = models.CharField(max_length=20, blank=True, null=True)  # H/NH
    color = models.CharField(max_length=50, blank=True, null=True)
    shape = models.CharField(max_length=50, blank=True, null=True)
    cutting = models.CharField(max_length=50, blank=True, null=True)
    size = models.CharField(max_length=50, blank=True, null=True)  # To be careful (Ex : 6x4, 2.3-2.4, 2.50)
    carats = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Weight in carats")
    
    # Prices 
    currency = models.CharField(max_length=5, default="THB")  # US/THB
    price_cur_per_unit = models.DecimalField(max_digits=15, decimal_places=2)
    unit = models.CharField(max_length=5, default="CT")
    
    total_thb = models.DecimalField(max_digits=15, decimal_places=2)
    
    weight_per_piece = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    
    price_usd_per_ct = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price_usd_per_piece = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_usd = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    rate_avg_2019 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    credit_term = models.CharField(max_length=50, blank=True, null=True)
    target_size = models.CharField(max_length=50, blank=True, null=True)
        
    def __str__(self):
        return f"Supplier Order {self.order_no} - {self.supplier} - {self.date}"

    def clean(self):
        # Appelle d’abord les validations de champ standard
        super().clean()

        # Vérifie la contrainte “unique” métier
        qs = SupplierOrder.objects.filter(
            supplier=self.supplier,
            order_no=self.order_no,
            number=self.number,
            stone=self.stone,
            shape=self.shape,
            color=self.color,
            cutting=self.cutting,
            size=self.size,
            carats=self.carats
        )
        # Si l’objet existe déjà (et n’est pas lui-même), c’est un doublon
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError({
                '__all__': 'A supplier order with this combination of fields already exists.'
            })

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
    
