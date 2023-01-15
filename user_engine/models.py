from django.db import models
import datetime

class UserProfile(models.Model):
    user_email = models.EmailField(unique=True)
    user_name = models.CharField(max_length=60, unique= True)
    user_password = models.CharField(max_length=250)
    user_id = models.CharField(max_length=120, primary_key=True, unique=True,)
    user_public_leaf_count = models.BigIntegerField()
    user_private_leaf_count = models.BigIntegerField()
    user_experience_points = models.BigIntegerField()
    user_verified = models.BooleanField(default=False)
    user_followers = models.BigIntegerField(default=0)
    user_following = models.BigIntegerField(default=0)
    user_level = models.BigIntegerField(default=1)


class UserFollowing(models.Model):
    slave = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="slave")
    master = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="master")


class UserAccessToken(models.Model):
    user = models.ForeignKey(UserProfile,on_delete=models.CASCADE, related_name="holy")
    user_session_id = models.CharField(max_length=100,unique=True)
    creation_date = models.DateTimeField(default = datetime.datetime.now())