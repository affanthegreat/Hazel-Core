from django.urls import path
from leaf_engine.views import *


urlpatterns = [
    path('create_leaf', create_leaf_view),  # checked
    path('get_user_public_leaves', get_user_public_leaves_view),  # checked
    path('get_user_private_leaves', get_user_private_leaves_view),  # checked
    path('delete_leaf', delete_leaf_view),  # checked
    path('like_leaf', like_leaf_view),  # checked
    path('remove_like', remove_like_view),  # checked
    path('add_comment', add_comment_view),  # checked
    path('remove_comment', remove_comment_view),  # checked
    path('get_all_likes', get_all_likes),  # checked
    path('get_all_comments', get_all_comments),  # checked
    path('get_all_dislikes', get_all_dislikes),
    path('dislike_leaf', dislike_leaf_view),
    path('remove_dislike', remove_dislike_view),
    path('get_leaves', get_leaves_view),
    path('add_sub_comment',add_sub_comment_view)
]

# TODO implement dislike views
