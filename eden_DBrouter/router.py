class EdenDBRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'user_data':
            return 'user_db'
        if model._meta.app_label == 'leaf_data':
            return 'leaf_db'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'user_data':
            return 'user_db'
        if model._meta.app_label == 'leaf_data':
            return 'leaf_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'user_data' or \
           obj2._meta.app_label == 'user_data':
           return True
        if obj1._meta.app_label == 'leaf_data' or \
           obj2._meta.app_label == 'leaf_data':
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):

        if app_label == 'user_data':
            return db == 'user_db'
        if app_label == 'leaf_data':
            return db == 'leaf_db'
        return None