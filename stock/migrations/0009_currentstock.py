# Generated by Django 4.2.1 on 2023-05-27 04:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0008_stock_list_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='currentStock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('close', models.FloatField()),
            ],
        ),
    ]
