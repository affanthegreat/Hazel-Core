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


class CommentVoteType(models.TextChoices):
    Upvote = "upvote", "upvote"
    Downvote = "downvote", "downvote"



class Leaf(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        UserProfile, related_name="creator", on_delete=models.CASCADE
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
    exp_points = models.DecimalField(default=0,max_digits=15,decimal_places=6)
    previous_analytics_run = models.DateTimeField(default=datetime.datetime.now())
    leaf_topic_id = models.BigIntegerField(default= -1)
    leaf_topic_category_id = models.IntegerField(max_length=3)
    leaf_sentiment = models.DecimalField(default=-69,max_digits=6,decimal_places=6)
    leaf_emotion_state = models.CharField(max_length=30,default="NULL")
    is_promoted = models.BooleanField(default=False)
    is_advertisement = models.BooleanField(default=False)
    topic_relevenacy_percentage= models.DecimalField(default=0,max_digits=15,decimal_places=6)
    category_relevancy_percentage = models.DecimalField(default=0,max_digits=15,decimal_places=6)

class LeafLikes(models.Model):
    like_id = models.CharField(max_length=100, blank=True, unique=True,primary_key=True ,default=uuid.uuid4)
    leaf = models.ForeignKey(
        Leaf, related_name="creator_comment_leaf", on_delete=models.CASCADE
    )
    liked_by = models.ForeignKey(
        UserProfile, related_name="liked_user", on_delete=models.DO_NOTHING
    )
    created_date = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ("leaf", "liked_by"),

class LeafDisLikes(models.Model):
    dislike_id = models.CharField(max_length=100, blank=True, unique=True,primary_key=True ,default=uuid.uuid4)
    leaf = models.ForeignKey(
        Leaf, related_name="content_leaf", on_delete=models.CASCADE
    )
    disliked_by = models.ForeignKey(
        UserProfile, related_name="disliked_user", on_delete=models.DO_NOTHING
    )
    created_date = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together =  ("leaf", "disliked_by")


class LeafComments(models.Model):
    comment_id = models.CharField(max_length=100, blank=True, unique=True,primary_key=True, default=uuid.uuid4)
    leaf = models.ForeignKey(
        Leaf, related_name="creator_leaf", on_delete=models.CASCADE
    )
    commented_by = models.ForeignKey(
        UserProfile, related_name="commented_user", on_delete=models.CASCADE
    )
    comment = models.CharField(max_length=100, null=False)
    comment_depth = models.IntegerField(default=1,null=False)
    votes = models.BigIntegerField(default=0)
    comment_sentiment = models.DecimalField(default=-69,max_digits=6,decimal_places=6)
    comment_emotion = models.CharField(max_length=40,default="NULL")
    root_comment = models.ForeignKey('self',null=True, blank= True, on_delete=models.CASCADE, related_name='main_comment' )
    parent_comment = models.ForeignKey('self',null=True,blank=True,on_delete=models.CASCADE,related_name='replies')
    created_date = models.DateTimeField(auto_now_add=True)

class LeafViewedBy(models.Model):
    leaf = models.ForeignKey(Leaf, related_name="viewed_leaf", on_delete=models.CASCADE)
    viewed_by = models.ForeignKey(
        UserProfile, related_name="viewer", on_delete=models.CASCADE
    )
    view_date = models.DateTimeField(auto_now_add=True)


class CommentVotes(models.Model):
    comment = models.ForeignKey(LeafComments, related_name="voted_comment", on_delete=models.CASCADE)
    voted_by = models.ForeignKey(UserProfile, related_name="voter", on_delete= models.CASCADE)
    vote_type =  models.CharField(choices=CommentVoteType.choices, max_length=30)
    class Meta:
        unique_together = ("comment", "voted_by"),

class LeafHashtags(models.Model):
    hashtag_string = models.CharField(max_length=100, null= False)
    associated_leaf = models.ForeignKey(Leaf, related_name="hashtaged_leaf", on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)


class LeafUserMentions(models.Model):
    mentioned_user = models.ForeignKey(
        UserProfile, related_name="mentioned_user", on_delete=models.CASCADE
    )
    mentioned_in_leaf = models.ForeignKey(Leaf, related_name="mentioned_leaf", on_delete=models.CASCADE)
    
    
class CommentUserMentions(models.Model):
    mentioned_user = models.ForeignKey(
        UserProfile, related_name="mentioned_comment_userr", on_delete=models.CASCADE
    )
    mentioned_in_comments = models.ForeignKey(LeafComments, related_name="mentioned_comment", on_delete=models.CASCADE)
   
   
class LeafExpLogs(models.Model):
    exp_points_per_day = models.DecimalField(default=0,max_digits=15,decimal_places=6)
    linked_leaf =  models.ForeignKey(Leaf, related_name="linked_leaf", on_delete=models.CASCADE)
    time_of_logging = models.DateTimeField(auto_now_add=True)

class LeafHashtagsLog(models.Model):
    period_usage = models.BigIntegerField(default=0)
    hashtag = models.CharField(max_length=100, unique=True)
    time_of_logging = models.DateTimeField(auto_now_add=True)

def throw_model_not_saved_error():
    logging.error("Model couldn't be saved.")
    raise Exception("Model not saved.")
    
@receiver(pre_save, sender=Leaf)
def start_leaf_text_ml_pipeline(sender, instance, **kwargs):
    if not instance:
        return
    if hasattr(instance, '_dirty'):
        return
    if instance.leaf_topic_id == -1 or instance.leaf_sentiment == -69 or instance.leaf_emotion_state == "NULL":
        logging.info("> Initiating pre save function.")
        try:
            response = json.loads(leaf_text_pipeline_object.start_leaf_text_ml_workflow(instance).content)
            if 'status' in response and response('status') == -101:
                raise Exception(response['message'])
            from exp_engine.exp_conx_manager import Eden_CONX_Engine
            response['user_id'] = instance.owner.user_id
            conx_engine_instance = Eden_CONX_Engine()
            conx_response = conx_engine_instance.create_user_topic_relation(response)
            if conx_response == 100 or conx_response == -111:
                instance.leaf_topic_id = response['topic_id']
                instance.leaf_sentiment= response['sentiment_value']
                instance.leaf_emotion_state = response['emotion_state']
                instance.leaf_topic_category_id = response['topic_category_id']
            else:
                raise Exception("Conx Failed.")

        except Exception as E:
            instance.delete()
            throw_model_not_saved_error()
    try:
        instance._dirty = True
        instance.save()
    except Exception as E:
        throw_model_not_saved_error()
    finally:
        del instance._dirty



@receiver(pre_save, sender=LeafComments)
def start_comment_text_ml_pipeline(sender, instance, **kwargs):
    if not instance:
        return
    if hasattr(instance, '_dirty'):
        return
    if (instance.comment_sentiment == -69 and 
        instance.comment_emotion == "NULL"):
        try:
            response = json.loads(leaf_text_pipeline_object.start_comment_text_ml_workflow(instance).content)
            if 'status' in response and response('status') == -101:
                raise Exception(response['message'])
            instance.comment_sentiment = response['sentiment_value'] 
            instance.comment_emotion = response['emotion_state']
        except Exception as E:
            print(E)
            instance.delete()
            throw_model_not_saved_error()
    try:
        instance._dirty = True
        instance.save()
    except Exception as e:
        print(e)
        instance.delete()
        throw_model_not_saved_error()
    finally:
        del instance._dirty
   