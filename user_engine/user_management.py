import crypt

from user_engine.models import *


class EdenUserManagement:
    def __init__(self) -> None:
        pass

    def make_password(self, txt) -> str:
        return crypt.crypt(txt)

    def create_user(self, data):
        user_name = data["user_name"]
        user_id = data["user_id"]
        user_email = data["user_email"]
        user_password = data["user_password"]
        user_public_leaf_count = 0
        user_private_leaf_count = 0
        user_experience_points = 0
        user_verified = False
        user_followers = 0
        user_following = 0
        user_level = 0

        verification_data = {
            "user_id": user_id,
            "user_email": user_email,
            "user_name": user_name,
        }
        if self.check_user_exists(verification_data):
            response = {"status": False, "issue": "User already exists."}
            return response
        else:
            user_profile_object = UserProfile()
            user_profile_object.user_email = user_email
            user_profile_object.user_id = user_id
            user_profile_object.user_private_leaf_count = user_private_leaf_count
            user_profile_object.user_public_leaf_count = user_public_leaf_count
            user_profile_object.user_experience_points = user_experience_points
            user_profile_object.user_verified = user_verified
            user_profile_object.user_password = self.make_password(user_password)
            user_profile_object.user_name = user_name
            user_profile_object.user_followers = user_followers
            user_profile_object.user_following = user_following
            user_profile_object.user_level = user_level
            try:
                user_profile_object.save()
                response = {"status": True, "issue": "Success."}
            except Exception:
                response = {"status": False, "issue": "object creation failed."}
            return response

    def check_user_exists(self, data) -> bool:
        print(data, type(data))
        user_name = data.get("user_name", None)
        user_id = data.get("user_id", None)
        user_email = data.get("user_email", None)
        if (
            UserProfile.objects.filter(user_id=user_id).exists()
            or UserProfile.objects.filter(user_name=user_name).exists()
            or UserProfile.objects.filter(user_email=user_email).exists()
        ):
            return True
        return False

    def validate_user(self, data) -> bool:
        user_password = data["user_password"]
        user_id = data['user_id']
        is_valid = False
        if self.check_user_exists({"user_id": user_id}):
            user_object = self.get_user_object(user_id)
            is_valid = crypt.crypt(user_password, user_object.user_password) == user_object.user_password
        return is_valid

    def retrieve_user_password(self, data):
        if self.check_user_exists(data):
            user_id = data["user_id"]
            user_object = UserProfile.objects.filter(user_id=user_id).all()
            return list(user_object)[0].user_password
        else:
            return None

    def user_follow(self, data):
        follower = data["follower"]
        follows = data["follows"]
        if self.check_user_exists({"user_id": follower}) and self.check_user_exists(
            {"user_id": follows}
        ):
            follower_relationship = UserFollowing()
            follower_object = self.get_user_object(follower)
            following_object = self.get_user_object(follows)
            follower_relationship.slave = follower_object
            follower_relationship.master = following_object
            print(follower_object, follower_object)
            try:
                follower_relationship.save()
                self.run_user_middleware(following_object, "update_followers", 1)
                response = {
                    "status": 200,
                    "message": f"{follower} added as follower added to {follows}",
                }
            except Exception as E:
                print(E)
                response = {"status": 200, "message": "Error while adding the follower"}
            print(response)
            return response
        else:
            response = {"status": 200, "message": "One of the user does not exists."}
            print(response)

    def user_unfollow(self, data):
        follower = data["follower"]
        follows = data["follows"]
        if self.check_user_exists({"user_id": follower}) and self.check_user_exists(
            {"user_id": follows}
        ):
            request_data = {
                'user_id': follower,
                'sub_user': follows
            }
            followers_set = self.get_user_followers(request_data)

    def get_user_followers(self, data):
        user_profile = data["user_id"]
        sub_user = data.get('sub_user', None)
        if self.check_user_exists(data):
            user_profile_object = UserProfile.objects.filter(user_id=user_profile)
            followers_query_set = UserFollowing.objects.filter(
                master=user_profile, slave=sub_user
            ).all()
            return list(followers_query_set.values())

    def get_user_following(self, data):
        user_profile = data["user_id"]
        if self.check_user_exists(data):
            user_profile_object = UserProfile.objects.filter(user_id=user_profile)
            following_query_set = UserFollowing.objects.filter(slave=user_profile).all()
            return list(following_query_set.values())

    def password_reset(self, data) -> bool:
        user_id = data['user_id']
        old_password = data['user_password']
        user_password1 = data['user_password1']
        user_password2 = data['user_password2']
        response = {}
        if self.check_user_exists(data):
            response['status'] = 200
            if self.validate_user(data):
                user_object = self.get_user_object(user_id)
                if user_password1 == user_password2:
                    new_pass = self.make_password(user_password1)
                    user_object.user_password = new_pass
                    user_object.save()
                    response['message'] = "Password changed sucessfully"
                else:
                    response['message'] = "New passwords does not match"
            else:
                response['message'] = "Invalid current password"
        else:
            response['message'] = "User doesn't exist"
        return response

    # TODO
    def edit_user(self, data):
        user_name = data['user_name']
        pass

    def get_user_object(self, user_id):
        return UserProfile.objects.filter(user_id=user_id).first()

    def run_user_middleware(self, user_object, operation, value):
        user_middleware_object = EdenUserMiddleWare(user_object)
        allowed_operations = ['update_public_leaf', "update_private_leaf",
                              "update_followers", "update_following", "update_user_exp", "update_user_level"]
        if operation not in allowed_operations:
            return False
        else:
            match operation:
                case "update_public_leaf":
                    return user_middleware_object.update_public_leafs_count(value)
                case "update_private_leaf":
                    return user_middleware_object.update_private_leafs_count(value)
                case "update_followers":
                    return user_middleware_object.update_followers(value)
                case "update_following":
                    return user_middleware_object.update_following(value)
                case "update_user_exp":
                    return user_middleware_object.update_user_exp(value)
                case "update_user_level":
                    return user_middleware_object.update_user_level(value)
