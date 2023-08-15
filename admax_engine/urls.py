from django.urls import path
from admax_engine.views import *


urlpatterns = [
    path('create_advertisement_campaign',create_advertisement_campaign, name="create_advertisement_campaign" ),
    path('create_advertisement_instance',create_advertisement_instance, name="create_advertisement_instance" ),
    path('delete_ad',delete_ad, name="delete_ad" ),
    path('delete_campaign',delete_campaign, name="delete_campaign" ),
    path('get_ad_analytics',get_ad_analytics, name="get_ad_analytics" ),
    path('get_campaign_summary',get_campaign_summary, name="get_campaign_summary" ),
    path('create_promoted_leaf',create_promoted_leaf, name="create_promoted_leaf" ),
    path('make_leaf_into_promoted_leaf',make_leaf_into_promoted_leaf, name="make_leaf_into_promoted_leaf"),
    path('remove_promoted_leaf',remove_promoted_leaf, name="remove_promoted_leaf" ),
    path('get_campaign_id', get_campaign_id, name="get_campaign_id")
]
