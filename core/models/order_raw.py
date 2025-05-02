# core/models/order_raw.py

from django.db import models
from django.core.serializers.json import DjangoJSONEncoder

class OrderRaw(models.Model):
    """
    Raw data just as the file imported.
    """
    source_file = models.CharField(max_length=255)
    sheet_name  = models.CharField(max_length=255, blank=True, null=True)
    row_index   = models.IntegerField(blank=True, null=True)
    data        = models.JSONField(
        help_text="Raw data from Excel line",
        encoder=DjangoJSONEncoder)

class SupplierOrderRaw(models.Model):
    class Meta:
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

