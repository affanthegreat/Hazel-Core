from django.urls import path
from user_engine.views import *

urlpatterns = [
    path('create_user', create_user_api),  # checked
    path('validate_data', validate_user_api),  # checked
    path('follow', follow_user_api),  # checked
    path('unfollow', unfollow_user_api),  # checked
    path('get_followers', get_followers),  # checked
    path('get_following', get_following),  # checked
    path('login', login),  # checked
    path('logout', logout),  # checked
    path('current_user', current_user),  # checked
    path('password_reset', password_reset),  # checked
    path('get_user_id',get_user_id)
]
