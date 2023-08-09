from django.urls import path
from user_engine.communicator_views import *

urlpatterns = [
    path('update_user_topics',update_user_topics)
]
