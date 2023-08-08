from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from user_engine.models import UserProfile
from leaf_engine.models import Leaf

class InteractionType(models.TextChoices):
    Like = "like", "like"
    Dislike = "dislike", "dislike"
    Comment = "comment", "comment"
    View = "view", "view"
    SubComment = "sub_comment", "sub_comment"

class LeafInteraction(models.Model):
    leaf = models.ForeignKey(Leaf,  related_name="interacted_leaf", on_delete=models.DO_NOTHING)
    interacted_by = models.ForeignKey(UserProfile, related_name="related_user", on_delete=models.DO_NOTHING)
    interaction_type = models.CharField(choices=InteractionType.choices, max_length=15)
    class Meta:
        unique_together = ["leaf", "interacted_by", "interaction_type"]
class UserLeafPreferences(models.Model):
    topic_id = models.BigIntegerField(default= -1)
    topic_category_id = models.BigIntegerField(default=-1)
    topic_visit_frequency = models.BigIntegerField(default=0)
    user_object = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING,related_name='user_obj')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ["topic_id", "topic_category_id", "user_object"]

