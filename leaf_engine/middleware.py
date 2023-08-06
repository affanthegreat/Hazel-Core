class EdenLeafMiddleware():

    def __init__(self, leaf_object) -> None:
        self.leaf_object = leaf_object

    def update_likes(self, value):
        try:
            self.leaf_object.likes_count += value
            self.leaf_object.save()
            return self.leaf_object.likes_count
        except Exception as e:
            raise self.throw_middleware_failed_error(e)

    def update_dislikes(self, value):
        try:
            self.leaf_object.dislikes_count += value
            self.leaf_object.save()
            return self.leaf_object.dislikes_count
        except Exception as e:
           raise self.throw_middleware_failed_error(e)

    def update_comments(self, value):
        try:
            self.leaf_object.comments_count += value
            self.leaf_object.save()
            return self.leaf_object.comments_count
        except Exception as e:
            raise self.throw_middleware_failed_error(e)

    def update_views(self, value):
        try:
            self.leaf_object.view_count += value
            self.leaf_object.save()
            return self.leaf_object.views_count
        except Exception as e:
            raise self.throw_middleware_failed_error(e)

    def update_engagement_rate(self, value):
        try:
            self.leaf_object.engagement_rating = value
            self.leaf_object.save()
            return self.leaf_object.engagement_rating
        except Exception as e:
            raise self.throw_middleware_failed_error(e)

    def update_experience_rate(self, value):
        try:
            self.leaf_object.experience_rating = value
            self.leaf_object.save()
            return self.leaf_object.experience_rating
        except Exception as e:
            raise self.throw_middleware_failed_error(e)

    def update_exp_points(self, value):
        try:
            self.leaf_object.exp_points = value
            self.leaf_object.save()
            return self.leaf_object.experience_rating
        except Exception as e:
            raise self.throw_middleware_failed_error(e)
    
    def update_previous_analytics_date(self, date):
        try:
            self.leaf_object.previous_analytics_run = date
            self.leaf_object.save()
            return self.leaf_object.previous_analytics_run
        except Exception as e:
            raise self.throw_middleware_failed_error(e)

    def throw_middleware_failed_error(self,error):
        return Exception(f"Middleware did not proceed as excepted. This might cause inconsistency with data. Wait till the Leaf object gets batch processed user-wise. \n ENCOUNTERED ERROR : {error}")