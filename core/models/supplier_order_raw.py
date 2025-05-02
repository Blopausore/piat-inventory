# core/models/supplier_order_raw.py

from django.db import models

class SupplierOrderRaw(models.Model):
    """
    Raw data just as the file imported.
    """
    imported_at = models.DateTimeField(auto_now_add=True)
    source_file = models.CharField(max_length=255)
    sheet_name  = models.CharField(max_length=255, blank=True, null=True)
    row_index   = models.IntegerField(blank=True, null=True)
    data        = models.JSONField(help_text="Raw data from Excel line")
    success     = models.BooleanField(default=False)
    error       = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Raw Supplier Order"
        verbose_name_plural = "Raw Supplier Orders"
        indexes = [models.Index(fields=['imported_at'])]

    def __str__(self):
        return f"RawSupplier #{self.id} – row {self.row_index}"

