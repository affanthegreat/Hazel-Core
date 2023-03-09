from django.contrib.auth.backends import ModelBackend

import crypt
import uuid

from .user_management import EdenUserManagement
from user_engine.models import UserAccessToken, UserProfile


class EdenLoginManagement(EdenUserManagement, ModelBackend):

    def authenticate(self, request, username=None, password=None):
        if UserProfile.objects.filter(user_name=username).exists():
            print("here")
            user_object = self.get_user(username)
            if crypt.crypt(password, user_object.user_password) == user_object.user_password:
                print("password correct")
                return user_object
        return None

    def get_user(self, user_name):
        try:
            return UserProfile.objects.get(user_name=user_name)
        except UserProfile.DoesNotExist:
            return None


class EdenSessionManagement():

    def __init__(self) -> None:
        pass

    def generate_session_id(self):
        session_id = str(uuid.uuid4()).upper().replace("-", "")
        return session_id

    def create_session(self, request, user):
        token = request.session.get('token', None)
        auth_token = request.session.get('auth_token', None)
        if not self.check_session(auth_token):
            session_id = self.generate_session_id()
            encrypted = self.encrypt_session_id(session_id, user.user_password)
            access_token_object = UserAccessToken()
            access_token_object.user_session_id = session_id
            access_token_object.user = user
            access_token_object.save()
            request.session["token"] = encrypted
            request.session["auth_token"] = session_id

    def delete_session(self, request):
        token = request.session.get('token', None)
        auth_token = request.session.get('auth_token', None)
        if self.check_session(auth_token):
            auth_object = self.get_session_object(auth_token)
            auth_object.delete()

    def encrypt_session_id(self, session_id, key):
        return crypt.crypt(session_id, key)

    def get_session_user(self, request):
        token = request.session.get('token', None)
        auth_token = request.session.get('auth_token', None)
        print(token, auth_token)
        try:
            rehashed_cipher = crypt.crypt(auth_token, token)
            if token == rehashed_cipher and self.check_session(auth_token):
                return self.get_session_object(auth_token).user
        except Exception as E:
            pass

    def check_session(self, auth_token):
        return UserAccessToken.objects.filter(user_session_id=auth_token).exists()

    def get_session_object(self, auth_token):
        return UserAccessToken.objects.filter(user_session_id=auth_token).first()

    def current_session(self, request):
        if request.session.get('token', None) and request.session.get('auth_token', None):
            return request.session['auth_token']
