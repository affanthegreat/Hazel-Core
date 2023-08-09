import logging
from itertools import chain
import random

from django.db.models import Count, F
from user_engine.models import UserFollowing

from user_engine.user_management import EdenUserManagement
from user_engine.communicator import EdenUserCommunicator
from leaf_engine.leaf_management import EdenLeafManagement
from leaf_engine.communicator import EdenLeafCommunicator
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
        self.parameters()
        logging.info("Hazel Recommendation Engine")

    def priority_weights(self):
        self.topic_likes_weight = 0.2
        self.topic_comments_weight = 0.6
        self.topic_sub_comments_weight = 0.5
        self.positive_comments_weight = 0.4
        self.negative_comments_weight = -0.1
        self.interactions_weight = 0.05
        self.average_sentiment_value = 0.2

    
    def parameters(self):
        self.FOLLOWING_MIX = 1
        self.RELEVENT_LEAF_MIX = 0.6
        self.NEW_TOPICS_MIX = 0.2
        self.ADS_MIX = 0.3
        
        self.MAX_NUMBER_OF_NEW_TOPICS = 6
        self.MAX_LEAVES_PER_NEW_TOPIC = 10
        self.MAX_lEAVES_PER_BIASED_TOPIC = 30
        
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

    def total_items_in_query_set(self, query_set):
        return query_set.count()
    
    def filter_leaves(self,queryset):
        user_interacted_leaves = self.get_leaf_user_interaction()
        user_blocked_accounts = EdenUserCommunicator().stream_user_blocked_accounts_query_set(self.user_object.user_id)
        without_interacted_leaves = queryset.exclude(leaf_id__in=user_interacted_leaves.objects.values('leaf')).order_by('-leaf_exp_points')
        without_blocked_users = without_interacted_leaves.exclude(owner__in=user_blocked_accounts.objects.values('blocked_profile'))
        return without_blocked_users

    def filter_following_leaves(self, queryset):
        user_interacted_leaves = self.get_leaf_user_interaction()
        without_interacted_leaves = queryset.exclude(leaf_id__in=user_interacted_leaves.objects.values('leaf')).order_by('-leaf_exp_points')
        return without_interacted_leaves

    def make_user_following_query_sets(self):
        query_set_list = []
        elm_object = EdenLeafManagement
        following_queryset = UserFollowing.objects.filter(slave=self.user_object)
        for relation in following_queryset:
            user = relation.master.user_id
            leaves_query_set = elm_object.get_leaves_by_user_id(user)
            query_set_list.append(self.filter_following_leaves(leaves_query_set))
        merged_query_set = self.merge_query_sets(query_set_list)
        return merged_query_set

    def get_leaf_user_interaction(self): 
        return LeafInteraction.objects.filter(interacted_by = self.user_object)
    
    def get_user_preferred_topics(self):
        return (UserLeafPreferences.objects.filter(user_object = self.user_object).
                all().values('topic_id').
                annotate(leaves_with_topic_id = Count('topic_id')).
                order_by("-leaves_with_topic_id"))

    def generate_bias_for_user_topics(self,topic_query_set):
        bias_map = {}
        for topic_obj in topic_query_set:
            topic_id = topic_obj.topic_id
            bias = self.calculate_favoritism_weight(topic_id, self.user_object)
            bias_map[topic_id] = bias
        return sorted(bias_map.items(),key=lambda x: x[1])[::-1]
    
    def get_leafs_priority_wise(self,topic_id):
        leaf_communicator = EdenLeafCommunicator()
        return leaf_communicator.stream_leaves_topic_wise_query_set({'topic_id':topic_id})
    
    def make_leaf_query_sets(self,bias_map):
        queryset_list = []
        for topic_id, _ in bias_map:
            queryset= self.get_leafs_priority_wise(topic_id)
            if queryset is not None:
                filtered_query_set = self.filter_leaves(queryset)
                queryset_list.append(filtered_query_set[:filtered_query_set.count() * self.RELEVENT_LEAF_MIX])
            else:
               logging.info(f"No leaves found from the topic {topic_id}")
        merged_query_set = self.merge_query_sets(queryset_list)
        return merged_query_set

    def make_topic_wise_query_sets(self):
        topics = self.get_user_preferred_topics(self.user_object)
        bias_map = self.generate_bias_for_user_topics(topics)
        return self.make_leaf_query_sets(bias_map)

    def get_topic_category_id(self,topic_id):
        try:
            return (UserLeafPreferences.objects.filter(topic_id=topic_id).first()).topic_category_id
        except:
            None
            
    def get_highest_rated_leaves_in_topic(self, topic_id):
        leaf_communicator = EdenLeafCommunicator()
        leaf_query_set = leaf_communicator.stream_top_rated_leaves_in_topic({'topic_id':topic_id})
        return self.filter_leaves(leaf_query_set)

    def make_similar_topics_query_sets(self):
        queryset_list = []
        topics = self.get_user_preferred_topics(self.user_object)
        bias_map = self.generate_bias_for_user_topics(topics)[:self.MAX_TOPICS_AT_ONE_TIME]
        for topic_id, _ in bias_map:
            topic_category_id = self.get_topic_category_id(topic_id)
            if topic_category_id:
                query_set = self.get_highest_rated_leaves_in_topic(topic_category_id)
                if query_set.count() > self.MAX_LEAVES_PER_NEW_TOPIC:
                    queryset_list.append(query_set[:query_set.count() * self.NEW_TOPICS_MIX])
        merged_query_set = self.merge_query_sets(queryset_list)
        return merged_query_set

    def make_query_sets_list(self):
        query_sets = []
        query_sets.extend(self.make_user_following_query_sets())
        query_sets.extend(self.make_topic_wise_query_sets())
        query_sets.extend(self.make_similar_topics_query_sets())
        #query_sets += self.make_relevent_ad_query_sets()
        
        return query_sets
    
    def merge_query_sets(self, query_set_list):
        return list(chain(*query_set_list))

    
    def initiate(self, user_id):
        eum_object = EdenUserManagement()
        self.user_object = eum_object.get_user_object(user_id)
        