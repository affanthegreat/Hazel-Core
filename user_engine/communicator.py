import logging

from django.core.paginator import Paginator


from user_engine.models import UserBlockedAccounts
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


    def stream_user_blocked_accounts_query_set(self, user_id):
        return UserBlockedAccounts.objects.filter(blocker_profile= EUM_Object.get_user_object(user_id)).all()
    
    def check_user_exists(self,user_id):
        return EUM_Object.get_user_object(user_id) is not None

    def paginator(self,query_set,page_number):
        pagination_obj = Paginator(query_set,self.MAX_OBJECT_LIMIT)
        total_pages = pagination_obj.page_range[-1]
        if page_number > total_pages:
            return {
                "message": f"Page number does not exists. (total pages available : {total_pages})"
            }
        try:
            response = {
                'page_number': page_number,
                'total_pages': total_pages,
                'data': list(pagination_obj.page(page_number).object_list.values()),
            }
        except Exception as E:
            response = {
                    "message": "Cannot load page."
                }

        return response
