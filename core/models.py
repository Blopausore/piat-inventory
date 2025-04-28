from django.db import models


class Client(models.Model):
    name = models.CharField(max_length=255)

class Supplier(models.Model):
    name = models.CharField(max_length=255)


class ClientOrder(models.Model):
    client:Client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField()

    # Détails spécifiques à la commande client
    shipping_method = models.CharField(max_length=20)
    payment_status = models.CharField(max_length=20)

    def __str__(self):
        return f"Client Order {self.id} - {self.client.name}"


class SupplierOrder(models.Model):
    supplier:Supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_address = models.TextField()

    # Détails spécifiques à l'achat fournisseur
    delivery_date = models.DateField()
    payment_terms = models.CharField(max_length=50)

    def __str__(self):
        return f"Supplier Order {self.id} - {self.supplier.name}"


class Gemstone(models.Model):
    type = models.CharField(max_length=255)
    weight = models.FloatField(verbose_name="weight per piece (ct)")
    color = models.CharField(max_length=255, null=True)
    number = models.IntegerField()
    
    client_order = models.ForeignKey("ClientOrder", null=True, blank=True, on_delete=models.CASCADE)
    supplier_order = models.ForeignKey(SupplierOrder, null=True, blank=True, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Gemstone {self.color} {self.type} x{self.number} of {self.weight} carats"
    # Shape, cutting, size, ... 
    
