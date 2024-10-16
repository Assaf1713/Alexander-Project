# Generated by Django 5.0.4 on 2024-07-07 18:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alexander', '0020_remove_user_permissions_user_user_permissions_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserLoginRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('login_time', models.DateTimeField(auto_now_add=True)),
                ('logout_time', models.DateTimeField(blank=True, null=True)),
                ('session_duration', models.DurationField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='alexander.user')),
            ],
        ),
    ]
