import logging
from exp_engine.middleware import EdenUserTopicRelationMiddleWare

from exp_engine.models import *
from leaf_engine.leaf_management import EdenLeafManagement
from user_engine.user_management import EdenUserManagement


class Eden_CONX_Engine():

    def meta(self):
        self.VERSION = 0.6
        self.BUILD_TYPE = "ALPHA"

    def check_field_validity(self, valid_fields, data):
        condition = True
        for field in valid_fields:
                if field not in data.keys():
                    condition = False
        return condition

    def throw_object_creation_failed_error(self,E):
        raise Exception(E)
    
    def throw_invalid_fields_error(self):
        return {"status": 200, "message": "Cannot unload data."}

    def __init__(self) -> None:
        self.meta()
        logging.info("Hazel Recommendation Engine")

    def create_leaf_interaction(self,leaf_object, interacted_by, interaction_type):
        try:

            if not self.check_leaf_interaction(leaf_object,interacted_by,interaction_type):
                leaf_interaction_object = LeafInteraction()
                leaf_interaction_object.leaf = leaf_object
                leaf_interaction_object.interacted_by = interacted_by
                leaf_interaction_object.interaction_type = interaction_type
                leaf_interaction_object.save()
                return 100
            else:
                return -103
        except:
            return -111
        
        
    def create_user_leaf_preference(self, data):
        try:
            if not self.check_user_leaf_preference(data):
                eum_object = EdenUserManagement()
                user_leaf_preference_object = UserLeafPreferences()
                user_leaf_preference_object.topic_id = data['topic_id']
                user_leaf_preference_object.topic_category_id = data['topic_category_id']
                user_leaf_preference_object.topic_visit_frequency = 1
                user_leaf_preference_object.user_object = data['user_id']
                user_leaf_preference_object.save()
                return 100
            else:
                return -111
        except Exception as E:
            self.throw_object_creation_failed_error(E)
    
    def create_user_topic_relation(self,data):
        try:
            eum_object = EdenUserManagement()
            user = eum_object.get_user_object(data['user_id'])
            if not self.check_user_topic_relation(data['topic_id'], user) :
                
                user_topic_relation_object = UserTopicRelations()
                user_topic_relation_object.topic_id = data['topic_id']
                user_topic_relation_object.topic_category_id = data['topic_category_id']
                user_topic_relation_object.user = user
                user_topic_relation_object.save()
                return 100
            else:
                return -111
        except Exception as E:
            self.throw_object_creation_failed_error(E)
    
    def check_user_topic_relation(self, topic_id, user_object):
        return UserTopicRelations.objects.filter(topic_id=topic_id, user= user_object).exists()
    
    def update_user_topic_relation_middleware(self,leaf_id, topic_id, interaction, user_object, value):
        try:
            if self.check_user_topic_relation(topic_id,user_object):
                user_topic_relation_object = self.get_user_topic_relation_object(topic_id,user_object)
                middleware_object = EdenUserTopicRelationMiddleWare(user_topic_relation_object)
                allowed_interactions = ['like',
                                        'dislike',
                                        'comment', 
                                        'sub_comment',
                                        'leaves_served',
                                        'favoritism_weight']
                if interaction not in allowed_interactions:
                    return -111
                else:
                    match interaction:
                        case "like":
                            middleware_object.update_likes_count(value)
                            middleware_object.update_times_interacted(value)
                        case "dislike":
                            middleware_object.update_dislikes_count(value)
                            middleware_object.update_times_interacted(value)
                        case "comments":
                            middleware_object.update_comments(value)
                            middleware_object.update_times_interacted(value)
                        case "sub_comments":
                            middleware_object.update_sub_comments(value)
                            middleware_object.update_times_interacted(value)
                        case "leaves_served":
                            middleware_object.update_total_leaves_served(value)
                            middleware_object.update_times_interacted(value)
                        case "positive_comments_made":
                            middleware_object.update_positive_comments_made(value)
                            middleware_object.update_times_interacted(value)
                        case "negative_comments_made":
                            middleware_object.update_negative_comments_made(value)
                            middleware_object.update_times_interacted(value)
                        case "favoritism_weight":
                            middleware_object.update_favoritism_weight(value)
                    return 100
        except:
            return -112
                            

    
    def get_user_topic_relation_object(self, topic_id, user_object):
        return UserTopicRelations.objects.filter(topic_id=topic_id, user= user_object).first()
    
    def check_leaf_interaction(self,leaf_object,user_object, interaction_type):
        return LeafInteraction.objects.filter(leaf=leaf_object, interacted_by= user_object, interaction_type= interaction_type).exists()
    
    def check_user_leaf_preference(self, data):
        eum_object = EdenUserManagement()
        data_fields = ['topic_id','topic_category','topic_category_id', 'user_id']
        if self.check_field_validity(data_fields, data):
            return UserLeafPreferences.objects.filter(topic_id= data['topic_id'], 
                                                      topic_category_id = data['topic_category_id'],
                                                      user_object = eum_object.get_user_object(data['user_id'])).exists()
        else:
            return False
        
    def check_user_leaf_perference_mini(self,data):
        eum_object = EdenUserManagement()
        data_fields = ['topic_id', 'user_id']
        if self.check_field_validity(data_fields, data):
            return UserLeafPreferences.objects.filter(topic_id= data['topic_id'], 
                                                      user_object = eum_object.get_user_object(data['user_id'])).exists()
        else:
            return False
    def get_user_leaf_preference_mini(self,data):
        eum_object = EdenUserManagement()
        if self.check_user_leaf_perference_mini(data):
            return UserLeafPreferences.objects.filter(topic_id= data['topic_id'], 
                                                      user_object = eum_object.get_user_object(data['user_id'])).first()
    def get_user_leaf_preferences(self, user_object):
        eum_object = EdenUserManagement()
        data = {'user_id': user_object.user_id}
        if eum_object.check_user_exists(data['user_id']):
            return UserLeafPreferences.objects.filter(user_object=user_object).all()
        else:
            return -103

    def get_leaf_interaction(self, leaf_object, interacted_by, interaction_type):
        if self.check_leaf_interaction(leaf_object=leaf_object, interaction_type= interacted_by):
            return LeafInteraction.objects.filter(leaf=leaf_object, interacted_by= interacted_by, interaction_type= interaction_type).first()
        pass

    def update_topic_visit_frequency(self, topic_id, user_object):
        data = {
            'topic_id': topic_id,
            'user_id': user_object.user_id
        }
        if self.check_user_leaf_perference_mini(data):
            try:
                leaf_interaction_object = self.get_user_leaf_preference_mini(data)
                leaf_interaction_object.topic_visit_frequency += 1
                leaf_interaction_object.save()
                return 100
            except:
                return -111
    

    def start_pipeline(self,data):
        elm_object =EdenLeafManagement()
        leaf_id, leaf_interaction_type, leaf_interacted_by = data['leaf_id'], data['leaf_interaction'], data['interacted_by']
        leaf_object = elm_object.get_leaf_object(leaf_id)
        interaction_status = self.check_leaf_interaction(leaf_object ,leaf_interacted_by, leaf_interaction_type)
        if not interaction_status:
            req_data = {
                'topic_id': leaf_object.leaf_topic_id,
                'topic_category_id': leaf_object.leaf_topic_category_id,
                'user_id': leaf_interacted_by,
            }
            self.create_leaf_interaction(leaf_object ,leaf_interacted_by, leaf_interaction_type)
            self.create_user_leaf_preference(req_data)
            return 100
        else:
            leaf_topic_id = leaf_object.leaf_topic_id
            interacted_by_object = elm_object.get_user_object(leaf_interacted_by)
            self.update_topic_visit_frequency(leaf_topic_id,interacted_by_object)
            return 100


