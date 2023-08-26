import crypt
import json
import logging
from datetime import datetime

from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse

from user_engine.middleware import EdenUserMiddleWare
from user_engine.models import *

import re



class EdenUserManagement:
    def __init__(self) -> None:
        self.MAX_OBJECT_LIMIT = 50
    
    
    def is_valid_email(self,email):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None
    

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
        if len(user_password) < 6:
            return {"status": False, "issue": "Password too short"}
        if not self.is_valid_email(user_email):
            return{"status": False, "issue": "Not a valid email"}
       

        verification_data = {
            "user_email": user_email,
            "user_name": user_name,
        }
        if self.check_user_exists(verification_data):
            response = {"status": False, "issue": "User already exists"}
            return response
        else:
            user_profile_object = UserProfile()
            user_profile_object.user_email = user_email
            user_profile_object.user_password = self.make_password(user_password)
            user_profile_object.user_name = user_name
            try:
                user_profile_object.save()
                response = {"status": True, "issue": "Success"}
            except Exception:
                response = {"status": False, "issue": "object creation failed"}
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
                try:
                    follower_relationship.save()
                    self.run_user_middleware(following_object, "update_followers", 1)
                    self.run_user_middleware(follower_object, "update_following", 1)
                    print("USER SUCCESSFULLY FOLLOWED")
                    return 100
                except Exception as E:
                    return 102
            else:
                return 99
        else:
            return -111

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
                self.run_user_middleware(following_object, "update_followers", -1)
                self.run_user_middleware(follower_object, "update_following", -1)
                return {"status": 200, "message": f"{follower_object.user_name} successfully unfollowed {following_object.user_name}"}
            else:
                return {"status": 200, "message": f"{follower_object.user_name} doesn't follow {following_object.user_name}"}
        else:
            response = {"status": 200, "message": "One of the user does not exists."}
            return response


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
                ).order_by("-created_at").all()
            else:
                followers_query_set = UserFollowing.objects.filter(
                    master=user_profile, slave=sub_user
                ).order_by("-created_at").all()
            qs = UserProfile.objects.filter(user_id__in = followers_query_set.values('slave')).order_by("-created_at").all()
            response = self.paginator(qs,page_number)
            return response
        else:
            return {'message': "User doesn't exist."}

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
            following_query_set = UserProfile.objects.filter(user_id__in = UserFollowing.objects.filter(slave=user_profile).values('master')).order_by("-created_at").all()
            response = self.paginator(following_query_set,page_number)
            return response

    def check_follow(self, user_id, search_profile_id):
        user_1, user_2 = self.get_user_object(search_profile_id), self.get_user_object(user_id)
        follow_request_status = self.check_follow_request(user_2, user_1)
        following_status = self.check_following(user_2, user_1)
        follower_status = self.check_following(user_1, user_2)
        block_status = self.check_block_status(user_2,user_1)
        blocked_by_status =  self.check_block_status(user_1,user_2)
        return {
            'follow_request_status': follow_request_status,
            'following_status': following_status,
            'follower_status' :follower_status,
            'block_status': block_status,
            'blocked_by_status': blocked_by_status
        }

    
    def check_block_status(self, blocker, blocked):
        return UserBlockedAccounts.objects.filter(blocker_profile= blocker, blocked_profile=blocked).exists()


    def check_follow_request(self, user_1, user_2):
        return UserFollowRequests.objects.filter(requester= user_1, requested_to = user_2).exists()

    def password_reset(self, data) -> bool:
        """
            Resets the password of a user.

            Args:
                data (dict): A dictionary containing the user data.
                    - user_id (int): The ID of the user.
                    - user_password (str): User current password.
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

    def generate_id(self):

        session_id = str(uuid.uuid4()).upper().replace("-", "")
        return session_id
    
    def add_user_details(self, data):
        user_id = data['user_id']
        if self.get_user_object(user_id):
            user_detail_object = self.get_user_detail_object(user_id)
            if user_detail_object:
                user_detail_object.user_full_name = data['user_full_name'] if 'user_full_name' in data else user_detail_object.user_full_name
                user_detail_object.user_phone_number = data['user_phone_number'] if 'user_phone_number' in data else user_detail_object.user_phone_number
                user_detail_object.user_address = data['user_address'] if 'user_address' in data else user_detail_object.user_address
                user_detail_object.user_city = data['user_city'] if 'user_city' in data else user_detail_object.user_city
                user_detail_object.user_country = data['user_country'] if 'user_country' in data else user_detail_object.user_country
                user_detail_object.user_region = data['user_region'] if 'user_region' in data else user_detail_object.user_region
                user_detail_object.user_state = data['user_state'] if 'user_state' in data else user_detail_object.user_state
                user_detail_object.user_gender = data['user_gender'] if 'user_gender' in data else user_detail_object.user_gender
                user_detail_object.user_age = data['user_age'] if 'user_age' in data else user_detail_object.user_age
                user_detail_object.user_bio = data['user_bio'] if 'user_bio' in data else user_detail_object.user_bio
            else:
                user_detail_object = UserDetails()
                user_detail_object.user_id = self.get_user_object(user_id)
                user_detail_object.user_full_name = data['user_full_name']
                user_detail_object.user_phone_number = data['user_phone_number']
                user_detail_object.user_address = data['user_address']
                user_detail_object.user_city = data['user_city']
                user_detail_object.user_country = data['user_country']
                user_detail_object.user_phone_id =  self.generate_id()
                user_detail_object.user_region = data['user_region']
                user_detail_object.user_gender = data['user_gender']
                user_detail_object.user_state = data['user_state']
                user_detail_object.user_age = data['user_age']
                user_detail_object.user_bio = data['user_bio']
            try:
                user_detail_object.save()
                return 100
            except Exception as e:
                return -105
        else:
            raise Exception()
            return -103
        
    def add_user_blocked(self,data):
        try:
            blocked = data['blocked']
            user_object = self.get_user_object(data['user_id'])
            if not self.check_user_blocked_status(blocked, user_object):
                user_block_obj = UserBlockedAccounts()
                user_block_obj.blocker_profile = user_object
                user_block_obj.blocked_profile = self.get_user_object(blocked)
                user_block_obj.save()
                blocker = user_object
                blocked_user_object = self.get_user_object(blocked)
                qs_1 = UserFollowing.objects.filter(master= blocker, slave=blocked_user_object)
                qs_2 = UserFollowing.objects.filter(master= blocked_user_object, slave=blocker)
                qs_3 = UserFollowRequests.objects.filter(requester = blocker, requested_to = blocked_user_object)
                qs_4 = UserFollowRequests.objects.filter(requested_to = blocker, requester = blocked_user_object)
                if qs_1.exists():
                    print("qs_1")
                    qs_1.delete()
                    self.run_user_middleware(blocker, "update_followers", -1)
                    self.run_user_middleware(blocked_user_object, "update_following", -1)
                if qs_2.exists():
                    print("qs_2")
                    qs_2.delete()
                    self.run_user_middleware(blocked_user_object, "update_followers", -1)
                    self.run_user_middleware(blocker, "update_following", -1)
                if qs_3.exists():
                    print("qs_3")
                    qs_3.delete()
                if qs_4.exists():
                    print("qs_4")
                    qs_4.delete()

                print("blocked.")
                return 100
            else:
                print("already blocked.")
                return 102
        except:
            return -111
            
            
    def check_user_blocked_status(self, blocked, blocked_by):
        return UserBlockedAccounts.objects.filter(blocker_profile = blocked_by,
                                                  blocked_profile__user_id = blocked).exists()
    
    def unblock_user(self, data):
        try:
            blocked = data['blocked']
            blocker = self.get_user_object(data['user_id'])
            if self.check_user_blocked_status(blocked, blocker):
                blocked_user_object = self.get_user_object(blocked)
                user_block_obj = self.get_user_block_object(blocked_user_object, blocker)
                user_block_obj.delete()
                return 100
            else:
                return 102
        except Exception as e:
            return -111
    
    def fetch_all_block_objects(self, data):
        if self.check_user_exists(data):
            user_obj = self.get_user_object(data['user_id'])
            qs = UserProfile.objects.filter(user_id__in = UserBlockedAccounts.objects.filter(blocker_profile= user_obj).values('blocked_profile')).all()
            return self.paginator(qs,data['page_number'])
        
    def get_user_block_object(self,blocked, blocker):
        return UserBlockedAccounts.objects.filter(blocker_profile = blocker, blocked_profile= blocked).first()
    
    def get_user_detail_object(self, user_id):
        return  UserDetails.objects.filter(user_id= user_id).first()
        
    def create_follow_request(self,data):
        requester = data['requester']
        requested_to = data['requested_to']
        if self.check_user_exists({'user_id': requested_to}) and self.check_user_exists({'user_id': requester}):
            follow_request = UserFollowRequests()
            user_1 = self.get_user_object(requester)
            user_2 = self.get_user_object(requested_to)
            if not self.check_follow_request(user_1,user_2):
                follow_request.requester = user_1
                follow_request.requested_to = user_2
                follow_request.save()
                return 100
            else:
                return 112
            
        else:
            print(self.check_user_exists({'user_id': requested_to}))
            print(self.check_user_exists({'user_id': requester}))
            return 102
        
    def remove_follow_request(self, data):
        requester = data['requester']
        requested_to = data['requested_to']
        if self.check_user_exists({'user_id': requested_to}) and self.check_user_exists({'user_id': requester}):
            requester = self.get_user_object(requester)
            requested_to = self.get_user_object(requested_to)
            print(requester.user_name)
            print(requested_to.user_name)
            UserFollowRequests.objects.filter(requested_to=requested_to, requester=requester).first().delete()
            print(UserFollowRequests.objects.all().count())
            return 100
        else:
            print(self.check_user_exists({'user_id': requested_to}))
            print(self.check_user_exists({'user_id': requester}))
            return 102
    
    def deny_follow_request(self, data):
        requester = data['requester']
        requested_to = data['requested_to']
        if self.check_user_exists({'user_id': requested_to}) and self.check_user_exists({'user_id': requester}):
            requester = self.get_user_object(requester)
            requested_to = self.get_user_object(requested_to)
            print(requester.user_name)
            print(requested_to.user_name)
            UserFollowRequests.objects.filter(requested_to=requested_to, requester=requester).first().delete()
            print(UserFollowRequests.objects.all().count())
            return 100
        else:
            print(self.check_user_exists({'user_id': requested_to}))
            print(self.check_user_exists({'user_id': requester}))
            return 102
    
    def fetch_all_follow_requests(self,data):
        requested_to = data['user_id']
        page_number = data['page_number']
        if self.check_user_exists({'user_id': requested_to}):
            requested_to = self.get_user_object(requested_to)
            queryset = UserProfile.objects.filter(user_id__in= UserFollowRequests.objects.filter(requested_to = requested_to).values('requester')).all()
            return self.paginator(queryset,page_number)
        else:
            return 101


    def accept_follow_request(self,data):
        if  self.check_user_exists({'user_id': data['user_id']}) and data['current_user'] is not None :
            requester = self.get_user_object(data['user_id'])
            requested_to =  data['current_user']
            data = {
                'follower' : data['user_id'],
                'follows' : data['current_user'].user_id
            }
            follow_status = self.user_follow(data)
            if follow_status == 100 or follow_status == 99:
                UserFollowRequests.objects.filter(requested_to=requested_to, requester=requester).first().delete()
            else:
                return 99
        else:
            return 191
    
            
    def fetch_follow_request_obj(self,request_id):
        return UserFollowRequests.objects.filter(id= request_id).first()
    

    def user_obj_to_json(self, user_obj):
        return {
            'user_id': user_obj.user_id,
            'user_email': user_obj.user_email,
            'user_name': user_obj.user_name,
            'user_public_leaf_count': user_obj.user_public_leaf_count,
            'user_private_leaf_count': user_obj.user_private_leaf_count,
            'user_experience_points': user_obj.user_experience_points,
            'user_verified': user_obj.user_verified,
            'user_followers': user_obj.user_followers,
            'user_following': user_obj.user_following,
            'user_level': user_obj.user_level,
            'user_universal_likes': user_obj.user_universal_likes,
            'user_universal_dislikes': user_obj.user_universal_dislikes,
            'user_universal_comments': user_obj.user_universal_comments,
            'created_at': str(user_obj.created_at)
        }


    def user_details_to_json(self, user_detail_obj):
        return {
                'user_id':user_detail_obj.user_id.user_id,
                "user_full_name": user_detail_obj.user_full_name, 
                "user_phone_number": user_detail_obj.user_phone_number,
                "user_address":user_detail_obj.user_address, 
                "user_phone_id":user_detail_obj.user_phone_id,
                "user_city": user_detail_obj.user_city,
                'user_state': user_detail_obj.user_state,
                'user_country': user_detail_obj.user_country,
                'user_region': user_detail_obj.user_region,
                "user_gender": user_detail_obj.user_gender,
                "user_age": user_detail_obj.user_age,
                'user_bio': user_detail_obj.user_bio
                }
    
    def get_user_info(self,data):
        user_id = self.get_user_id(data)
        user_obj = self.get_user_object(user_id)
        user_detail_obj = self.get_user_detail_object(user_id)
        map1 = self.user_obj_to_json(user_obj)
        if(user_detail_obj is not None):
            print("detail object found")
            map2 = self.user_details_to_json(user_detail_obj)
            result =  map1.update(map2)
            return map1
        print(UserDetails.objects.filter(user_id= user_obj).first())
        print("Detail object is not none")
        return map1


    def get_user_info_id(self,data):
        try:
            user_id = data['user_id']
            user_obj = self.get_user_object(user_id)
            user_detail_obj = self.get_user_detail_object(user_id)
            map1 = self.user_obj_to_json(user_obj)
            map2 = self.user_details_to_json(user_detail_obj)
            result =  map1.update(map2)
            return map1
        except Exception as e:
            return 101


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
        if self.check_user_exists(data):
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
    
    def get_searched_users(self, user_name, page_number):
        return self.paginator(UserProfile.objects.filter(user_name__contains = user_name).defer('created_at', 'previous_experience_generation_date').order_by('-user_experience_points'), page_number)
    
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
            data = []
            for obj in  list(pagination_obj.page(page_number).object_list):
                user_id = obj.user_id
                user_detail_obj = self.get_user_detail_object(user_id)
                map1 = self.user_obj_to_json(obj)
                map2 = self.user_details_to_json(user_detail_obj)
                result = map1.update(map2)
                data.append(map1)

            response = {
                'page_number': page_number,
                'total_pages': total_pages,
                'data': data,
            }
        except Exception as E:
            response = {
                    "message": "Cannot load page."
                }

        return response
