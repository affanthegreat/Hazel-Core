# Generated by Django 4.2.3 on 2023-08-24 19:45

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
                default=datetime.datetime(2023, 8, 24, 19, 45, 41, 925626)
            ),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="previous_experience_generation_date",
            field=models.DateTimeField(
                default=datetime.datetime(2023, 8, 24, 19, 45, 41, 924741)
            ),
        ),
    ]
