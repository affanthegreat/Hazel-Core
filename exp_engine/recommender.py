import logging

from django.db.models import Count, Sum

from user_engine.models import *
from leaf_engine.models import *
from exp_engine.models import *
from exp_engine.conx_manager import Eden_CONX_Engine

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
        relation = conX_object.get_user_topic_relation_object(topic_id,user_object)
        bias = 0
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
    
    def get_leaves_query_set(self,topic_id):
        return Leaf.objects.filter(leaf_topic_id= topic_id)

    def get_user_preferences_query_set(self, user_object):
        return UserLeafPreferences.objects.filter(user_object= user_object)
    
    def get_topics_frequency_wise(self, user_object):
        return (self.get_user_preferences_query_set(user_object).
                values("topic_id").
                annotate(total_leaves=Count('topic_id'), total_frequency_per_topic = Sum("topic_visit_frequency ")).
                order_by("-total_frequency_per_topic"))
    
    def get_topics_category_frequency_wise(self, user_object):
        return (self.get_user_preferences_query_set(user_object).
                values("topic_category_id").
                annotate(total_leaves_in_topic=Count('topic_category_id'), total_visits=Sum('topic_visit_frequency')).
                order_by("-total_visits"))
    
    def filter_out_interacted_leaves(self, user_object):
        topics_batch =self.get_topics_frequency_wise(user_object)[0]
        total_topics = len(topics_batch)
        leaf_query_sets = {}
        for i in range(total_topics if total_topics < self.MAX_TOPICS_AT_ONE_TIME
                                         else self.MAX_TOPICS_AT_ONE_TIME):
            topic = topics_batch[i]['topic_id']
            topic_query_set = LeafInteraction.objects.filter(interacted_by= user_object).all()
            priority = (topics_batch[i]['topic_visit_frequency'] / total_topics) * (1 / topics_batch[i]['total_leaves_in_topics'])
            leaf_query_sets[i+1] = (self.get_leaves_query_set(topic_id=topic).
                                    exclude(leaf__in=topic_query_set).all().
                                    annotate(priority = (i+1).
                                    order_by('-creation_date'))[0]

        return leaf_query_sets

    def get_leaf_user_interaction(self, user_object): 
        pass

    def initiate(self):
        leaf_query
        pass
        