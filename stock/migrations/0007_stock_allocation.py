# Generated by Django 4.2.1 on 2023-05-24 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0006_stock_list_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='allocation',
            field=models.FloatField(default=0.2),
            preserve_default=False,
        ),
    ]
