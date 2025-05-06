from django.db import models
from django.core.serializers.json import DjangoJSONEncoder

UNIQUE_SUPPLIER_LOT =('source_file', 'sheet_name', 'row_index')

class OrderRaw(models.Model):
    """
    Raw data just as the file imported.
    """
    class Meta:
        unique_together = UNIQUE_SUPPLIER_LOT
        constraints = [
            models.UniqueConstraint(
                fields=list(UNIQUE_SUPPLIER_LOT),
                name='unique_raw_order_lot'
            )
        ]
        
    source_file = models.CharField(max_length=255)
    sheet_name  = models.CharField(max_length=255, blank=True, null=True)
    row_index   = models.IntegerField(blank=True, null=True)
    data        = models.JSONField(
                    help_text="Raw data from Excel line",
                    encoder=DjangoJSONEncoder)

class SupplierOrderRaw(models.Model):
    class Meta:
        unique_together = UNIQUE_SUPPLIER_LOT
        constraints = [
            models.UniqueConstraint(
                fields=list(UNIQUE_SUPPLIER_LOT),
                name='unique_supplier_raw_order_lot'
            )
        ]
        verbose_name = "Raw Supplier Order"
        verbose_name_plural = "Raw Supplier Orders"
        
    source_file = models.CharField(max_length=255)
    sheet_name  = models.CharField(max_length=255, blank=True, null=True)
    row_index   = models.IntegerField(blank=True, null=True)
    data        = models.JSONField(
                    help_text="Raw data from Excel line",
                    encoder=DjangoJSONEncoder)

    def __str__(self):
        return f"RawSupplier #{self.id} – row {self.row_index}"


class ClientOrderRaw(models.Model):
    class Meta:
        unique_together = UNIQUE_SUPPLIER_LOT
        constraints = [
            models.UniqueConstraint(
                fields=list(UNIQUE_SUPPLIER_LOT),
                name='unique_client_raw_order_lot'
            )
        ]
        verbose_name = "Raw Client Order"
        verbose_name_plural = "Raw Client Orders"

    source_file = models.CharField(max_length=255)
    sheet_name  = models.CharField(max_length=255, blank=True, null=True)
    row_index   = models.IntegerField(blank=True, null=True)
    data        = models.JSONField(
                    help_text="Raw data from Excel line",
                    encoder=DjangoJSONEncoder)


       
    def __str__(self):
        return f"RawClient #{self.id} – row {self.row_index}"

