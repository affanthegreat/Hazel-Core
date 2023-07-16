from django.urls import path
from user_engine.communicator_views import *

urlpatterns = [
    path('stream_users_by_topic', stream_users_by_topics_view),
    path('update_user_topics',update_user_topics)
]
