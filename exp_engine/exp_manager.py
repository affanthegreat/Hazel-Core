import logging
from datetime import datetime, timedelta

from leaf_engine.leaf_management import EdenLeafManagement
from leaf_engine.models import LeafType
from leaf_engine.middleware import EdenLeafMiddleware
from user_engine.backends import EdenSessionManagement
from user_engine.middleware import EdenUserMiddleWare
from user_engine.user_management import EdenUserManagement


class EdenExperienceEngine():
    def __init__(self):
        self.exp_points_weight = 0.4
        self.engagement_points_weight = 0.6
        logging.info("================EDEN EXP-PBR ENGINE================")
        self.time_of_running = datetime.now().astimezone()

    def experience_status_verification(self, user_object):
        prev_date = user_object.previous_experience_generation_date
        if prev_date == None:
            return True
        delta = self.time_of_running - prev_date
        return delta > timedelta(minutes=2)
    
    def generate_exp_points(self, engagement_rating, experience_rating):
        leaf_exp_points = 0
        leaf_exp_points += self.exp_points_weight * experience_rating
        leaf_exp_points += self.engagement_points_weight * engagement_rating
        return leaf_exp_points

    def generate_batch_exp_points(self, engagement_map, experience_map):
        total_user_exp = 0
        leaf_ids = engagement_map.keys()
        for leaf_id in leaf_ids:
            total_user_exp += (self.exp_points_weight * experience_map[leaf_id])
            total_user_exp += (self.engagement_points_weight * engagement_map[leaf_id])
        return total_user_exp

    def get_experience_points_for_level(self, level, base_points=100, multiplier=2):
        if level == 0:
            return 0
        previous_level_points = self.get_experience_points_for_level(level - 1, base_points, multiplier)
        return previous_level_points * multiplier if previous_level_points > 0 else base_points

    def generate_level(self, user_exp_points, base_points=750, multiplier=2):

        if user_exp_points < self.get_experience_points_for_level(1, base_points, multiplier):
            return 0
        level = 1
        while experience_points >= self.get_experience_points_for_level(level, base_points, multiplier):
            experience_points -= self.get_experience_points_for_level(level, base_points, multiplier)
            level += 1
        return level - 1

    def filter_metrics(self, metric_map):
        leaf_engagement_map = {}
        leaf_experience_map = {}
        for leaf_id in metric_map.keys():
            leaf_engagement_map[leaf_id] = metric_map[leaf_id][0]
            leaf_experience_map[leaf_id] = metric_map[leaf_id][1]
        return (leaf_engagement_map, leaf_experience_map)

    def initiate_user_middleware(self, user_object, total_user_exp, level):
        try:
            eden_user_middleware = EdenUserMiddleWare(user_object)
            eden_user_middleware.update_user_exp(total_user_exp)
            eden_user_middleware.update_user_level(level)
            eden_user_middleware.update_previous_experience_generation_date(self.time_of_running)
            return True
        except Exception as e:
            return False

    def pre_process(self,leaf_object):
        analytics_object = EdenAnalyticsEngine()
        response = analytics_object.run_analytics_per_leaf(leaf_object)
        logging.info("> Created Required objects.")
        return response

    def batch_pre_process(self,request):
        analytics_object = EdenAnalyticsEngine(request)
        eden_session_manager = EdenSessionManagement()
        self.response = analytics_object.per_user_batch_initiate()
        self.user_object = eden_session_manager.get_session_user(request)
        logging.info("> Created Required objects.")
    
    def start_main_process(self):
        unfiltered_metric_data = self.response['data']
        leaf_engagement_map, leaf_experience_map = self.filter_metrics(unfiltered_metric_data)
        total_user_exp = self.generate_batch_exp_points(leaf_engagement_map, leaf_experience_map)
        level = self.generate_level(total_user_exp)
        return (total_user_exp, level)

    def batch_initiate(self, request):
        self.batch_pre_process(request)
        if self.response['status'] == 100 and self.experience_status_verification(self.user_object):
            total_user_exp, level = self.start_main_process()
            middleware_status = self.initiate_user_middleware(self.user_object, total_user_exp, level)
            if middleware_status:
                return self.throw_process_complete_msg()
        return self.throw_process_failed_error()
    
    def calculate_user_exp_points(self,user_object):
        elm_object = EdenLeafManagement()
        leaves_query_set = elm_object.get_leaves_by_user_id(user_object.user_id)
        exp_points = 0
        for leaf in leaves_query_set:
            exp_points += leaf.exp_points
        logging.info(f"> User Object {user_object.user_id} total exp points: {exp_points}")
        return exp_points

    def run_per_leaf_middleware(self, leaf_object, ratings):
        eden_leaf_middleware  = EdenLeafMiddleware(leaf_object)

        eden_leaf_middleware.update_engagement_rate(ratings['engagement_rate'])
        eden_leaf_middleware.update_experience_rate(ratings['experience_rate'])
        eden_leaf_middleware.update_exp_points(ratings['leaf_total_exp_points'])
        eden_leaf_middleware.update_previous_analytics_date(self.time_of_running)

    def update_leaf_owner_metrics(self,leaf_object):
        eden_leaf_management = EdenLeafManagement()
        leaf_owner = eden_leaf_management.get_user_object(leaf_object.owner.user_id)
        eden_user_middleware = EdenUserMiddleWare(leaf_owner)
        operation_status = self.experience_status_verification(leaf_owner)
        if operation_status:
            logging.info("> Updating user metrics.")
            user_exp_points = self.calculate_user_exp_points(leaf_owner)
            level = self.generate_level(user_exp_points)
            eden_user_middleware.update_user_exp(user_exp_points)
            eden_user_middleware.update_user_level(level)
            eden_user_middleware.update_previous_experience_generation_date(self.time_of_running)
        logging.info(f"> Leaf owner metrics last performed on {leaf_owner.previous_experience_generation_date.strftime('%m/%d/%Y, %H:%M:%S')}.")
    def initiate_per_leaf(self,leaf_object):
        try:
            ratings = self.pre_process(leaf_object)
            engagement_rating, experience_rating = ratings['engagement_rate'], ratings['experience_rate']
            ratings['leaf_total_exp_points'] = self.generate_exp_points(engagement_rating, experience_rating)
            logging.info(f"> Leaf Object {leaf_object.leaf_id} total exp points: {ratings}")
            self.run_per_leaf_middleware(leaf_object, ratings)
            self.update_leaf_owner_metrics(leaf_object)
            return 100
        except Exception as e:
            raise e
        
    def initiate_per_leaf_view(self, leaf_id):
        elm_object = EdenLeafManagement()
        leaF_object = elm_object.get_leaf_object(leaf_id)
        response = self.initiate_per_leaf(leaF_object)
        
    def throw_process_complete_msg(self):
         return {'status': 100, 
                'message': f"Experience Engine has completed it's task on user {self.user_object.user_id}."}

    def throw_process_failed_error(self):
        return {'status': 106,
                 "message": "User is either not logged-in or has gone through exp engine before delta period."}

class EdenAnalyticsEngine():
    def __init__(self, request=None):
        self.request = request
        self.leaf_avg_points_map = {}
        self.time_of_running = datetime.now()
        self.metric_weights()

    def metric_weights(self):
        self.public_like_weight = 1
        self.public_dislike_weight = -1
        self.public_comment_weight = 2
        self.public_view_weight = 0.1

        self.private_like_weight = 0.3
        self.private_dislike_weight = -0.3
        self.private_comment_weight = 0.8
        self.private_view_weight = 0.05

    def analytics_verification(self, leaf_object):
        prev_date = leaf_object.previous_analytics_run
        if prev_date == None:
            True
        delta = self.time_of_running - prev_date
        return delta > timedelta(hours=6)

    def generate_engagement_rate(self, leaf_object):
        if leaf_object.view_count == 0:
            return 0
        else:
            likes = leaf_object.likes_count
            dislikes = leaf_object.dislikes_count
            comments = leaf_object.comments_count
            views = leaf_object.view_count
            return (likes + comments + (0.75 * dislikes)) / views

    def generate_per_view_exp(self, leaf_object, user_object):
        experience_points = 0

        user_followers = user_object.user_followers
        user_following = user_object.user_following

        if leaf_object.leaf_type == LeafType.Private.value:
            experience_points += (leaf_object.likes_count * self.private_like_weight)
            experience_points += (leaf_object.dislikes_count * self.private_dislike_weight)
            experience_points += (leaf_object.comments_count * self.private_comment_weight)
            experience_points += (leaf_object.view_count * self.private_view_weight)
        else:
            experience_points += (leaf_object.likes_count * self.public_like_weight)
            experience_points += (leaf_object.dislikes_count * self.public_dislike_weight)
            experience_points += (leaf_object.comments_count * self.public_comment_weight)
            experience_points += (leaf_object.view_count * self.public_view_weight)

        return experience_points * (1 + (user_followers / 100) + (user_following) / 100)

    def run_middleware(self, data):
        eden_leaf_middleware = EdenLeafMiddleware(data['leaf_object'])

        eden_leaf_middleware.update_engagement_rate(data['leaf_engagement_rate'])
        eden_leaf_middleware.update_experience_rate(data['leaf_experience_rate'])
        eden_leaf_middleware.update_previous_analytics_date(self.time_of_running)
    
    def run_analytics_per_leaf(self,leaf_object):
        eden_leaf_manager = EdenLeafManagement()
        data = {"leaf_object": leaf_object}
        leaf_engagement_rate = self.generate_engagement_rate(leaf_object)
        leaf_experience_rate = self.generate_per_view_exp(leaf_object, eden_leaf_manager.get_user_object(leaf_object.owner.user_id))

        data['leaf_engagement_rate'] = leaf_engagement_rate
        data['leaf_experience_rate'] = leaf_experience_rate

        self.run_middleware(data)
        return {"engagement_rate": leaf_engagement_rate, 
                "experience_rate": leaf_experience_rate}
        
    def process_user_public_leaves(self):
        if self.request == None:
            return self.throw_request_not_found_error()
        eden_leaf_manager = EdenLeafManagement()
        public_leaf_objects = eden_leaf_manager.get_user_public_leaves(self.request,require_pagination=False)
        for public_leaf in public_leaf_objects:
            analytics_required = self.analytics_verification(public_leaf)
            if analytics_required:
                ratings = self.run_analytics_per_leaf(public_leaf)
                self.leaf_avg_points_map[public_leaf.leaf_id] = (ratings['engagement_rate'], ratings['experience_rate'])

    
    def process_user_private_leaves(self):
        if self.request == None:
            return self.throw_request_not_found_error()
        eden_leaf_manager = EdenLeafManagement()
        private_leaf_objects = eden_leaf_manager.get_user_private_leaves(self.request, require_pagination= False)
        for private_leaf in private_leaf_objects:
            analytics_required = self.analytics_verification(private_leaf)
            if analytics_required:
                ratings = self.run_analytics_per_leaf(private_leaf)
                self.leaf_avg_points_map[private_leaf.leaf_id] =  (ratings['engagement_rate'], ratings['experience_rate'])
 

    def per_user_batch_initiate(self):
        if self.request == None:
            return self.throw_request_not_found_error()
        self.process_user_public_leaves()
        self.process_user_private_leaves()
        return {'status': 100, 'data': self.leaf_avg_points_map}
    
    def throw_request_not_found_error(self):
        return {
            'status':'-111',
            'message': 'request object not initiated with analytics object.'
        }