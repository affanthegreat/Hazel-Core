import crypt
import json
import logging

from django.core.paginator import Paginator
from django.http import JsonResponse

from user_engine.backends import EdenSessionManagement
from user_engine.middleware import EdenUserMiddleWare
from user_engine.models import *


session_management_object = EdenSessionManagement()
class EdenUserManagement:
    def __init__(self) -> None:
        self.MAX_OBJECT_LIMIT = 50

    def make_password(self, txt) -> str:
        """
            Generates a password hash from the given text.

            Args:
                txt (str): The text to be hashed.

            Returns:
                str: The password hash generated from the input text.
            """
        return crypt.crypt(txt)

    def create_user(self, data):
        """
         Creates a new user profile with the provided data.

         Args:
             data (dict): A dictionary containing the user data.
                 - user_name (str): The name of the user.
                 - user_email (str): The email address of the user.
                 - user_password (str): The password of the user.

         Returns:
             dict: A dictionary containing the status of the operation.
                 - status (bool): True if the user was successfully created, False otherwise.
                 - issue (str): A message describing the outcome of the operation.
         """
        user_name = data["user_name"]
        user_email = data["user_email"]
        user_password = data["user_password"]
        user_public_leaf_count = 0
        user_private_leaf_count = 0
        user_experience_points = 0
        user_verified = False
        user_followers = 0
        user_following = 0
        user_level = 0

        verification_data = {
            "user_email": user_email,
            "user_name": user_name,
        }
        if self.check_user_exists(verification_data):
            response = {"status": False, "issue": "User already exists."}
            return response
        else:
            user_profile_object = UserProfile()
            user_profile_object.user_email = user_email
            user_profile_object.user_private_leaf_count = user_private_leaf_count
            user_profile_object.user_public_leaf_count = user_public_leaf_count
            user_profile_object.user_experience_points = user_experience_points
            user_profile_object.user_verified = user_verified
            user_profile_object.user_password = self.make_password(user_password)
            user_profile_object.user_name = user_name
            user_profile_object.user_followers = user_followers
            user_profile_object.user_following = user_following
            user_profile_object.user_level = user_level
            try:
                user_profile_object.save()
                response = {"status": True, "issue": "Success."}
            except Exception:
                response = {"status": False, "issue": "object creation failed."}
            return response

    def check_user_exists(self, data) -> bool:
        """
        Checks if a user with the given name or email already exists.

        Args:
            data (dict): A dictionary containing the user data.
                - user_name (str, optional): The name of the user.
                - user_email (str, optional): The email address of the user.

        Returns:
            bool: True if a user with the provided name or email exists, False otherwise.
        """
        user_name = data.get("user_name", None)
        user_email = data.get("user_email", None)
        user_id = data.get("user_id", None)
        logging.info(str((user_name,user_email,user_id)))
        if (UserProfile.objects.filter(user_name=user_name).exists()
            or UserProfile.objects.filter(user_email=user_email).exists()
            or UserProfile.objects.filter(user_id=user_id).exists()
        ):
            return True
        return False

    def validate_user(self, data) -> bool:
        """
           Validates a user's password against the stored password hash.

           Args:
               data (dict): A dictionary containing the user data.
                   - user_password (str): The password to be validated.
                   - user_id (int): The ID of the user.

           Returns:
               bool: True if the password is valid, False otherwise.
           """
        user_password = data["user_password"]
        user_id = data['user_id']
        is_valid = False
        if self.check_user_exists({"user_id": user_id}):
            user_object = self.get_user_object(user_id)
            is_valid = crypt.crypt(user_password, user_object.user_password) == user_object.user_password
        return is_valid

    def retrieve_user_password(self, data):
        """
           Retrieves the password of a user based on the provided data.

           Args:
               data (dict): A dictionary containing the user data.
                   - user_id (int): The ID of the user.

           Returns:
               str or None: The password of the user if the user exists, None otherwise.
           """
        if self.check_user_exists(data):
            user_id = data["user_id"]
            user_object = UserProfile.objects.filter(user_id=user_id).all()
            return list(user_object)[0].user_password
        else:
            return None

    def user_follow(self, data):
        """
          Adds a follower for a user.

          Args:
              data (dict): A dictionary containing the follower and follows data.
                  - follower (int): The ID of the follower user.
                  - follows (int): The ID of the user being followed.

          Returns:
              dict: A dictionary containing the status and message of the operation.
                  - status (int): The HTTP status code of the operation.
                  - message (str): A message describing the outcome of the operation.
          """
        follower = data["follower"]
        follows = data["follows"]
        if self.check_user_exists({"user_id": follower}) and self.check_user_exists(
            {"user_id": follows}
        ):
            follower_relationship = UserFollowing()
            follower_object = self.get_user_object(follower)
            following_object = self.get_user_object(follows)
            if not self.check_follower(following_object, follower_object):
                follower_relationship.slave = follower_object
                follower_relationship.master = following_object
                print(follower_object, follower_object)
                try:
                    follower_relationship.save()
                    self.run_user_middleware(following_object, "update_followers", 1)
                    response = {
                        "status": 200,
                        "message": f"{follower} added as follower added to {follows}",
                    }
                except Exception as E:
                    print(E)
                    response = {"status": 200, "message": "Error while adding the follower"}
                print(response)
                return response
            else:
                response = {
                    "status": 200,
                    "message": f"{follower_object} already follows {following_object}",
                }
                return response
        else:
            print(self.check_user_exists({"user_id": follower}))
            print(self.check_user_exists({"user_id": follows}))
            response = {"status": 200, "message": "One of the user does not exists."}
            return response

    def check_follower(self, following_object, follower_object):
        """
        Checks if a user is already following another user.

        Args:
            following_object: The user being followed.
            follower_object: The user who wants to follow.

        Returns:
            bool: True if the follower is already following the user, False otherwise.
        """
        return UserFollowing.objects.filter(master=following_object, slave=follower_object).exists()

    def check_following(self, following_object, follower_object):
        """
        Checks if a user is already followed by another user.

        Args:
            following_object: The user being followed.
            follower_object: The user who wants to follow.

        Returns:
            bool: True if the follower is already following the user, False otherwise.
        """
        return UserFollowing.objects.filter(slave=following_object, master=follower_object).exists()

    def user_unfollow(self, data):
        """
         Allows a user to unfollow another user.

         Args:
             data (dict): A dictionary containing the user data.
                 - follower (int): The ID of the user who wants to unfollow.
                 - follows (int): The ID of the user being unfollowed.

         Returns:
             dict: A dictionary containing the status of the operation.
                 - status (int): The status code indicating the result of the operation.
                 - message (str): A message describing the outcome.
         """
        follower = data["follower"]
        follows = data["follows"]
        if self.check_user_exists({"user_id": follower}) and self.check_user_exists(
            {"user_id": follows}
        ):
            follower_object = self.get_user_object(follower)
            following_object = self.get_user_object(follows)
            if self.check_follower(following_object, follower_object):
                UserFollowing.objects.filter(master=following_object, slave=follower_object).first().delete()
                return {"status": 200, "message": f"{follower_object} successfully unfollowed {following_object}."}
            else:
                return {"status": 200, "message": f"{follower_object} doesn't follow {following_object}."}

    def get_user_followers(self, data):
        """
           Retrieves the followers of a user.

           Args:
               data (dict): A dictionary containing the user data.
                   - user_id (int): The ID of the user.
                   - sub_user (int, optional): The ID of the sub-user. Defaults to None.

           Returns:
               list or dict: A list of dictionaries containing the follower information if the user exists,
                   or a dictionary with an error message if the user doesn't exist.
                   Each dictionary in the list represents a follower and contains relevant information.
          """
        user_profile = data["user_id"]
        page_number = data['page_number'] if 'page_number' in data else 1
        sub_user = data.get('sub_user', None)
        if self.check_user_exists(data):
            if sub_user == None:
                followers_query_set = UserFollowing.objects.filter(
                    master=user_profile
                ).order_by("created_at").all()
            else:
                followers_query_set = UserFollowing.objects.filter(
                    master=user_profile, slave=sub_user
                ).order_by("created_at").all()
            response = self.paginator(followers_query_set,page_number)
            return response
        else:
            return {"User doesn't exist."}

    def get_user_following(self, data):
        """
           Retrieves the users that a given user is following.

           Args:
               data (dict): A dictionary containing the user data.
                   - user_id (int): The ID of the user.

           Returns:
               list: A list of dictionaries containing the following user information.
        """
        user_profile = data["user_id"]
        page_number = data['page_number'] if 'page_number' in data else 1
        if self.check_user_exists(data):
            following_query_set = UserFollowing.objects.filter(slave=user_profile).order_by("created_at").all()
            response = self.paginator(following_query_set,page_number)
            return response

    def password_reset(self, data) -> bool:
        """
            Resets the password of a user.

            Args:
                data (dict): A dictionary containing the user data.
                    - user_id (int): The ID of the user.
                    - user_password1 (str): The new password.
                    - user_password2 (str): The confirmation of the new password.

            Returns:
                dict: A dictionary containing the status of the operation.
                    - status (int): The status code indicating the result of the operation.
                    - message (str): A message describing the outcome.
            """
        user_id = data['user_id']
        user_password1 = data['user_password1']
        user_password2 = data['user_password2']
        response = {}
        if self.check_user_exists(data):
            response['status'] = 200
            if self.validate_user(data):
                user_object = self.get_user_object(user_id)
                if user_password1 == user_password2:
                    new_pass = self.make_password(user_password1)
                    user_object.user_password = new_pass
                    user_object.save()
                    response['message'] = "Password changed sucessfully"
                else:
                    response['message'] = "New passwords does not match"
            else:
                response['message'] = "Invalid current password"
        else:
            response['message'] = "User doesn't exist"
        return response


    def add_user_details(self, data):
        user_id = data['user_id']
        if self.get_user_object(user_id):
            user_detail_object = self.get_user_detail_object(user_id)
            if user_detail_object:
                user_detail_object.user_full_name = data['user_full_name'] if 'user_full_name' in data else user_detail_object.user_full_name
                user_detail_object.user_phone_number = data['user_phone_number'] if 'user_phone_number' in data else user_detail_object.user_phone_number
                user_detail_object.user_address = data['user_address'] if 'user_address' in data else user_detail_object.user_address
                user_detail_object.user_phone_id = data['user_phone_id'] if 'user_phone_id' in data else user_detail_object.user_phone_id
            else:
                user_detail_object = UserDetails()
                user_detail_object.user_id = self.get_user_object(user_id)
                user_detail_object.user_full_name = data['user_full_name']
                user_detail_object.user_phone_number = data['user_phone_number']
                user_detail_object.user_address = data['user_address']
                user_detail_object.user_phone_id = data['user_phone_id']
            try:
                user_detail_object.save()
                return 100
            except:
                return -105
        else:
            return -103
        
    def add_user_blocked(self,request,data):
        blocked = data['blocked']
        if self.is_authorised(request):
            user_object = self.get_logged_in_user(request)
            if not self.check_user_blocked_status(blocked, user_object):
                user_block_obj = UserBlockedAccounts()
                user_block_obj.blocker_profile = user_object
                user_block_obj.blocked_profile = self.get_user_object(blocked)
                user_block_obj.save()
                return 100
            else:
                return 102
        else:
            return -111
            
            
    def check_user_blocked_status(self, blocked, blocked_by):
        return UserBlockedAccounts.objects.filter(blocker_profile = blocked_by,
                                                  blocked_profile__user_id = blocked).exists()
    
    def unblock_user(self,request, data):
        blocked = data['blocked']
        if self.is_authorised(request):
            user_object = self.get_logged_in_user(request)
            if self.check_user_blocked_status(blocked, user_object):
                blocked_user_object = self.get_user_block_object(blocked)
                user_block_obj = self.get_user_block_object(blocked_user_object, user_block_obj)
                user_block_obj.delete()
                return 100
            else:
                return 102
        else:
            return -111
        
    def get_user_block_object(self,blocked, blocked_by):
        return UserBlockedAccounts.objects.filter(blocker_profile = blocked_by, blocked_profile= blocked).first()
    
    def get_user_detail_object(self, user_id):
        return  UserDetails.objects.filter(user_id= user_id).first()

    def get_user_id(self,data):
        """
           Retrieves the ID of a user based on the provided username.

           Args:
               data (dict): A dictionary containing the user data.
                   - user_name (str): The username of the user.

           Returns:
               int: The ID of the user, or None if the user doesn't exist.
           """
        user_name = data['user_name']
        user_obj = UserProfile.objects.filter(user_name=user_name).first()
        return user_obj.user_id

    def get_user_object(self, user_id):
        """
           Retrieves the user object based on the provided user ID.

           Args:
               user_id (int): The ID of the user.

           Returns:
               UserProfile or None: The user object if the user exists, or None otherwise.
           """
        return UserProfile.objects.filter(user_id=user_id).first()

    def is_authorised(self, request) -> bool:
        """Check if the given request is authorized.

        Args:
            request (HttpRequest): The HTTP request to check.

        Returns:
            bool: True if the request is authorized, False otherwise.
        """
        return session_management_object.current_session(
            request
        ) != None and session_management_object.check_session(
            request.session["auth_token"]
        )

    def get_logged_in_user(self, request):
        """Return the logged in user for the given request.

        Args:
            request (HttpRequest): The HTTP request to get the logged in user for.

        Returns:
            User or None: The logged in user for the given request, or None if no user is logged in.
        """
        return session_management_object.get_session_user(request)
    
    def run_user_middleware(self, user_object, operation, value):
        """
          Runs a middleware operation on a user object.

          Args:
              user_object (UserProfile): The user object on which the middleware operation is performed.
              operation (str): The operation to be performed.
              value: The value associated with the operation.

          Returns:
              bool or None: The result of the middleware operation if the operation is valid, or None otherwise.
          """
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
