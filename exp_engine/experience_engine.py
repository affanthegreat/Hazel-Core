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
        self.time_of_running = datetime.now()
        self.engagement_points_weight = 0.6

    def experience_status_verification(self, user_object):
        prev_date = user_object.previous_experience_generation_date
        if prev_date == None:
            return True
        delta = self.time_of_running - prev_date
        return delta > timedelta(hours=6)

    def generate_exp_points(self, engagement_map, experience_map):
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

    def generate_level(self, user_exp_points, base_level_points=750, multiplier=2):

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

    def initiate(self, request):
        analytics_object = EdenAnalyticsEngine(request)
        response = analytics_object.initiate()

        eden_session_manager = EdenSessionManagement()
        user_object = eden_session_manager.get_session_user(request)

        if response['status'] == 100 and self.experience_status_verification(user_object):
            unfiltered_metric_data = response['data']
            leaf_engagement_map, leaf_experience_map = self.filter_metrics(unfiltered_metric_data)
            total_user_exp = self.generate_exp_points(leaf_engagement_map, leaf_experience_map)
            level = self.generate_level(total_user_exp)
            middleware_status = self.initiate_user_middleware(user_object, total_user_exp, level)
            if middleware_status:
                return {'status': 100,'message': f"Experience Engine has completed it's task on user {user_object.user_id}. "}
        return {'status': 106, "message": "User is either not logged-in or has gone through exp engine before delta period."}


class EdenAnalyticsEngine():
    def __init__(self, request):
        self.request = request
        self.time_of_running = datetime.now()

    def metric_weights(self):
        self.public_like_weight = 1
        self.public_dislike_weight = -1
        self.public_comment_weight = 2
        self.public_view_weight = 0.2

        self.private_like_weight = 0.6
        self.private_dislike_weight = -0.6
        self.private_comment_weight = 1.2
        self.private_view_weight = 0.7

    def analytics_verification(self, leaf_object):
        prev_date =leaf_object.previous_analytics_run
        if prev_date == None:
            True
        delta = self.time_of_running - prev_date
        return delta > timedelta(hours=6)

    def generate_engagement_rate(self, leaf_object):
        if leaf_object.views_count == 0:
            return 0
        else:
            likes = leaf_object.likes_count
            dislikes = leaf_object.dislikes_count
            comments = leaf_object.comments_count
            views = leaf_object.views_count
            return (likes + comments + (0.75 * dislikes)) / views

    def generate_per_view_exp(self, leaf_object, user_object):
        experience_points = 0

        user_followers = user_object.user_followers
        user_following = user_object.user_following

        if leaf_object.leaf_type == LeafType.Private.value:
            experience_points += (leaf_object.likes_count * self.private_like_weight)
            experience_points += (leaf_object.dislikes_count * self.private_dislike_weight)
            experience_points += (leaf_object.comments_count * self.private_comment_weight)
            experience_points += (leaf_object.views_count * self.private_view_weight)
        else:
            experience_points += (leaf_object.likes_count * self.public_like_weight)
            experience_points += (leaf_object.dislikes_count * self.public_dislike_weight)
            experience_points += (leaf_object.comments_count * self.public_comment_weight)
            experience_points += (leaf_object.views_count * self.public_view_weight)

        return experience_points * (1 + (user_followers / 100) + (user_following) / 100)

    def run_middleware(self, data):
        eden_leaf_middleware = EdenLeafMiddleware(data['leaf_object'])

        eden_leaf_middleware.update_engagement_rate(data['leaf_engagement_rate'])
        eden_leaf_middleware.update_exp_rate(data['leaf_experience_rate'])
        eden_leaf_middleware.update_previous_analytics_date(self.time_of_running)

    def initiate(self):
        eden_leaf_manager = EdenLeafManagement()
        try:
            eden_user = eden_leaf_manager.get_logged_in_user(self.request)
            public_leaf_objects = eden_leaf_manager.get_user_public_leaves()
            private_leaf_objects = eden_leaf_manager.get_user_private_leaves()
            leaf_avg_points_map = {}

            for public_leaf in public_leaf_objects:
                analytics_required = self.analytics_verification(public_leaf)
                if analytics_required:
                    data = {
                        "leaf_object": public_leaf
                    }
                    leaf_engagement_rate = self.generate_engagement_rate(public_leaf)
                    leaf_experience_rate = self.generate_per_view_exp(public_leaf, eden_user)

                    data['leaf_engagement_rate'] = leaf_engagement_rate
                    data['leaf_experience_rate'] = leaf_experience_rate

                    self.run_middleware(public_leaf, data)
                    leaf_avg_points_map[public_leaf.leaf_id] = (leaf_engagement_rate, leaf_experience_rate)

            for private_leaf in private_leaf_objects:
                analytics_required = self.analytics_verification(private_leaf)
                if analytics_required:
                    data = {
                        "leaf_object": public_leaf
                    }
                    leaf_engagement_rate = self.generate_engagement_rate(private_leaf)
                    leaf_experience_rate = self.generate_per_view_exp(private_leaf, eden_user)

                    data['leaf_engagement_rate'] = leaf_engagement_rate
                    data['leaf_experience_rate'] = leaf_experience_rate
                    self.run_middleware(private_leaf, data)
                    leaf_avg_points_map[private_leaf.leaf_id] = (leaf_engagement_rate, leaf_experience_rate)

            response = {'status': 100, 'data': leaf_avg_points_map}
            return response
        except Exception as E:
            return {'status': 105}
