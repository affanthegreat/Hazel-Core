from django.urls import path
from leaf_engine.communicator_views import *

urlpatterns = [
    path('stream_uncategorized_leaves', stream_uncategorized_leaves_view),
    path('stream_leaves_topic_wise',stream_leaves_topic_wise_view),
    path('stream_negative_leaves', stream_negative_leaves_view),
    path('stream_unmarked_comments', stream_unmarked_comments_view),
    path('stream_marked_comments',stream_marked_comments_view),
    path('get_leaf_metrics',get_leaf_metrics_view),
    path('update_batch_leaf_metrics', update_batch_leaf_metrics_view),
]
