# Generated by Django 5.0.4 on 2024-07-02 11:30

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alexander', '0012_admin_highlights_type'),
    ]

    # operations = [
    #     migrations.AddField(
    #         model_name='employee',
    #         name='id',
    #         field=models.BigAutoField(auto_created=True, primary_key=True, default=1 , serialize=False, verbose_name='ID'),
    #         preserve_default=False,
    #     ),
    #     migrations.AlterField(
    #         model_name='employee',
    #         name='Employee_ID',
    #         field=models.CharField(help_text='Enter a 9-digit employee ID.', max_length=9, unique=True, validators=[django.core.validators.RegexValidator(message='ID must be exactly 9 digits.', regex='^\\d{9}$')]),
    #     ),
    # ]
