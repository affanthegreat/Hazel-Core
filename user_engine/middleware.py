from user_engine.models import UserProfile

class EdenUserMiddleWare():
    def __init__(self, user_object):
        self.user_object = user_object
        pass

    def update_public_leafs_count(self, value):
        try:
            self.user_object.user_public_leaf_count += value
            self.user_object.save()
            return self.user_object.user_public_leaf_count
        except:
            return False
      

    def update_private_leafs_count(self, value):
        try:
            self.user_object.user_private_leaf_count += value
            self.user_object.save()
            return self.user_object.user_private_leaf_count
        except:
            return False

        pass

    def update_followers(self, value):
        try:
            self.user_object.user_followers += value
            self.user_object.save()
            return self.user_object.user_followers
        except:
            return False


    def update_following(self, value):
        try:
            self.user_object.user_following += value
            self.user_object.save()
            return self.user_object.user_following
        except:
            return False

    def update_user_exp(self, value):
        try:
            self.user_object.user_experience_points += value
            self.user_object.save()
            return self.user_object.experience_points
        except:
            return False

    def update_user_level(self, value):
        try:
            self.user_object.user_level += value
            self.user_object.save()
            return self.user_object.user_level
        except:
            return False
