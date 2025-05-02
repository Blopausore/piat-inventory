from django.db import models
from django.core.exceptions import ValidationError

from .choices import Currency

UNIQUE_SUPPLIER_LOT = (
    'date','supplier','order_no','number',
    'stone','shape','color','size','carats',
    'weight_per_piece','price_usd_per_ct',
)


class SupplierOrderRaw(models.Model):
    """
    Raw just has been imported from Excel
    """
    imported_at = models.DateTimeField(auto_now_add=True)
    source_file = models.CharField(max_length=255)
    row_data    = models.JSONField()   # tous les champs bruts dans un JSON
    success     = models.BooleanField(default=False)
    error       = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Raw #{self.id} from {self.source_file}"


class SupplierOrder(models.Model):
    """An order made to a supplier.
    
    ::note:
        - THB rate at 'date'
    """
    class Meta:
        unique_together = UNIQUE_SUPPLIER_LOT
        constraints = [
            models.UniqueConstraint(
                fields=list(UNIQUE_SUPPLIER_LOT),
                name='unique_supplier_lot'
            )
        ]


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
    size = models.CharField(max_length=50, blank=True, null=True)  # To be careful (Ex : 6x4, 2.3-2.4, 2.50)
    carats = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Weight in carats")
    
    # Prices 
    # RAW
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.THB,
    )
    price_cur_per_unit = models.DecimalField(max_digits=15, decimal_places=2)
    unit = models.CharField(max_length=5, default="CT")
    
    total_thb = models.DecimalField(max_digits=15, decimal_places=2)
    
    # CT, PC & $$ 
    weight_per_piece = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    
    price_usd_per_piece = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_usd = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    # if possible
    price_usd_per_ct = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Additional informations
    rate_avg_2019 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    credit_term = models.CharField(max_length=50, blank=True, null=True)
    target_size = models.CharField(max_length=50, blank=True, null=True)
        
    def __str__(self):
        return f"Supplier Order {self.order_no} - {self.supplier} - {self.date}"

    def clean(self):
        self.full_clean()
        super().clean()

        filters = {
            field: getattr(self, field) 
            for field in self._meta.unique_together
        }
        qs = SupplierOrder.objects.filter(**filters)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError({
                '__all__': 'A supplier order with this combination of fields already exists.'
            })

