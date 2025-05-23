# Generated by Django 5.2 on 2025-05-02 09:21

import django.core.serializers.json
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='ClientOrderRaw',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source_file', models.CharField(max_length=255)),
                ('sheet_name', models.CharField(blank=True, max_length=255, null=True)),
                ('row_index', models.IntegerField(blank=True, null=True)),
                ('success', models.BooleanField(default=False)),
                ('error', models.TextField(blank=True, null=True)),
                ('data', models.JSONField(encoder=django.core.serializers.json.DjangoJSONEncoder, help_text='Raw data from Excel line')),
            ],
            options={
                'verbose_name': 'Raw Client Order',
                'verbose_name_plural': 'Raw Client Orders',
            },
        ),
        migrations.CreateModel(
            name='OrderRaw',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source_file', models.CharField(max_length=255)),
                ('sheet_name', models.CharField(blank=True, max_length=255, null=True)),
                ('row_index', models.IntegerField(blank=True, null=True)),
                ('success', models.BooleanField(default=False)),
                ('error', models.TextField(blank=True, null=True)),
                ('data', models.JSONField(encoder=django.core.serializers.json.DjangoJSONEncoder, help_text='Raw data from Excel line')),
            ],
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='SupplierOrderRaw',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source_file', models.CharField(max_length=255)),
                ('sheet_name', models.CharField(blank=True, max_length=255, null=True)),
                ('row_index', models.IntegerField(blank=True, null=True)),
                ('success', models.BooleanField(default=False)),
                ('error', models.TextField(blank=True, null=True)),
                ('data', models.JSONField(encoder=django.core.serializers.json.DjangoJSONEncoder, help_text='Raw data from Excel line')),
            ],
            options={
                'verbose_name': 'Raw Supplier Order',
                'verbose_name_plural': 'Raw Supplier Orders',
            },
        ),
        migrations.CreateModel(
            name='ClientOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_no', models.IntegerField()),
                ('date', models.DateTimeField()),
                ('total_price_usd', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_price_thb', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_weight', models.DecimalField(decimal_places=2, max_digits=4)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.client')),
            ],
        ),
        migrations.CreateModel(
            name='SupplierOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('book_no', models.IntegerField()),
                ('order_no', models.IntegerField()),
                ('tax_invoice', models.CharField(blank=True, max_length=50, null=True)),
                ('supplier', models.CharField(max_length=50)),
                ('number', models.IntegerField()),
                ('stone', models.CharField(max_length=50)),
                ('heating', models.CharField(blank=True, max_length=20, null=True)),
                ('color', models.CharField(blank=True, max_length=50, null=True)),
                ('shape', models.CharField(blank=True, max_length=50, null=True)),
                ('cutting', models.CharField(blank=True, max_length=50, null=True)),
                ('size', models.CharField(blank=True, max_length=50, null=True)),
                ('carats', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('weight_per_piece', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('price_usd_per_piece', models.DecimalField(decimal_places=2, max_digits=10)),
                ('price_usd_per_ct', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('total_usd', models.DecimalField(decimal_places=2, max_digits=15)),
                ('raw', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='interpreted', to='core.supplierorderraw')),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('date', 'supplier', 'order_no', 'number', 'stone', 'shape', 'color', 'size', 'carats', 'weight_per_piece', 'price_usd_per_ct'), name='unique_supplier_lot')],
                'unique_together': {('date', 'supplier', 'order_no', 'number', 'stone', 'shape', 'color', 'size', 'carats', 'weight_per_piece', 'price_usd_per_ct')},
            },
        ),
    ]
