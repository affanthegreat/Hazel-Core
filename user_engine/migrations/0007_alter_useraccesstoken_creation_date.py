# Generated by Django 4.0.8 on 2023-03-08 08:22

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_engine', '0006_userprofile_user_universal_comments_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraccesstoken',
            name='creation_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 3, 8, 8, 22, 14, 323045)),
        ),
    ]
