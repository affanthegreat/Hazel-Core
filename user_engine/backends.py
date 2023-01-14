from django.contrib.auth.backends import ModelBackend

import crypt

from eden_utils.user_management import EdenUserManagement
from user_engine.models import UserProfile

class LoginManagement(EdenUserManagement,ModelBackend):

    def authenticate(self,request, username= None, password= None):
        if UserProfile.objects.filter(user_name= username).exists():
            user_object =  self.get_user_object(username)
            if crypt.crypt(password, user_object.user_password) == user_object.user_password:
                print("password correct")
                return user_object
        return None

    def get_user(self, user_id):
        try:
            return UserProfile.objects.get(user_id=user_id)
        except UserProfile.DoesNotExist:
            return None