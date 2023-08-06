from django.db import models
import datetime
import uuid


class UserProfile(models.Model):
    user_email = models.EmailField(unique=True)
    user_name = models.CharField(max_length=60, unique=True)
    user_password = models.CharField(max_length=250)
    user_id = models.CharField(max_length=100, blank=True, unique=True,primary_key=True, default=uuid.uuid4)
    user_public_leaf_count = models.BigIntegerField()
    user_private_leaf_count = models.BigIntegerField()
    user_experience_points = models.BigIntegerField()
    user_verified = models.BooleanField(default=False)
    user_followers = models.BigIntegerField(default=0)
    user_following = models.BigIntegerField(default=0)
    user_level = models.BigIntegerField(default=1)
    user_universal_likes = models.BigIntegerField(default=0)
    user_universal_dislikes = models.BigIntegerField(default=0)
    user_universal_comments = models.BigIntegerField(default=0)
    previous_experience_generation_date = models.DateTimeField(default=datetime.datetime.now())
    created_at = models.DateTimeField(auto_now_add=True)

class UserFollowing(models.Model):
    slave = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, related_name="slave")
    master = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, related_name="master")
    created_at = models.DateTimeField(auto_now_add=True)


class UserAccessToken(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, related_name="holy")
    user_session_id = models.CharField(max_length=100, unique=True)
    creation_date = models.DateTimeField(default=datetime.datetime.now())

class UserDetails(models.Model):
    user_full_name = models.CharField(max_length=100,null=False)
    user_id = models.ForeignKey(UserProfile,on_delete=models.DO_NOTHING,related_name='detail')
    user_phone_number = models.CharField(max_length=15,null=False,unique= True)
    user_address = models.CharField(max_length=50,null=False)
    user_phone_id = models.CharField(max_length=120,unique= True,null=False)


#TODO ADD eden user management classes and communicators.
class UserPreferredTopics(models.Model):
    topic_id = models.BigIntegerField(default= -1)
    topic_category = models.BigIntegerField(default=-1)
    topic_view_frequency = models.BigIntegerField(default=0)
    user_object = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING,related_name='user_obj')
    created_at = models.DateTimeField(auto_now_add=True)

class UserBlockedAccounts(models.Model):
    blocker_profile = models.ForeignKey(UserProfile,on_delete=models.DO_NOTHING,related_name='sigma')
    blocked_profile = models.ForeignKey(UserProfile,on_delete=models.DO_NOTHING,related_name='beta')