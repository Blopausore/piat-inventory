# core/models/supplier_order.py
from django.db import models
from django.core.exceptions import ValidationError


UNIQUE_SUPPLIER_LOT = (
    'date','supplier','order_no','number',
    'stone','shape','color','size','carats',
    'weight_per_piece','price_usd_per_ct',
)

class SupplierOrder(models.Model):
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
    )

    # Info
    date         = models.DateTimeField()
    book_no      = models.IntegerField()
    order_no     = models.IntegerField()
    tax_invoice  = models.CharField(max_length=50, blank=True, null=True)
    supplier     = models.CharField(max_length=50)

    # Stone
    number            = models.IntegerField()
    stone             = models.CharField(max_length=50) # to parse
    heating           = models.CharField(max_length=20, blank=True, null=True)
    color             = models.CharField(max_length=50, blank=True, null=True) # to parse
    shape             = models.CharField(max_length=50, blank=True, null=True) # to parse
    cutting           = models.CharField(max_length=50, blank=True, null=True) # to parse
    size              = models.CharField(max_length=50, blank=True, null=True) # to parse
    carats            = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    weight_per_piece  = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)

    # Price
    price_usd_per_piece = models.DecimalField(max_digits=10, decimal_places=2)
    price_usd_per_ct    = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_usd           = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"SupplierOrder {self.order_no} – {self.supplier} – {self.date.date()}"

    def clean(self):
        super().clean()
        
        filters = {f: getattr(self, f) for f in UNIQUE_SUPPLIER_LOT}
        qs = SupplierOrder.objects.filter(**filters)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError({
                '__all__': 'A supplier order with this combination of fields already exists.'
            })


