from django.db import models
from django.contrib.postgres.fields import ArrayField

from leaf_engine.models import Leaf
from user_engine.models import UserProfile


class Advertisements(models.Model):
    leaf = models.ForeignKey(Leaf, related_name='advertisement', on_delete=models.CASCADE)
    created_by = models.ForeignKey(UserProfile, related_name='ad_created_by', on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    target_topic_id = ArrayField(models.BigIntegerField(default= -1))
    target_topic_category = models.IntegerField(max_length=3)
    advertisement_tier = models.IntegerField(default=1)
    is_active = models.BooleanField(default=False )


class PromotedLeafs(models.Model):
    leaf = models.ForeignKey(Leaf, related_name='promoted_leaf', on_delete=models.CASCADE)
    created_by = models.ForeignKey(UserProfile, related_name='promoted_by', on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    expiry = models.DateTimeField()
    boost_multiplier = models.DecimalField(default=1,max_digits=5,decimal_places=5)
    is_active = models.BooleanField(default=False)