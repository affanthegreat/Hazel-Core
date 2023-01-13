from django.db import models

from user_engine.models import UserProfile

# Create your models here.


class Leaf(models.Model):
    created_date = models.DateTimeField()
    owner = models.ForeignKey(UserProfile, related_name="creator", on_delete=models.CASCADE)
    text_content = models.CharField(max_length=400, null=False)
    leaf_id = models.CharField(max_length=100, primary_key=True)
    image_content = models.ImageField()
    likes_count = models.BigIntegerField(default=0)
    comments_count = models.BigIntegerField(default=0)


class LeafLikes(models.Model):
    leaf = models.ForeignKey(Leaf, related_name='creator_leaf', on_delete=models.CASCADE)
    liked_by = models.ForeignKey(UserProfile, related_name="liked_user", on_delete=models.DO_NOTHING)


# class PublicLeafComments(models.Model):
#     leaf = models.ForeignKey(Leaf, related_name='creator_leaf', on_delete=models.CASCADE)
#     commented_by = models.ForeignKey(UserProfile, related_name="commented_user", on_delete=models.CASCADE)
#     comment = models.CharField(max_length=100, null=False, on_delete=models.CASCADE)


