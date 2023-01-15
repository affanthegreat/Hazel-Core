import uuid

from leaf_engine.models import Leaf, LeafComments, LeafLikes, LeafType
from user_engine.backends import EdenSessionManagement
from user_engine.models import UserProfile

session_management_object = EdenSessionManagement()

class EdenLeafManagement:
    def generate_leaf_id(self):
        session_id = str(uuid.uuid4()).upper().replace("-","") 
        return session_id
    
    def __init__(self, request) -> None:
        self.request = request
    
    def create_leaf(self, request, data):
        response = {}
        if session_management_object.current_session(request) != None:
            new_leaf_object = Leaf
            new_leaf_object.leaf_id = self.generate_leaf_id()
            new_leaf_object.owner = session_management_object.get_session_user(request)
            new_leaf_object.text_content = data['text_content']
            new_leaf_object.image_content = None
            new_leaf_object.leaf_type = LeafType(data['leaf_type'])
            new_leaf_object.save()
            response['status'] = 200
            response['message'] = "Leaf successfully created."
            response['code'] = True
        else:
            response['status'] = 200
            response['message'] = "User Authenication Failed."
            response['code'] = False
        return response

    def read_leaf(self):
        
        pass

    def delete_leaf(self):
        pass

    def like_leaf(self):
        pass

    def dislike_leaf(self):
        pass

    def add_comment(self):
        pass

    def remove_comment(self):
        pass

    def check_leaf(self, leaf_id):
        leaf_object = Leaf.objects.filter(leaf_id=leaf_id).first()
        return leaf_object is not None

    def check_comment(self):
        pass

    def check_like(self, leaf_id, user_name):
        user_object = self.get_user_object(user_name)
        leaf_valid = self.check_leaf(leaf_id)
        response = {}
        if user_object is not None and leaf_valid:
            leaf_object = self.get_leaf_object(leaf_id)
            leaf_like_object = LeafLikes.objects.filter(leaf_id=leaf_object.leaf_id, liked_by=user_object.user_id)
            response['status'] = 200
            response['message'] = str(leaf_like_object.exists())
            response['code'] = True
        else:
            response['status'] = 200
            response['code'] = False
            if not leaf_valid:
                response['message'] = "Leaf doesn't exist."
            else:
                response['message'] = "User doesn't exist"
        return response

    def get_leaf_object(self, leaf_id):
        if self.check_leaf(leaf_id):
            return Leaf.objects.filter(leaf_id=leaf_id)
        else:
            return None

    def get_comment_object(self):
        pass

    def get_like_object(self, leaf_id, user_name):
        if self.check_like(leaf_id, user_name)['code']:
            user_object = self.get_user_object(user_name)
            leaf_object = self.get_leaf_object(leaf_id)
            return LeafLikes.objects.filter(leaf=leaf_object, liked_by=user_object)
        else:
            None

    #TODO remove these 2 methods
    def is_authorised(self) -> bool:
        return self.request.session.get('user_id', None) == None

    def get_logged_in_user(self):
        if self.is_authorised():
            user_id = self.request.session['user_id']
            return UserProfile.objects.filter(user_id=user_id)
        else:
            return None

    def get_user_object(self, user_name):
        return UserProfile.objects.filter(user_name=user_name).first()
