from exp_engine.models import UserTopicRelations

class EdenUserTopicRelationMiddleWare():
    def __init__(self, user_topic_relation_object):
        self.user_topic_relation_object = user_topic_relation_object

    def update_likes_count(self, value):
        try:
            self.user_topic_relation_object.likes += value
            self.user_topic_relation_object.save()
            return self.user_topic_relation_object.likes
        except:
            return False

    def update_dislikes_count(self, value):
        try:
            self.user_topic_relation_object.dislikes += value
            self.user_topic_relation_object.save()
            return self.user_topic_relation_object.dislikes
        except:
            return False


    def update_comments(self, value):
        try:
            self.user_topic_relation_object.comments += value
            self.user_topic_relation_object.save()
            return self.user_topic_relation_object.comments
        except:
            return False

    def update_sub_comments(self, value):
        try:
            self.user_topic_relation_object.sub_comments += value
            self.user_topic_relation_object.save()
            return self.user_topic_relation_object.sub_comments
        except:
            return False

    def update_total_leaves_served(self, value):
        try:
            self.user_topic_relation_object.leaves_served_by_engine += value
            self.user_topic_relation_object.save()
            return self.user_topic_relation_object.leaves_served_by_engine
        except:
            return False

    def update_times_interacted(self, value):
        try:
            self.user_topic_relation_object.times_interacted += value
            self.user_topic_relation_object.save()
            return self.user_topic_relation_object.times_interacted
        except:
            return False

    def update_positive_comments_made(self, value):
        try:
            self.user_topic_relation_object.positive_comments_made += value
            self.user_topic_relation_object.save()
            return self.user_topic_relation_object.positive_comments_made
        except:
            return False
    
    def update_negative_comments_made(self, value):
        try:
            self.user_topic_relation_object.negative_comments_made += value
            self.user_topic_relation_object.save()
            return self.user_topic_relation_object.negative_comments_made
        except:
            return False
    
    def update_favoritism_weight(self,value):
        try:
            self.user_topic_relation_object.favoritism_weight += value
            self.user_topic_relation_object.save()
            return self.user_topic_relation_object.favoritism_weight
        except:
            return False
        

