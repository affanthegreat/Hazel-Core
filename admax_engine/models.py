from django.db import models
from django.contrib.postgres.fields import ArrayField

from leaf_engine.models import Leaf
from user_engine.models import UserProfile


class AdvertisementCampaigns(models.Model):
    campaign_id = models.CharField(max_length=100,primary_key=True)
    campaign_name = models.CharField(max_length=50)
    total_ads = models.PositiveIntegerField(default=0)
    active_ads = models.PositiveBigIntegerField(default=0)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(UserProfile, related_name='campaign_creator', on_delete=models.CASCADE)

class Advertisements(models.Model):
    leaf = models.ForeignKey(Leaf, related_name='advertisement', on_delete=models.CASCADE)
    created_by = models.ForeignKey(UserProfile, related_name='ad_created_by', on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
   # target_topic_id = ArrayField(models.BigIntegerField(default= -1))
    target_topic_category = models.IntegerField(max_length=3)
    advertisement_tier = models.IntegerField(default=1)
    campaign = models.ForeignKey(AdvertisementCampaigns,related_name='campaign_given_name', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False,  )
    advertisement_id = models.CharField(max_length=100,primary_key=True)


class PromotedLeafs(models.Model):
    leaf = models.ForeignKey(Leaf, related_name='promoted_leaf', on_delete=models.CASCADE)
    created_by = models.ForeignKey(UserProfile, related_name='promoted_by', on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    expiry = models.DateTimeField()
    boost_multiplier = models.DecimalField(default=1,max_digits=5,decimal_places=5)
    is_active = models.BooleanField(default=False)

