import uuid
from leaf_engine.middleware import EdenLeafMiddleware

from leaf_engine.models import Leaf, LeafComments, LeafDisLikes, LeafLikes, LeafType
from user_engine.backends import EdenSessionManagement
from user_engine.models import UserProfile
from user_engine.middleware import EdenUserMiddleWare
from user_engine.user_management import EdenUserManagement

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
            new_leaf_object = Leaf()
            new_leaf_object.leaf_id = self.generate_leaf_id()
            new_leaf_object.owner = session_management_object.get_session_user(request)
            new_leaf_object.text_content = data["text_content"]
            new_leaf_object.image_content = None
            new_leaf_object.leaf_type = LeafType(data["leaf_type"])
            new_leaf_object.save()
            if LeafType(data['leaf_type']) == LeafType.Private:
                self.run_user_middleware(self.get_logged_in_user(request), "update_private_leaf", 1)
            else:
                self.run_user_middleware(self.get_logged_in_user(request), "update_public_leaf", 1)
            response["status"] = -100
            response["message"] = "Leaf successfully created."
            response["code"] = True
        else:
            response["status"] = -101
            response["code"] = False
        return response

    def get_user_public_leaves(self, request):
        if self.is_authorised(request):
            user_object = self.get_logged_in_user(request)
            print(user_object)
            return Leaf.objects.filter(owner=user_object, leaf_type=LeafType.Public).all()
        else:
            return -101
    
    def get_leaves(self, request, user_id):
        follower_user = self.get_logged_in_user(request)
        user_management_instance = EdenUserManagement()
        if user_management_instance.check_user_exists({'user_id': user_id}):
            following_object = user_management_instance.get_user_object(user_id)
            if user_management_instance.check_following(following_object,follower_user):
                return Leaf.objects.filter(owner=following_object).all()
            else:
                return Leaf.objects.filter(owner=following_object, leaf_type=LeafType.Public).all()
        else:
            return -101
    



    def get_user_private_leaves(self, request):
        if self.is_authorised(request):
            user_object = self.get_logged_in_user(request)
            return Leaf.objects.filter(owner=user_object, leaf_type=LeafType.Private).all()
        else:
            return -101

    def delete_leaf(self, request, leaf_id):
        if self.is_authorised(request):
            response = {}
            user_object = self.get_logged_in_user(request)
            leaf_object = self.get_leaf_object(leaf_id)
            if leaf_object.owner == user_object:
                leaf_object.delete()
                response["message"] = f"-100"
            else:
                response["message"] = "-102"
            return response

    def like_leaf(self, request, leaf_id):
        if self.is_authorised(request):
            user_object = self.get_logged_in_user(request)
            print(self.check_like(leaf_id, user_object.user_id)["message"])
            if (
                self.check_leaf(leaf_id)
                and not self.check_like(leaf_id, user_object.user_id)["message"]
            ):
                like_object = LeafLikes()
                like_object.leaf = self.get_leaf_object(leaf_id)
                like_object.liked_by = user_object
                like_object.save()
                self.run_leaf_middleware(self.get_leaf_object(leaf_id), "update_likes", 1)
                return -100
            else:
                return -103

    def dislike_leaf(self, request, leaf_id):
        if self.is_authorised(request):
            user_object = self.get_logged_in_user(request)
            if (
                self.check_leaf(leaf_id)
                and not self.check_dislike(leaf_id, user_object.user_id)["message"]
            ):
                dislike_object = LeafDisLikes()
                dislike_object.leaf = self.get_leaf_object(leaf_id)
                dislike_object.disliked_by = user_object
                dislike_object.save()
                self.run_leaf_middleware(self.get_leaf_object(leaf_id), "update_dislikes", 1)
                return -100
            else:
                return -103

    def remove_like(self, request, leaf_id):
        if self.is_authorised(request):
            user_object = self.get_logged_in_user(request)
            like_status = self.check_like(leaf_id, user_object.user_id)
            print(like_status)
            if self.check_leaf(leaf_id) and like_status["message"]:
                like_object = self.get_like_object(leaf_id, user_object.user_id)
                like_object.delete()
                self.run_leaf_middleware(self.get_leaf_object(leaf_id), "update_likes", -1)
                return -100
            else:
                return -105

    def remove_dislike(self, request, leaf_id):
        if self.is_authorised(request):
            user_object = self.get_logged_in_user(request)
            like_status = self.check_dislike(leaf_id, user_object.user_id)
            if self.check_leaf(leaf_id) and like_status["message"]:
                dislike_object = self.get_dislike_object(leaf_id, user_object.user_id)
                dislike_object.delete()
                self.run_leaf_middleware(self.get_leaf_object(leaf_id), "update_dislikes", -1)
                return -100
            else:
                return -105

    def get_total_likes(self, leaf_id):
        if self.check_leaf(leaf_id):
            return LeafLikes.objects.filter(leaf_id=leaf_id)
        else:
            return -104

    def get_total_dislikes(self, leaf_id):
        if self.check_leaf(leaf_id):
            return LeafDisLikes.objects.filter(leaf_id=leaf_id)
        else:
            return -104

    def get_total_comments(self, request, leaf_id):
        if self.check_leaf(leaf_id):
            return LeafComments.objects.filter(leaf_id=leaf_id)
        else:
            return -104

    def add_comment(self, request, leaf_id, comment_string):
        if self.is_authorised(request):
            user_object = self.get_logged_in_user(request)
            comment_status = self.check_comment(leaf_id, user_object.user_id)
            print(user_object, comment_status, comment_string)
            if comment_string != None:
                try:
                    if self.check_leaf(leaf_id) and not comment_status["message"]:
                        leaf_comment_object = LeafComments()
                        leaf_comment_object.commented_by = user_object
                        leaf_comment_object.leaf = self.get_leaf_object(leaf_id)
                        leaf_comment_object.comment = comment_string
                        leaf_comment_object.save()
                        self.run_leaf_middleware(self.get_leaf_object(leaf_id), "update_comments", 1)
                        return -100
                except Exception as E:
                    return -103
            else:
                return -106
        else:
            return -101

    def remove_comment(self, request, leaf_id):
        if self.is_authorised(request):
            user_object = self.get_logged_in_user(request)
            comment_status = self.check_comment(leaf_id, user_object.user_id)
            try:
                if self.check_leaf(leaf_id) and comment_status["message"]:
                    comment_object = self.get_comment_object(
                        leaf_id, user_object.user_id
                    )
                    comment_object.delete()
                    self.run_leaf_middleware(self.get_leaf_object(leaf_id), "update_comments", -1)
                    return -100
            except Exception:
                return -105
        pass

    def add_view(self, request, leaf_id):
        if self.is_authorised(request):
            try:
                if self.check_leaf(leaf_id):
                    leaf_object = self.get_leaf_object(leaf_id)
                    self.run_leaf_middleware(leaf_object, "update_view", 1)
                    return -100
            except Exception:
                return -105

    def check_leaf(self, leaf_id):
        leaf_object = Leaf.objects.filter(leaf_id=leaf_id).first()
        return leaf_object is not None

    def check_comment(self, leaf_id, user_id):
        user_object = self.get_user_object(user_id)
        leaf_valid = self.check_leaf(leaf_id)
        response = {}
        if user_object is not None and leaf_valid:
            leaf_object = self.get_leaf_object(leaf_id)
            leaf_comment_object = LeafComments.objects.filter(
                leaf=leaf_object, commented_by=user_object.user_id
            ).first()
            response["status"] = -100
            response["message"] = leaf_comment_object != None
            response["code"] = True
        else:
            response["status"] = -104
            response["code"] = False
            if not leaf_valid:
                response["message"] = "Leaf doesn't exist."
            else:
                response["message"] = "User doesn't exist"
        return response

    def check_like(self, leaf_id, user_id):
        user_object = self.get_user_object(user_id)
        leaf_valid = self.check_leaf(leaf_id)
        response = {}
        if user_object is not None and leaf_valid:
            leaf_object = self.get_leaf_object(leaf_id)
            leaf_like_object = LeafLikes.objects.filter(
                leaf=leaf_object, liked_by=user_object.user_id
            ).first()
            print(leaf_like_object)
            response["status"] = -100
            response["message"] = leaf_like_object != None
            response["code"] = True
        else:
            response["status"] = -100
            response["code"] = False
            if not leaf_valid:
                response["message"] = "Leaf doesn't exist."
            else:
                response["message"] = "User doesn't exist"
        print(response)
        return response

    def check_dislike(self, leaf_id, user_id):
        user_object = self.get_user_object(user_id)
        leaf_valid = self.check_leaf(leaf_id)
        response = {}
        if user_object is not None and leaf_valid:
            leaf_object = self.get_leaf_object(leaf_id)
            leaf_like_object = LeafDisLikes.objects.filter(
                leaf=leaf_object, disliked_by=user_object.user_id
            ).first()
            response["status"] = -100
            response["message"] = leaf_like_object != None
            response["code"] = True
        else:
            response["status"] = -100
            response["code"] = False
            if not leaf_valid:
                response["message"] = "Leaf doesn't exist."
            else:
                response["message"] = "User doesn't exist"
        return response

    def get_leaf_object(self, leaf_id):
        if self.check_leaf(leaf_id):
            return Leaf.objects.filter(leaf_id=leaf_id).first()

    def get_comment_object(self, leaf_id, user_id):
        if self.check_leaf(leaf_id):
            return Leaf.objects.filter(leaf_id=leaf_id)

    def get_like_object(self, leaf_id, user_id):
        leaf_info = self.check_like(leaf_id, user_id)["message"]
        if leaf_info:
            user_object = self.get_user_object(user_id)
            leaf_object = self.get_leaf_object(leaf_id)
            return LeafLikes.objects.filter(leaf=leaf_object, liked_by=user_object)
        else:
            None

    def get_like_object(self, leaf_id, user_id):
        leaf_info = self.check_dislike(leaf_id, user_id)["message"]
        if leaf_info:
            user_object = self.get_user_object(user_id)
            leaf_object = self.get_leaf_object(leaf_id)
            return LeafDisLikes.objects.filter(leaf=leaf_object, disliked_by=user_object)
        else:
            None

    def is_authorised(self, request) -> bool:
        return session_management_object.current_session(
            request
        ) != None and session_management_object.check_session(
            request.session["auth_token"]
        )

    def get_logged_in_user(self, request):
        return session_management_object.get_session_user(request)

    def get_user_object(self, user_id):
        return UserProfile.objects.filter(user_id=user_id).first()

    def run_user_middleware(self, user_object, operation, value):
        user_middleware_object = EdenUserMiddleWare(user_object)
        allowed_operations = ['update_public_leaf', "update_private_leaf",
                              "update_followers", "update_following", "update_user_exp", "update_user_level"]
        if operation not in allowed_operations:
            return False
        else:
            match operation:
                case "update_public_leaf":
                    return user_middleware_object.update_public_leafs_count(value)
                case "update_private_leaf":
                    return user_middleware_object.update_private_leafs_count(value)
                case "update_followers":
                    return user_middleware_object.update_followers(value)
                case "update_following":
                    return user_middleware_object.update_following(value)
                case "update_user_exp":
                    return user_middleware_object.update_user_exp(value)
                case "update_user_level":
                    return user_middleware_object.update_user_level(value)

    def run_leaf_middleware(self, leaf_object, operation, value):
        leaf_middleware_object = EdenLeafMiddleware(leaf_object)
        allowed_operations = ["update_likes", "update_dislikes", "update_comments", "update_views"]
        if operation not in allowed_operations:
            return False
        else:
            match operation:
                case "update_likes":
                    return leaf_middleware_object.update_likes(value)
                case "update_dislikes":
                    return leaf_middleware_object.update_dislikes(value)
                case "update_comments":
                    return leaf_middleware_object.update_comments(value)
                case "update_views":
                    return leaf_middleware_object.update_views(value)
