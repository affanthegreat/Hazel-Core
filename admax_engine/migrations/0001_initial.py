# Generated by Django 4.2.3 on 2023-08-26 17:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("leaf_engine", "0003_alter_leaf_previous_analytics_run"),
        ("user_engine", "0004_alter_useraccesstoken_creation_date_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="AdvertisementCampaigns",
            fields=[
                (
                    "campaign_id",
                    models.CharField(max_length=100, primary_key=True, serialize=False),
                ),
                ("campaign_name", models.CharField(max_length=50)),
                ("total_ads", models.PositiveIntegerField(default=0)),
                ("active_ads", models.PositiveBigIntegerField(default=0)),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="campaign_creator",
                        to="user_engine.userprofile",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PromotedLeafs",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                ("expiry", models.DateTimeField()),
                (
                    "boost_multiplier",
                    models.DecimalField(decimal_places=5, default=1, max_digits=5),
                ),
                ("is_active", models.BooleanField(default=False)),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="promoted_by",
                        to="user_engine.userprofile",
                    ),
                ),
                (
                    "leaf",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="promoted_leaf",
                        to="leaf_engine.leaf",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Advertisements",
            fields=[
                ("created_date", models.DateTimeField(auto_now_add=True)),
                ("target_topic_id", models.BigIntegerField(default=-1)),
                ("target_topic_category", models.IntegerField(max_length=3)),
                ("advertisement_tier", models.IntegerField(default=1)),
                ("is_active", models.BooleanField(default=False)),
                (
                    "advertisement_id",
                    models.CharField(max_length=100, primary_key=True, serialize=False),
                ),
                (
                    "campaign",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="campaign_given_name",
                        to="admax_engine.advertisementcampaigns",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ad_created_by",
                        to="user_engine.userprofile",
                    ),
                ),
                (
                    "leaf",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="advertisement",
                        to="leaf_engine.leaf",
                    ),
                ),
            ],
        ),
    ]
