# Generated by Django 4.2.3 on 2023-08-18 03:13

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("leaf_engine", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="leaf",
            name="previous_analytics_run",
            field=models.DateTimeField(
                default=datetime.datetime(2023, 8, 18, 3, 13, 38, 660755)
            ),
        ),
    ]
