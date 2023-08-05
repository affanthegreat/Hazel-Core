import logging
import json

from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse

from leaf_engine.models import Leaf, LeafComments
from leaf_engine.leaf_management import EdenLeafManagement

class EdenLeafCommunicator():

    def __init__(self):
        self.MAX_OBJECT_LIMIT = 50
        logging.info("Eden Leaf Communicator object created.")

    def stream_uncategorized_leaves(self,args):
        return self.paginator(Leaf.objects.filter(leaf_topic_id=-1),page_number=args['page_number'] if 'page_number' in args else 1)

    def stream_leaves_topic_wise(self,args):
        return self.paginator(Leaf.objects.filter(leaf_topic_id=args['topic_id']),
                              page_number=args['page_number'] if 'page_number' in args else 1)

    def stream_negative_leaves(self,args):
        return self.paginator(Leaf.objects.filter(leaf_sentiment__lt=0,leaf_id=args['leaf_id'] ),
                              page_number=args['page_number'] if 'page_number' in args else 1)

    def stream_unmarked_comments(self, args):
        return self.paginator(LeafComments.objects.filter(comment_sentiment=-9,   leaf_id=args['leaf_id']),
                              page_number=args['page_number'] if 'page_number' in args else 1,
                              )

    def stream_marked_comments(self, args):
        return self.paginator(LeafComments.objects.filter(~Q(comment_sentiment=-9),
                                                          page_number=args['page_number'] if 'page_number' in args else 1 ))

    def send_leaf_metrics(self,leaf_id):
        return Leaf.objects.filter(leaf_id=leaf_id).first()

    def update_batch_leaf_metrics(self, leaf_batch):
        ElM_object = EdenLeafManagement()
        try:
            for item in leaf_batch:
                topic_id = item['topic_id']
                sentiment_value = item['sentiment']
                leaf_id = item['leaf_id']
                if ElM_object.check_leaf(leaf_id):
                    leaf_object = ElM_object.get_leaf_object(leaf_id)
                    leaf_object.leaf_topic_id = topic_id
                    leaf_object.sentiment_value = sentiment_value
                    leaf_object.save()
            return 100
        except Exception:
            return 111


    def paginator(self,query_set,page_number):
        pagination_obj = Paginator(query_set,self.MAX_OBJECT_LIMIT)
        total_pages = pagination_obj.page_range[-1]
        if page_number > total_pages:
            return {
                "message": f"Page number does not exists. (total pages available : {total_pages})"
            }
        try:
            response = {
                'page_number': page_number,
                'total_pages': total_pages,
                'data': list(pagination_obj.page(page_number).object_list.values()),
            }
        except Exception as E:
            response = {
                    "message": "Cannot load page."
                }

        return response
