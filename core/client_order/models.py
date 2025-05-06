from django.db import models
from django.core.exceptions import ValidationError

from core.common.models import Client

from django.db import models
from django.core.exceptions import ValidationError


UNIQUE_SUPPLIER_LOT = (
    'date','supplier','order_no','number',
    'stone','shape','color','size','carats',
    'weight_per_piece','price_usd_per_ct',
)

class ClientOrder(models.Model):
    """
    Supplier order, it is a purchase.
    """
    class Meta:
        unique_together = UNIQUE_SUPPLIER_LOT
        constraints = [
            models.UniqueConstraint(
                fields=list(UNIQUE_SUPPLIER_LOT),
                name='unique_supplier_lot'
            )
        ]
        
    raw = models.OneToOneField(
        'SupplierOrderRaw',
        on_delete=models.PROTECT,
        related_name='interpreted',
        blank=True,
        null=True
    )

    # Info
    date                = models.DateTimeField()
    book_no             = models.IntegerField(blank=True, null=True)
    order_no            = models.IntegerField(blank=True, null=True)
    client              = models.CharField(max_length=50)
    
    # Stone 
    number              = models.IntegerField(blank=True, null=True)
    stone               = models.CharField(max_length=50, blank=True, null=True) # to parse
    heating             = models.CharField(max_length=20, blank=True, null=True) 
    color               = models.CharField(max_length=50, blank=True, null=True) # to parse
    shape               = models.CharField(max_length=50, blank=True, null=True) # to parse
    cutting             = models.CharField(max_length=50, blank=True, null=True) # to parse
    size                = models.CharField(max_length=50, blank=True, null=True) # to parse
    carats              = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    weight_per_piece    = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)

    # Price
    price_usd_per_piece = models.DecimalField(max_digits=13, decimal_places=3, blank=True, null=True)
    price_usd_per_ct    = models.DecimalField(max_digits=13, decimal_places=3, blank=True, null=True)
    total_usd           = models.DecimalField(max_digits=13, decimal_places=3, blank=True, null=True)
    
    def __str__(self):
        return f"Client order : {self.order_no} – {self.client} – {self.date.date()} for {self.number} {self.stone} {self.color} {self.shape} {self.carats}"
    
    def clean(self):
        super().clean()
        
        filters = {f: getattr(self, f) for f in UNIQUE_SUPPLIER_LOT}
        qs = ClientOrder.objects.filter(**filters)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError({
                '__all__': 'A supplier order with this combination of fields already exists.'
            })


