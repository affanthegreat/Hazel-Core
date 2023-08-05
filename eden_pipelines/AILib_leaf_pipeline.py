import logging
import requests
import json

class HazelAI_Leaf_Pipeline():
    def meta(self):
        self.VERSION = 0.1
        self.HAZEL_AI_SERVER = "http://127.0.0.1"
        self.HAZEL_AI_PORT = "7000"
        self.HAZEL_AI_ADDRESS = self.HAZEL_AI_SERVER + ":" + self.HAZEL_AI_PORT + "/conx_engine/"


    def __init__(self) -> None:
        self.meta()
    
    def make_POST_request(self,api_endpoint,body):
        return requests.post(api_endpoint,json=body)

    def leaf_to_json(self, leaf_object):
        return {
            'created_date': str(leaf_object.created_date),
            'owner': str(leaf_object.owner.user_id),
            'leaf_id': str(leaf_object.leaf_id),
            'text_content':leaf_object.text_content,
            'image_content': str(leaf_object.image_content),
            'likes_count': str(leaf_object.likes_count),
            'dislikes_count': str(leaf_object.dislikes_count),
            'comment_count': str(leaf_object.comments_count),
            'view_count': str(leaf_object.view_count),
            'leaf_type': str(leaf_object.leaf_type),
            'engagement_rating': leaf_object.engagement_rating,
            'experience_rating': leaf_object.experience_rating,
            'previous_analytics_run': str(leaf_object.previous_analytics_run),
            'leaf_topic_id': leaf_object.leaf_topic_id,
            'leaf_sentiment': leaf_object.leaf_sentiment
        }
    
    def comment_to_json(self, comment_object):
        return {
            'comment_id': comment_object.comment_id,
            'commented_by': comment_object.commented_by.user_id,
            'comment': comment_object.comment,
            'comment_depth' : comment_object.comment_depth,
            'comment_sentiment': comment_object.comment_sentiment,
            'root_comment': comment_object.root_comment,
            'parent_comment': comment_object.parent_comment
        }
    
    def start_text_ml_workflow(self, leaf_object):
        leaf_data = self.leaf_to_json(leaf_object)
        text_api_endpoint = self.HAZEL_AI_ADDRESS + 'leaf_text_pipeline'
        response = self.make_POST_request(text_api_endpoint,leaf_data)
        return response
    


