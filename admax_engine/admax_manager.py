import logging
from user_engine.backends import EdenSessionManagement 

from user_engine.user_management import EdenUserManagement
from leaf_engine.leaf_management import EdenLeafManagement
from admax_engine.models import Advertisements


session_management_object = EdenSessionManagement()
leaf_management_object = EdenLeafManagement()

class Eden_ADMAX_Engine():
    
    def meta(self):
        self.VERSION = 0.5
    
    def __init__(self) -> None:
        self.meta()
        logging.info(f"Eden_ADMAX_Engine {self.VERSION}")
    
    def create_advertisement_instance(self,reqeust,data):
        leaf_creation_response = leaf_management_object.create_leaf(reqeust,data)
        try:
            leaf_id = leaf_creation_response['leaf_id']
            leaf_object = leaf_management_object.get_leaf_object(leaf_id)
            advertisement_obj = Advertisements()
            advertisement_obj.leaf = leaf_object
            advertisement_obj.created_by = leaf_object.owner
            advertisement_obj.target_topic_id = data['target_topic_id']
            advertisement_obj.target_topic_category = leaf_object.leaf_topic_category_id
            advertisement_obj.advertisement_tier = data['advertisement_tier']
            advertisement_obj.is_active = True
            return {'status':200, 'message': f"Advertisement is active."}
        except Exception as e:
            return {'status':200, 'message': f"Advertisement could not be created. ({e}) "}
        
    
    def fetch_advertisement_instance(self, user_object, leaf):
        return Advertisements.objects.filter(created_by = user_object, leaf= leaf).get()
    
    def delete_ad(self,request,data): 
        try:
            leaf_deletion_status = leaf_management_object.delete_leaf(request,data['leaf_id'])
            if leaf_deletion_status['message'] == '-100':
                return  {'status':200, 'message': f"Advertisement deleted."}

        except Exception as e:
            return {}

    def check_ad_exists(self):
        pass
    
    def get_ad_analytics(self):
        pass
    
    def stream_ads_topic_wise(self):
        pass
    
    def stream_ads_topic_category_wise(self):
        pass
    
    def is_authorised(self, request) -> bool:

        return session_management_object.current_session(
            request
        ) != None and session_management_object.check_session(
            request.session["auth_token"]
        )
