from django.urls import path
from exp_engine.views import *


urlpatterns = [
    path('initiate_exp_engine', initiate_exp_engine),
    path('initiate_exp_engine_per_leaf', initiate_exp_engine_per_leaf)
]
