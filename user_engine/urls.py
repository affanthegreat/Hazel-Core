from django.urls import path
from user_engine.views import *

urlpatterns = [
    path('create_user', create_user_api),
    path('validate_data', validate_user_api),
    path('follow', follow_user_api),
    path('get_followers', get_followers),
    path('get_following', get_following),
    path('login', login),
    path('logout', logout),
    path('current_user', current_user),
    path('password_reset', password_reset)
]
