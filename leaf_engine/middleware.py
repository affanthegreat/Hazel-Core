class EdenLeafMiddleware:

    def __init__(self, leaf_object) -> None:
        self.leaf_object = leaf_object

    def update_likes(self, value):
        try:
            self.leaf_object.likes_count += value
            self.leaf_object.save()
            return self.leaf_object.likes_count
        except:
            return False

    def update_dislikes(self, value):
        try:
            self.leaf_object.dislikes_count += value
            self.leaf_object.save()
            return self.leaf_object.dislikes_count
        except:
            return False

    def update_comments(self, value):
        try:
            self.leaf_object.comment_count += value
            self.leaf_object.save()
            return self.leaf_object.comment_count
        except:
            return False

    def update_views(self, value):
        try:
            self.leaf_object.views_count += value
            self.leaf_object.save()
            return self.leaf_object.views_count
        except:
            return False
