import datetime
import uuid
import logging
import json

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver


from user_engine.models import UserProfile
from eden_pipelines.AILib_leaf_pipeline import HazelAI_Leaf_Pipeline


leaf_text_pipeline_object = HazelAI_Leaf_Pipeline()


class LeafType(models.TextChoices):
    Public = "public", "public"
    Private = "private", "private"


class Leaf(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        UserProfile, related_name="creator", on_delete=models.DO_NOTHING
    )
    text_content = models.CharField(max_length=400, null=False)
    leaf_id = models.CharField(max_length=100,primary_key=True)
    image_content = models.ImageField()
    likes_count = models.BigIntegerField(default=0)
    dislikes_count = models.BigIntegerField(default=0)
    comments_count = models.BigIntegerField(default=0)
    view_count = models.BigIntegerField(default=0)
    leaf_type = models.CharField(choices=LeafType.choices, max_length=30)
    engagement_rating = models.DecimalField(default=0, decimal_places=2, max_digits=125)
    experience_rating = models.DecimalField(default=0, decimal_places=2, max_digits=125)
    previous_analytics_run = models.DateTimeField(default=datetime.datetime.now())
    leaf_topic_id = models.BigIntegerField(default= -1)
    leaf_sentiment = models.IntegerField(default=-69)
    leaf_emotion_state = models.CharField(max_length=30)


class LeafLikes(models.Model):
    like_id = models.CharField(max_length=100, blank=True, unique=True,primary_key=True ,default=uuid.uuid4)
    leaf = models.ForeignKey(
        Leaf, related_name="creator_comment_leaf", on_delete=models.CASCADE
    )
    liked_by = models.ForeignKey(
        UserProfile, related_name="liked_user", on_delete=models.DO_NOTHING
    )


class LeafDisLikes(models.Model):
    dislike_id = models.CharField(max_length=100, blank=True, unique=True,primary_key=True ,default=uuid.uuid4)
    leaf = models.ForeignKey(
        Leaf, related_name="content_leaf", on_delete=models.CASCADE
    )
    disliked_by = models.ForeignKey(
        UserProfile, related_name="disliked_user", on_delete=models.DO_NOTHING
    )


class LeafComments(models.Model):
    comment_id = models.CharField(max_length=100, blank=True, unique=True,primary_key=True, default=uuid.uuid4)
    leaf = models.ForeignKey(
        Leaf, related_name="creator_leaf", on_delete=models.DO_NOTHING
    )
    commented_by = models.ForeignKey(
        UserProfile, related_name="commented_user", on_delete=models.DO_NOTHING
    )
    comment = models.CharField(max_length=100, null=False)
    comment_depth = models.IntegerField(default=1,null=False)
    comment_sentiment = models.IntegerField(default=-69)
    comment_emotion = models.CharField(max_length=40)
    root_comment = models.ForeignKey('self',null=True, blank= True, on_delete=models.DO_NOTHING, related_name='main_comment' )
    parent_comment = models.ForeignKey('self',null=True,blank=True,on_delete=models.CASCADE,related_name='replies')
    
    
def throw_model_not_saved_error():
    logging.error("Model couldn't be saved.")
    raise Exception("Model not saved.")
    
@receiver(pre_save, sender=Leaf)
def start_leaf_text_ml_pipeline(sender, instance, **kwargs):
    if not instance:
        return
    if hasattr(instance, '_dirty'):
        return
    try:
        response = json.loads(leaf_text_pipeline_object.start_leaf_text_ml_workflow(instance).content)
        if 'status' in response and response('status') == -101:
            raise Exception(response['message'])
        instance.leaf_topic_id = response['topic_id']
        instance.leaf_sentiment= response['sentiment_value']
        instance.leaf_emotion_state = response['emotion_state']
        try:
            instance._dirty = True
            instance.save()
        except Exception as e:
            instance.delete()
            throw_model_not_saved_error()
        finally:
            del instance._dirty
    except Exception as E:
        instance.delete()
        throw_model_not_saved_error()


@receiver(pre_save, sender=LeafComments)
def start_comment_text_ml_pipeline(sender, instance, **kwargs):
    if not instance:
        return
    if hasattr(instance, '_dirty'):
        return
    try:
        response = json.loads(leaf_text_pipeline_object.start_comment_text_ml_workflow(instance).content)
        if 'status' in response and response('status') == -101:
            raise Exception(response['message'])
        instance.comment_sentiment = response['sentiment_value'] 
        instance.comment_emotion = response['emotion_state']
        try:
            instance._dirty = True
            instance.save()
        except Exception as e:
            instance.delete()
            throw_model_not_saved_error()
        finally:
            del instance._dirty
    except Exception as E:
        instance.delete()
        throw_model_not_saved_error()