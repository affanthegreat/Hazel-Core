# Generated by Django 4.2.3 on 2023-08-26 17:36

import datetime
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                ("user_email", models.EmailField(max_length=254, unique=True)),
                ("user_name", models.CharField(max_length=60, unique=True)),
                ("user_password", models.CharField(max_length=250)),
                (
                    "user_id",
                    models.CharField(
                        blank=True,
                        default=uuid.uuid4,
                        max_length=100,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("user_public_leaf_count", models.BigIntegerField(default=0)),
                ("user_private_leaf_count", models.BigIntegerField(default=0)),
                ("user_experience_points", models.BigIntegerField(default=0)),
                ("user_verified", models.BooleanField(default=False)),
                ("user_followers", models.BigIntegerField(default=0)),
                ("user_following", models.BigIntegerField(default=0)),
                ("user_level", models.BigIntegerField(default=1)),
                ("user_universal_likes", models.BigIntegerField(default=0)),
                ("user_universal_dislikes", models.BigIntegerField(default=0)),
                ("user_universal_comments", models.BigIntegerField(default=0)),
                (
                    "previous_experience_generation_date",
                    models.DateTimeField(
                        default=datetime.datetime(2023, 8, 26, 17, 36, 38, 948749)
                    ),
                ),
                ("user_dp", models.ImageField(upload_to="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="UserDetails",
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
                ("user_bio", models.CharField(max_length=120)),
                ("user_country", models.CharField(max_length=100)),
                ("user_state", models.CharField(max_length=100)),
                ("user_region", models.CharField(max_length=100)),
                ("user_city", models.CharField(max_length=100)),
                ("user_gender", models.CharField(max_length=15)),
                ("user_age", models.PositiveIntegerField(default=1)),
                ("user_full_name", models.CharField(max_length=100)),
                ("user_phone_number", models.CharField(max_length=15, unique=True)),
                ("user_address", models.CharField(max_length=50)),
                ("user_phone_id", models.CharField(max_length=120, unique=True)),
                (
                    "user_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="detail",
                        to="user_engine.userprofile",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="UserAccessToken",
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
                ("user_session_id", models.CharField(max_length=100, unique=True)),
                (
                    "creation_date",
                    models.DateTimeField(
                        default=datetime.datetime(2023, 8, 26, 17, 36, 38, 949663)
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="holy",
                        to="user_engine.userprofile",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="UserFollowRequests",
            fields=[
                ("status", models.BooleanField(default=False)),
                (
                    "id",
                    models.CharField(
                        blank=True,
                        default=uuid.uuid4,
                        max_length=100,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "requested_to",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="requested_to",
                        to="user_engine.userprofile",
                    ),
                ),
                (
                    "requester",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="requester",
                        to="user_engine.userprofile",
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(
                        fields=["requester", "requested_to"],
                        name="user_engine_request_493a01_idx",
                    ),
                    models.Index(
                        fields=["requested_to", "requester"],
                        name="user_engine_request_a9f513_idx",
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="UserFollowing",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "master",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="master",
                        to="user_engine.userprofile",
                    ),
                ),
                (
                    "slave",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="slave",
                        to="user_engine.userprofile",
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(
                        fields=["slave", "master"],
                        name="user_engine_slave_i_a4c9ff_idx",
                    ),
                    models.Index(
                        fields=["master", "slave"],
                        name="user_engine_master__74129d_idx",
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="UserBlockedAccounts",
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
                (
                    "blocked_profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="beta",
                        to="user_engine.userprofile",
                    ),
                ),
                (
                    "blocker_profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sigma",
                        to="user_engine.userprofile",
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(
                        fields=["blocker_profile", "blocked_profile"],
                        name="user_engine_blocker_a6f24b_idx",
                    ),
                    models.Index(
                        fields=["blocked_profile", "blocker_profile"],
                        name="user_engine_blocked_559c45_idx",
                    ),
                ],
            },
        ),
    ]
