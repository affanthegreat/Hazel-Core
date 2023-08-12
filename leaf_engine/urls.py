from django.urls import path
from leaf_engine.views import *


urlpatterns = [
    path('create_leaf', create_leaf_view, name="create_leaf"),  # checked
    path('get_user_public_leaves', get_user_public_leaves_view, name="get_user_public_leaves"),  # checked
    path('get_user_private_leaves', get_user_private_leaves_view, name="get_user_private_leaves"),  # checked
    path('delete_leaf', delete_leaf_view, name="delete_leaf"),  # checked
    path('like_leaf', like_leaf_view, name="like_leaf"),  # checked
    path('remove_like', remove_like_view, name="remove_like"),  # checked
    path('add_comment', add_comment_view, name="add_comment"),  # checked
    path('remove_comment', remove_comment_view, name="remove_comment"),  # checked
    path('get_all_likes', get_all_likes, name= "get_all_likes"),  # checked
    path('get_all_comments', get_all_comments, name="get_all_comments"),  # checked
    path('get_all_dislikes', get_all_dislikes, name="get_all_dislikes"), #checked
    path('dislike_leaf', dislike_leaf_view, name= 'dislike_leaf'), #checked
    path('remove_dislike', remove_dislike_view, name= "remove_dislike"), #checked
    path('get_leaves', get_leaves_view, name="get_leaves"), #checked
    path('add_sub_comment',add_sub_comment_view, name="add_sub_comment"), #checked
    path('remove_sub_comment',remove_sub_comment_view, name = "remove_sub_comment"), #checked
    path('add_view',add_leaf_view, name="add_view")
]


