# Generated by Django 5.1.6 on 2025-03-28 14:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('welcome', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='description',
            name='welcome',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='descriptions', related_query_name='descriptions', to='welcome.welcome'),
        ),
    ]
