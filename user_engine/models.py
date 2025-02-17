from django.db import models
import datetime
import uuid


class UserProfile(models.Model):
    user_email = models.EmailField(unique=True)
    user_name = models.CharField(max_length=60, unique=True)
    user_password = models.CharField(max_length=250)
    user_id = models.CharField(max_length=100, blank=True, unique=True,primary_key=True, default=uuid.uuid4)
    user_public_leaf_count = models.BigIntegerField(default=0)
    user_private_leaf_count = models.BigIntegerField(default=0)
    user_experience_points = models.BigIntegerField(default=0)
    user_verified = models.BooleanField(default=False)
    user_followers = models.BigIntegerField(default=0)
    user_following = models.BigIntegerField(default=0)
    user_level = models.BigIntegerField(default=1)
    user_universal_likes = models.BigIntegerField(default=0)
    user_universal_dislikes = models.BigIntegerField(default=0)
    user_universal_comments = models.BigIntegerField(default=0)
    previous_experience_generation_date = models.DateTimeField(default=datetime.datetime.now())
    user_dp = models.ImageField()
    created_at = models.DateTimeField(auto_now_add=True)

class UserFollowing(models.Model):
    slave = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="slave")
    master = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="master")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["slave", "master"]),
            models.Index(fields=["master", "slave"]),
        ]

class UserAccessToken(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="holy")
    user_session_id = models.CharField(max_length=100, unique=True)
    creation_date = models.DateTimeField(default=datetime.datetime.now())

class UserDetails(models.Model):
    user_bio = models.CharField(max_length=120, null=False)
    user_country = models.CharField(max_length=100,null=False)
    user_state = models.CharField(max_length=100, null=False)
    user_region = models.CharField(max_length=100, name=False)
    user_city = models.CharField(max_length=100, null= False)
    user_gender = models.CharField(max_length=15, null = False)
    user_age = models.PositiveIntegerField(default=1)
    user_full_name = models.CharField(max_length=100,null=False)
    user_id = models.ForeignKey(UserProfile,on_delete=models.CASCADE,related_name='detail')
    user_phone_number = models.CharField(max_length=15,null=False,unique= True)
    user_address = models.CharField(max_length=50,null=False)
    user_phone_id = models.CharField(max_length=120,unique= True,null=False)

class UserBlockedAccounts(models.Model):
    blocker_profile = models.ForeignKey(UserProfile,on_delete=models.CASCADE,related_name='sigma')
    blocked_profile = models.ForeignKey(UserProfile,on_delete=models.CASCADE,related_name='beta')

    class Meta:
        indexes = [
            models.Index(fields=["blocker_profile", "blocked_profile"]),
            models.Index(fields=["blocked_profile", "blocker_profile"]),
        ]

    
class UserFollowRequests(models.Model):
    status = models.BooleanField(default=False)
    id = models.CharField(max_length=100, blank=True, unique=True,primary_key=True, default=uuid.uuid4)
    requester = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="requester")
    requested_to = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="requested_to")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["requester", "requested_to"]),
            models.Index(fields=["requested_to", "requester"]),
        ]
