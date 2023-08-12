# Generated by Django 4.2.3 on 2023-08-12 06:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("leaf_engine", "0002_alter_leaf_previous_analytics_run"),
        ("user_engine", "0003_alter_useraccesstoken_creation_date_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserTopicRelations",
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
                ("topic_id", models.BigIntegerField(default=-1)),
                ("topic_category_id", models.BigIntegerField(default=-1)),
                ("likes", models.BigIntegerField(default=0)),
                ("dislikes", models.BigIntegerField(default=0)),
                ("comments", models.BigIntegerField(default=0)),
                ("sub_comments", models.BigIntegerField(default=0)),
                ("leaves_served_by_engine", models.BigIntegerField(default=0)),
                ("times_interacted", models.BigIntegerField(default=0)),
                ("positive_comments_made", models.BigIntegerField(default=0)),
                ("negative_comments_made", models.BigIntegerField(default=0)),
                ("favoritism_weight", models.BigIntegerField(default=0)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="topic_relation_user",
                        to="user_engine.userprofile",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="AdvertisementRelation",
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
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="ad_creator",
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
        migrations.CreateModel(
            name="UserLeafPreferences",
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
                ("topic_id", models.BigIntegerField(default=-1)),
                ("topic_category_id", models.BigIntegerField(default=-1)),
                ("topic_visit_frequency", models.BigIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user_object",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="user_obj",
                        to="user_engine.userprofile",
                    ),
                ),
            ],
            options={
                "unique_together": {("topic_id", "topic_category_id", "user_object")},
            },
        ),
        migrations.CreateModel(
            name="LeafInteraction",
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
                    "interaction_type",
                    models.CharField(
                        choices=[
                            ("like", "like"),
                            ("dislike", "dislike"),
                            ("comment", "comment"),
                            ("view", "view"),
                            ("sub_comment", "sub_comment"),
                        ],
                        max_length=15,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "interacted_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="related_user",
                        to="user_engine.userprofile",
                    ),
                ),
                (
                    "leaf",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="interacted_leaf",
                        to="leaf_engine.leaf",
                    ),
                ),
            ],
            options={
                "unique_together": {("leaf", "interacted_by", "interaction_type")},
            },
        ),
    ]
