# Generated by Django 5.0.4 on 2024-06-13 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alexander', '0005_alter_products_in_cashier_orders_comments'),
    ]

    operations = [
        migrations.AddField(
            model_name='cashier_orders',
            name='Status',
            field=models.CharField(choices=[('open', 'open'), ('close', 'close')], default='open', max_length=5),
        ),
    ]
