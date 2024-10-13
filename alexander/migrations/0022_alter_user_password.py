# Generated by Django 5.0.4 on 2024-07-10 11:55

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alexander', '0021_userloginrecord'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='Password',
            field=models.CharField(max_length=15, validators=[django.core.validators.RegexValidator(message='Password must be at least 8 characters long and include at least one digit.', regex='^[a-zA-Z\\d]{8,}$')]),
        ),
    ]
