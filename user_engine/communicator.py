import logging

from django.core.paginator import Paginator


from user_engine.models import UserPreferredTopics
from user_engine.user_management import EdenUserManagement

EUM_Object = EdenUserManagement()

class EdenUserCommunicator():

    def __init__(self):
        self.MAX_OBJECT_LIMIT = 50
        logging.info('Eden User Communicator Object created.')

    def update_user_topics(self,data):
        user_id = data['user_id']
        topic_id = data['topic_id']
        if self.check_user_exists(user_id):
            user_topic_object = UserPreferredTopics()
            user_topic_object.topic_id = topic_id
            user_topic_object.user_object = EUM_Object.get_user_object(user_id)
            user_topic_object.save()
            logging.info('user topic object created.')
            return -100
        else:
            return -103
    def stream_user_objects_by_topics(self,topic_id,page_number):
        return self.paginator(UserPreferredTopics.objects.filter(topic_id= topic_id).all(), page_number)

    def check_user_exists(self,user_id):
        return EUM_Object.get_user_object(user_id) is not None

    def paginator(self,query_set,page_number):
        pagination_obj = Paginator(query_set,self.MAX_OBJECT_LIMIT)
        response = {
            'page_number': page_number,
            'total_pages': pagination_obj.page_range[-1],
            'data': list(pagination_obj.page(page_number).object_list.values()),
        }
        return response
