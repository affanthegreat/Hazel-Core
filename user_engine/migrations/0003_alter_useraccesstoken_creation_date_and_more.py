# Generated by Django 4.2.3 on 2023-08-19 17:40

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user_engine", "0002_alter_useraccesstoken_creation_date_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="useraccesstoken",
            name="creation_date",
            field=models.DateTimeField(
                default=datetime.datetime(2023, 8, 19, 17, 40, 42, 859696)
            ),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="previous_experience_generation_date",
            field=models.DateTimeField(
                default=datetime.datetime(2023, 8, 19, 17, 40, 42, 859052)
            ),
        ),
    ]
