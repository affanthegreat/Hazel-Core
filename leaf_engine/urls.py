from django.urls import path
from leaf_engine.views import *


urlpatterns = [
    path('create_leaf', create_leaf_view, name="create_leaf"),  
    path('get_user_public_leaves', get_user_public_leaves_view, name="get_user_public_leaves"),  
    path('get_user_private_leaves', get_user_private_leaves_view, name="get_user_private_leaves"),  
    path('delete_leaf', delete_leaf_view, name="delete_leaf"),  
    path('like_leaf', like_leaf_view, name="like_leaf"),  
    path('remove_like', remove_like_view, name="remove_like"),  
    path('add_comment', add_comment_view, name="add_comment"), 
    path('remove_comment', remove_comment_view, name="remove_comment"),  
    path('get_all_likes', get_all_likes, name= "get_all_likes"),  
    path('get_all_comments', get_all_comments, name="get_all_comments"),  
    path('get_all_dislikes', get_all_dislikes, name="get_all_dislikes"),
    path('dislike_leaf', dislike_leaf_view, name= 'dislike_leaf'), 
    path('remove_dislike', remove_dislike_view, name= "remove_dislike"), 
    path('get_leaves', get_leaves_view, name="get_leaves"), 
    path('get_top_comments', get_top_comments,name="get_top_leaves"),
    path('add_sub_comment',add_sub_comment_view, name="add_sub_comment"), 
    path('remove_sub_comment',remove_sub_comment_view, name = "remove_sub_comment"), 
    path('add_view',add_leaf_view, name="add_view"),
    path("check_like", check_like, name="check_like"),
    path("check_dislike", check_dislike, name="check_like"),
    path("delete_comment_by_id", delete_comment_by_id, name="delete_comment_by_id"),
    path("vote_comment", vote_comment, name="vote_comment"),
    path("get_vote", get_vote, name='get_vote'),
    path("remove_vote_comment", remove_vote_comment, name="remove_vote_comment")
]


