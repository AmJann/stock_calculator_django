# Generated by Django 4.2.1 on 2023-05-26 03:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0007_stock_allocation'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='list_id',
            field=models.CharField(default=1234567812345678, max_length=16),
            preserve_default=False,
        ),
    ]
