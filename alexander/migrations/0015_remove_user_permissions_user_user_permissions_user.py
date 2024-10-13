# Generated by Django 5.0.4 on 2024-07-07 15:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alexander', '0014_alter_user_type_delete_user_types'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user_permissions',
            name='User',
        ),
        migrations.AddField(
            model_name='user_permissions',
            name='User',
            field=models.ForeignKey(default=4, on_delete=django.db.models.deletion.CASCADE, to='alexander.user'),
            preserve_default=False,
        ),
    ]
