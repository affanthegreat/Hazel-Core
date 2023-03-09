import datetime
from django.db import models
from django.utils.translation import gettext as _

from user_engine.models import UserProfile


class LeafType(models.TextChoices):
    Public = "public", "public"
    Private = "private", "private"


class Leaf(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        UserProfile, related_name="creator", on_delete=models.DO_NOTHING
    )
    text_content = models.CharField(max_length=400, null=False)
    leaf_id = models.CharField(max_length=100, primary_key=True)
    image_content = models.ImageField()
    likes_count = models.BigIntegerField(default=0)
    dilikes_count = models.BigIntegerField(default=0)
    comments_count = models.BigIntegerField(default=0)
    view_count = models.BigIntegerField(default=0)
    leaf_type = models.CharField(choices=LeafType.choices, max_length=30)
    engagement_rating = models.DecimalField(default=0,decimal_places=2, max_digits=125)
    experience_rating = models.DecimalField(default=0, decimal_places=2, max_digits=125)
    previous_analytics_run = models.DateTimeField(default=datetime.datetime.now())


class LeafLikes(models.Model):
    leaf = models.ForeignKey(
        Leaf, related_name="creator_comment_leaf", on_delete=models.CASCADE
    )
    liked_by = models.ForeignKey(
        UserProfile, related_name="liked_user", on_delete=models.DO_NOTHING
    )


class LeafDisLikes(models.Model):
    leaf = models.ForeignKey(
        Leaf, related_name="content_leaf", on_delete=models.CASCADE
    )
    disliked_by = models.ForeignKey(
        UserProfile, related_name="disliked_user", on_delete=models.DO_NOTHING
    )


class LeafComments(models.Model):
    leaf = models.ForeignKey(
        Leaf, related_name="creator_leaf", on_delete=models.CASCADE
    )
    commented_by = models.ForeignKey(
        UserProfile, related_name="commented_user", on_delete=models.DO_NOTHING
    )
    comment = models.CharField(max_length=100, null=False)
