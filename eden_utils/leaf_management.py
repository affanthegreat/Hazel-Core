import uuid

from leaf_engine.models import Leaf, LeafComments, LeafLikes, LeafType
from user_engine.backends import EdenSessionManagement
from user_engine.models import UserProfile

session_management_object = EdenSessionManagement()


class EdenLeafManagement:
    def generate_leaf_id(self):
        session_id = str(uuid.uuid4()).upper().replace("-", "")
        return session_id

    def __init__(self) -> None:
        pass

    def create_leaf(self, request, data):
        response = {}
        if self.get_logged_in_user(request):
            new_leaf_object = Leaf
            new_leaf_object.leaf_id = self.generate_leaf_id()
            new_leaf_object.owner = session_management_object.get_session_user(request)
            new_leaf_object.text_content = data['text_content']
            new_leaf_object.image_content = None
            new_leaf_object.leaf_type = LeafType(data['leaf_type'])
            new_leaf_object.save()
            response['status'] = -100
            response['message'] = "Leaf successfully created."
            response['code'] = True
        else:
            response['status'] = -101
            response['code'] = False
        return response

    def get_user_public_leaves(self, request):
        if self.is_authorised(request):
            user_object = self.get_logged_in_user(request)
            return Leaf.objects.filter(owner=user_object, leaf_type=LeafType.Public)
        else:
            return -101

    def get_user_private_leaves(self, request):
        if self.is_authorised(request):
            user_object = self.get_logged_in_user(request)
            return Leaf.objects.filter(owner=user_object, leaf_type=LeafType.Private)
        else:
            return -101

    def delete_leaf(self, request, leaf_id):
        if self.is_authorised(request):
            response = {}
            user_object = self.get_logged_in_user(request)
            leaf_object = self.get_leaf_object(leaf_id)
            if leaf_object.owner == user_object:
                leaf_object.delete()
                response['message'] = f"-100"
            else:
                response['message'] = "-102"
            return response

    #TODO add User Engine value updation mechanism
    def like_leaf(self,request, leaf_id):
        if self.is_authorised(request):
            user_object = self.get_logged_in_user(request)
            if self.check_leaf(leaf_id) and not self.check_like(leaf_id, user_object.user_id)['message']:
                like_object = LeafLikes()
                like_object.leaf = self.get_leaf_object(leaf_id)
                like_object.liked_by = user_object
                like_object.save()
                return -100
            else:
                return -103
    
    #TODO add User Engine value updation mechanism
    def dislike_leaf(self,request,leaf_id):
        if self.is_authorised(request):
            user_object = self.get_logged_in_user(request)
            like_status = self.check_like(leaf_id, user_object.user_id)
            try:
                if self.check_leaf(leaf_id) and like_status['message'] :
                    like_object = self.get_like_object(leaf_id,user_object.user_id)
                    like_object.delete()
                    return -100
            except Exception:
                return -105

    def get_total_likes(self,leaf_id):
        if self.check_leaf(leaf_id):
            return LeafLikes.objects.filter(leaf_id = leaf_id)
        else:
            return -104

    def get_total_comments(self,request,leaf_id):
        if self.check_leaf(leaf_id):
            return LeafComments.objects.filter(leaf_id = leaf_id)
        else:
            return -104

    #TODO add User Engine value updation mechanism
    def add_comment(self,request ,leaf_id, comment_string):
        if self.is_authorised(request):
            user_object = self.get_logged_in_user(request)
            comment_status = self.check_like(leaf_id, user_object.user_id)
            if comment_string != None:
                try:
                    if self.check_leaf(leaf_id) and comment_status['message']:
                        leaf_comment_object = LeafComments()
                        leaf_comment_object.commented_by = user_object
                        leaf_comment_object.leaf = self.get_leaf_object(leaf_id)
                        leaf_comment_object.comment = comment_string
                        return -100
                except Exception:
                    return -103
        else:
            return -101
    
    #TODO add User Engine value updation mechanism
    def remove_comment(self,request, leaf_id):
        if self.is_authorised(request):
            user_object = self.get_logged_in_user(request)
            comment_status = self.check_comment(leaf_id, user_object.user_id)
            try:
                if self.check_leaf(leaf_id) and comment_status['message'] :
                    comment_object = self.get_comment_object(leaf_id,user_object.user_id)
                    comment_object.delete()
                    return -100
            except Exception:
                return -105       
        pass

    def check_leaf(self, leaf_id):
        leaf_object = Leaf.objects.filter(leaf_id=leaf_id).first()
        return leaf_object is not None

    def check_comment(self,leaf_id,user_id):
        user_object = self.get_user_object(user_id)
        leaf_valid = self.check_leaf(leaf_id)
        response = {}
        if user_object is not None and leaf_valid:
            leaf_object = self.get_leaf_object(leaf_id)
            leaf_comment_object = LeafComments.objects.filter(leaf_id=leaf_object.leaf_id, commented_by=user_object.user_id)
            response['status'] = -100
            response['message'] = leaf_comment_object.exists()
            response['code'] = True
        else:
            response['status'] = -104
            response['code'] = False
            if not leaf_valid:
                response['message'] = "Leaf doesn't exist."
            else:
                response['message'] = "User doesn't exist"
        return response

    def check_like(self, leaf_id, user_id):
        user_object = self.get_user_object(user_id)
        leaf_valid = self.check_leaf(leaf_id)
        response = {}
        if user_object is not None and leaf_valid:
            leaf_object = self.get_leaf_object(leaf_id)
            leaf_like_object = LeafLikes.objects.filter(leaf_id=leaf_object.leaf_id, liked_by=user_object.user_id)
            response['status'] = -100
            response['message'] = leaf_like_object.exists()
            response['code'] = True
        else:
            response['status'] = -100
            response['code'] = False
            if not leaf_valid:
                response['message'] = "Leaf doesn't exist."
            else:
                response['message'] = "User doesn't exist"
        return response

    def get_leaf_object(self, leaf_id):
        if self.check_leaf(leaf_id):
            return Leaf.objects.filter(leaf_id=leaf_id)

    def get_comment_object(self,leaf_id,user_id):
        if self.check_leaf(leaf_id):
            return Leaf.objects.filter(leaf_id=leaf_id)

    def get_like_object(self, leaf_id, user_id):
        leaf_info = self.check_like(leaf_id, user_id)['message'] 
        if leaf_info['message'] and leaf_info['code'] :
            user_object = self.get_user_object(user_id)
            leaf_object = self.get_leaf_object(leaf_id)
            return LeafLikes.objects.filter(leaf=leaf_object, liked_by=user_object)
        else:
            None

    def is_authorised(self, request) -> bool:
        return session_management_object.current_session(request) != None and session_management_object.check_session(request.session['auth_token'])

    def get_logged_in_user(self, request):
        return session_management_object.get_session_user(request)

    def get_user_object(self, user_id):
        return UserProfile.objects.filter(user_name=user_id).first()

