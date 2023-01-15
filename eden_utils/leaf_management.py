from leaf_engine.models import Leaf, LeafComments, LeafLikes
from user_engine.models import UserProfile


class EdenLeafManagement:
    def __init__(self, request) -> None:
        self.request = request

    def create_leaf(self):
        pass

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

    #remove these 2 methods
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
