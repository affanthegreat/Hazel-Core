from django.urls import path
from user_engine.views import *

urlpatterns = [
    path('create_user', create_user_api, name='create_user'),  # checked
    path('validate_data', validate_user_api, name='validate_data'),  # checked
    path('follow', follow_user_api, name='follow'),  # checked
    path('unfollow', unfollow_user_api, name= 'unfollow'),  # checked
    path('get_followers', get_followers, name= 'get_followers'),  # checked
    path('get_following', get_following, name= 'get_following'),  # checked
    path('login', login, name = 'login'),  # checked
    path('logout', logout, name = 'logout'),  # checked
    path('current_user', current_user,name = 'current_user'),  # checked
    path('password_reset', password_reset, name = 'password_reset'),  # checked
    path('get_user_id',get_user_id, name = 'get_user_id'), #checked
    path('get_user_details',get_user_details, name='get_user_details'), 
    path('modify_user_details',modify_user_details, name = 'modify_user_details'),
    path('block_user',block_user, name='block_user'),
    path('unblock_user', unblock_user, name='unblock_user'),
    path('add_user_private_relation', add_user_private_relation, name='add_user_private_relation'),
    path('remove_user_private_relation', remove_user_private_relation, name= 'remove_user_private_relation'),
    path('make_follow_request_view', make_follow_request_view, name='make_follow_request_view'),
    path('remove_follow_request_view', remove_follow_request_view, name='remove_follow_request_view'),
    path('fetch_all_follow_request_view',fetch_all_follow_request_view,name='fetch_all_follow_request_view'),
    path('accept_follow_request',accept_follow_request,name='accept_follow_request'),
    path('delete_follow_request',delete_follow_request, name='delete_follow_request')
]
