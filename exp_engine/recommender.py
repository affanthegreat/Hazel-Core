import logging

from django.db.models import Count, Sum
from leaf_engine.leaf_management import EdenLeafManagement

from user_engine.models import *
from leaf_engine.models import *
from exp_engine.models import *
from exp_engine.conx_manager import Eden_CONX_Engine
from user_engine.user_management import EdenUserManagement

conX_object = Eden_CONX_Engine()

class HazelRecommendationEngine():

    def meta(self):
        self.VERSION = 0.1
        self.BUILD_TYPE = "ALPHA"
        self.MAX_TOPICS_AT_ONE_TIME = 25

    def __init__(self) -> None:
        self.meta()
        self.priority_weights()
        logging.info("Hazel Recommendation Engine")

    def priority_weights(self):
        self.topic_likes_weight = 0.2
        self.topic_comments_weight = 0.6
        self.topic_sub_comments_weight = 0.5
        self.positive_comments_weight = 0.4
        self.negative_comments_weight = -0.1
        self.interactions_weight = 0.05
        self.average_sentiment_value = 0.2

    
    def sort_parameters(self):
        self.use_user_following = True
        self.use_visit_frequency = True
        self.use_leaf_sentiment = True
        self.use_leaf_emotion = True
        self.use_exp_points = True
        self.use_creation_date = True
    
    def calculate_favoritism_weight(self,topic_id,user_object):
        bias = 0
        relation = conX_object.get_user_topic_relation_object(topic_id,user_object)
       
        bias += self.topic_likes_weight * (relation.likes - relation.dislikes)
        bias += self.topic_comments_weight * (relation.comments)
        bias += self.topic_sub_comments_weight * relation.sub_comments
        bias += self.positive_comments_weight * relation.positive_comments_made
        bias += self.negative_comments_weight * relation.negative_comments_made
        bias += self.interactions_weight * (relation.times_interacted / relation.leaves_served_by_engine)
        bias += self.average_sentiment_value * ((relation.positive_comments_made + relation.negative_comments_made)
                                                / (relation.comments + relation.sub_comments))
        
        relation.favoritism_weight = bias
        relation.save()
        return bias

    
    def assign_priorities_topic_wise(self):
        pass
    
    def sort_leaves(self):
        pass

    def filter_leaves(self):
        pass

    def mix_new_categories(self):
        pass

    def mix_user_following_leaves(self):
        pass

    def get_leaf_user_interaction(self, user_object): 
        return LeafInteraction.objects.filter(interacted_by = user_object)
    
    def get_user_preferred_topics(self, user_object):
        return (UserLeafPreferences.objects.filter(user_object = user_object).
                all().values('topic_id').
                annotate(leaves_with_topic_id = Count('topic_id')).
                order_by("-leaves_with_topic_id"))

    def initiate(self):
        self.generate_bias_for_user_topics
        pass
        