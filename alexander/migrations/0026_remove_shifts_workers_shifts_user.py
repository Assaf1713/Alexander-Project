# Generated by Django 5.0.4 on 2024-07-18 18:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alexander', '0025_alter_shift_types_shift_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shifts',
            name='Workers',
        ),
        migrations.AddField(
            model_name='shifts',
            name='User',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='my_shifts', to='alexander.user'),
        ),
    ]
