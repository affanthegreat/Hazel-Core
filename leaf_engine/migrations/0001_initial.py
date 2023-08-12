# Generated by Django 4.2.3 on 2023-08-12 13:20

import datetime
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("user_engine", "0002_alter_useraccesstoken_creation_date_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Leaf",
            fields=[
                ("created_date", models.DateTimeField(auto_now_add=True)),
                ("text_content", models.CharField(max_length=400)),
                (
                    "leaf_id",
                    models.CharField(max_length=100, primary_key=True, serialize=False),
                ),
                ("image_content", models.ImageField(upload_to="")),
                ("likes_count", models.BigIntegerField(default=0)),
                ("dislikes_count", models.BigIntegerField(default=0)),
                ("comments_count", models.BigIntegerField(default=0)),
                ("view_count", models.BigIntegerField(default=0)),
                (
                    "leaf_type",
                    models.CharField(
                        choices=[("public", "public"), ("private", "private")],
                        max_length=30,
                    ),
                ),
                (
                    "engagement_rating",
                    models.DecimalField(decimal_places=2, default=0, max_digits=125),
                ),
                (
                    "experience_rating",
                    models.DecimalField(decimal_places=2, default=0, max_digits=125),
                ),
                ("exp_points", models.BigIntegerField(default=0, max_length=25)),
                (
                    "previous_analytics_run",
                    models.DateTimeField(
                        default=datetime.datetime(2023, 8, 12, 13, 20, 4, 24300)
                    ),
                ),
                ("leaf_topic_id", models.BigIntegerField(default=-1)),
                ("leaf_topic_category_id", models.IntegerField(max_length=3)),
                (
                    "leaf_sentiment",
                    models.DecimalField(decimal_places=6, default=-69, max_digits=6),
                ),
                ("leaf_emotion_state", models.CharField(default="NULL", max_length=30)),
                ("is_promoted", models.BooleanField(default=False)),
                ("is_advertisement", models.BooleanField(default=False)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="creator",
                        to="user_engine.userprofile",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="LeafViewedBy",
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
                ("view_date", models.DateTimeField(auto_now_add=True)),
                (
                    "leaf",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="viewed_leaf",
                        to="leaf_engine.leaf",
                    ),
                ),
                (
                    "viewed_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="viewer",
                        to="user_engine.userprofile",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="LeafLikes",
            fields=[
                (
                    "like_id",
                    models.CharField(
                        blank=True,
                        default=uuid.uuid4,
                        max_length=100,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                (
                    "leaf",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="creator_comment_leaf",
                        to="leaf_engine.leaf",
                    ),
                ),
                (
                    "liked_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="liked_user",
                        to="user_engine.userprofile",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="LeafDisLikes",
            fields=[
                (
                    "dislike_id",
                    models.CharField(
                        blank=True,
                        default=uuid.uuid4,
                        max_length=100,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                (
                    "disliked_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="disliked_user",
                        to="user_engine.userprofile",
                    ),
                ),
                (
                    "leaf",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="content_leaf",
                        to="leaf_engine.leaf",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="LeafComments",
            fields=[
                (
                    "comment_id",
                    models.CharField(
                        blank=True,
                        default=uuid.uuid4,
                        max_length=100,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("comment", models.CharField(max_length=100)),
                ("comment_depth", models.IntegerField(default=1)),
                (
                    "comment_sentiment",
                    models.DecimalField(decimal_places=6, default=-69, max_digits=6),
                ),
                ("comment_emotion", models.CharField(default="NULL", max_length=40)),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                (
                    "commented_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="commented_user",
                        to="user_engine.userprofile",
                    ),
                ),
                (
                    "leaf",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="creator_leaf",
                        to="leaf_engine.leaf",
                    ),
                ),
                (
                    "parent_comment",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="replies",
                        to="leaf_engine.leafcomments",
                    ),
                ),
                (
                    "root_comment",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="main_comment",
                        to="leaf_engine.leafcomments",
                    ),
                ),
            ],
        ),
    ]
