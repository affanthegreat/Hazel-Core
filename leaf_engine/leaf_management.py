import uuid
import logging 

from django.core.paginator import Paginator
from exp_engine.conx_manager import Eden_CONX_Engine
from exp_engine.middleware import EdenUserTopicRelationMiddleWare
from exp_engine.models import InteractionType

from leaf_engine.middleware import EdenLeafMiddleware
from leaf_engine.models import Leaf, LeafComments, LeafDisLikes, LeafLikes, LeafType, LeafViewedBy

from user_engine.backends import EdenSessionManagement
from user_engine.models import UserProfile
from user_engine.middleware import EdenUserMiddleWare
from user_engine.user_management import EdenUserManagement

session_management_object = EdenSessionManagement()


class EdenLeafManagement:
    def generate_leaf_id(self):
        """
        Generate a unique identifier for a leaf node.

        The function generates a unique identifier for a leaf node by creating a session ID using the uuid module.
        Returns:
        A string representing the generated session ID.

        """
        session_id = str(uuid.uuid4()).upper().replace("-", "")
        return session_id

    def __init__(self) -> None:
        self.MAX_OBJECT_LIMIT = 30
        pass

    def create_leaf(self, request, data):
        """
        Create a new leaf object with provided data.

        This function creates a new leaf object with the given data by first checking if the user is logged in or not.
        If the user is logged in, it creates a new Leaf object with the provided data such as text content, image content,
        leaf type, and generates a unique ID for the new leaf object using the generate_leaf_id() method.
        After creating the new Leaf object, it is saved to the database and the user's middleware is updated accordingly.
        If the leaf type is Private, the user's "update_private_leaf" middleware is updated. If the leaf type is Public, the
        user's "update_public_leaf" middleware is updated.

        Args:
        request: HttpRequest object representing the incoming request.
        data: A dictionary containing the necessary data for creating a new Leaf object.

        Returns:
        A dictionary with the following keys:
        - status: An integer representing the status code of the response.
        - message: A string representing the message of the response.
        - code: A boolean value indicating the success or failure of the operation.
        """

        response = {}
        if self.get_logged_in_user(request):
            new_leaf_object = Leaf()
            new_leaf_object.leaf_id = self.generate_leaf_id()
            new_leaf_object.owner = session_management_object.get_session_user(request)
            new_leaf_object.text_content = data["text_content"]
            new_leaf_object.image_content = None
            new_leaf_object.leaf_type = LeafType(data["leaf_type"])
            try:
                new_leaf_object.save()
            except:
                return {
                    "status": -101,
                    "message": "Model not saved."
                }
            if LeafType(data['leaf_type']) == LeafType.Private:
                self.run_user_middleware(self.get_logged_in_user(request), "update_private_leaf", 1)
            else:
                self.run_user_middleware(self.get_logged_in_user(request), "update_public_leaf", 1)
            response["status"] = -100
            response["message"] = "Leaf successfully created."
            response["code"] = True
        else:
            response["status"] = -101
            response["code"] = False
        return response

    def get_user_public_leaves(self, request, page_number, require_pagination= True):
        """
        Retrieve all public leaf objects associated with the logged-in user.

        This function retrieves all public leaf objects associated with the logged-in user. If the user is not logged in or
        not authorized to access the resource, it returns a status code of -101.

        Args:
        request: HttpRequest object representing the incoming request.

        Returns:
        If the user is authorized, a QuerySet containing all the public leaf objects associated with the logged-in user
        is returned. Otherwise, a status code of -101 is returned to indicate unauthorized access.
        """
        
        if self.is_authorised(request):
            user_object = self.get_logged_in_user(request)
            query_set = Leaf.objects.filter(owner=user_object, leaf_type=LeafType.Public).order_by('-creation_date').all()
            if require_pagination:
                return self.paginator(query_set,page_number)
            else:
                return query_set
        else:
            return -101

    def get_leaves_by_user_id(self,user_id):
        user_management_instance = EdenUserManagement()
        if user_management_instance.check_user_exists({'user_id': user_id}):
            query_set = Leaf.objects.filter(owner= self.get_user_object(user_id)).order_by('-creation_date').all()
            return query_set
        else:
            raise Exception("User does not exists")


    def get_leaves(self, request, user_id, page_number, require_pagination = True):
        """
        Retrieve all leaf objects associated with a given user ID.

        This function retrieves all leaf objects associated with a given user ID by first checking if the logged-in user is
        authorized to access the resource. If the user is authorized and the user ID exists, it returns all leaf objects
        associated with the user ID. If the logged-in user is not following the user with the given ID, it returns only the
        public leaf objects. If the user ID does not exist, it returns a status code of -101.

        Args:
        request: HttpRequest object representing the incoming request.
        user_id: A string representing the user ID whose leaf objects need to be retrieved.

        Returns:
        If the user is authorized and the user ID exists, a QuerySet containing all the leaf objects associated with the
        user ID is returned. If the logged-in user is not following the user with the given ID, it returns only the public
        leaf objects. If the user ID does not exist, a status code of -101 is returned to indicate the non-existence of the
        user.
        """
        follower_user = self.get_logged_in_user(request)
        user_management_instance = EdenUserManagement()
        if user_management_instance.check_user_exists({'user_id': user_id}):
            following_object = user_management_instance.get_user_object(user_id)
            if user_management_instance.check_following(following_object, follower_user):
                query_set = Leaf.objects.filter(owner=following_object).order_by('-creation_date').all()
            else:
                query_set = Leaf.objects.filter(owner=following_object, leaf_type=LeafType.Public).order_by('-creation_date').all()
            if require_pagination: 
                return self.paginator(query_set,page_number)
            else:
                return query_set
        else:
            return -101

    def get_user_private_leaves(self, request, page_number,require_pagination= True):
        """
        Retrieve all private leaf objects associated with the logged-in user.

        This function retrieves all private leaf objects associated with the logged-in user. If the user is not logged in or
        not authorized to access the resource, it returns a status code of -101.

        Args:
        request: HttpRequest object representing the incoming request.

        Returns:
        If the user is authorized, a QuerySet containing all the private leaf objects associated with the logged-in user
        is returned. Otherwise, a status code of -101 is returned to indicate unauthorized access.
        """
        if self.is_authorised(request):
            user_object = self.get_logged_in_user(request)
            query_set = Leaf.objects.filter(owner=user_object, leaf_type=LeafType.Private).order_by('-creation_date').all()
            if require_pagination:
                return self.paginator(query_set,page_number)
            else:
                return query_set
        else:
            return -101

    def delete_leaf(self, request, leaf_id):
        """
        Delete the leaf object with the given ID if authorized.

        This function deletes the leaf object with the given ID if the logged-in user is authorized to do so. If the user is
        not authorized, it returns a status code of -102. If the leaf object does not exist, an appropriate error message is
        returned.

        Args:
        request: HttpRequest object representing the incoming request.
        leaf_id: A string representing the ID of the leaf object that needs to be deleted.

        Returns:
        A dictionary containing the response message indicating whether the leaf object was successfully deleted or not.
        If the logged-in user is authorized and the leaf object exists, a message of -100 is returned indicating
        successful deletion. If the user is not authorized, a message of -102 is returned. If the leaf object does not
        exist, an appropriate error message is returned.
        """
        if self.is_authorised(request):
            response = {}
            user_object = self.get_logged_in_user(request)
            leaf_object = self.get_leaf_object(leaf_id)
            if leaf_object.owner == user_object:
                leaf_object.delete()
                response["message"] = f"-100"
            else:
                response["message"] = "-102"
            return response

    def like_leaf(self, request, leaf_id):
        """
        Like a leaf if authorized and not already liked by the user.

        This function allows a logged-in user to like a leaf object if the user is authorized and the leaf object has not been
        liked by the user before. If the user is not authorized or the leaf object has already been liked by the user, it
        returns an appropriate error message.

        Args:
        request: HttpRequest object representing the incoming request.
        leaf_id: A string representing the ID of the leaf object that the user wants to like.

        Returns:
        If the logged-in user is authorized and the leaf object has not been liked by the user before, the function
        creates a new LeafLikes object and returns a status code of -100 indicating successful liking of the leaf object.
        If the user is not authorized, a status code of -101 is returned. If the leaf object does not exist, an appropriate
        error message is returned. If the leaf object has already been liked by the user, a status code of -103 is returned.
        """
        if self.is_authorised(request):
            user_object = self.get_logged_in_user(request)
            print(self.check_like(leaf_id, user_object.user_id)["message"])
            if (
                self.check_leaf(leaf_id)
                and not self.check_like(leaf_id, user_object.user_id)["message"]
            ):
                like_object = LeafLikes()
                like_object.leaf = self.get_leaf_object(leaf_id)
                like_object.liked_by = user_object
                like_object.save()
                self.run_leaf_middleware(self.get_leaf_object(leaf_id), "update_likes", 1)
                self.run_exp_engine_per_leaf(self.get_leaf_object(leaf_id))
                self.run_conX_engine(leaf_id,'like')
                self.run_user_topic_middleware(leaf_id,
                                               "like",
                                               self.get_user_object(user_object.user_id),
                                                1)
                return -100
            else:
                return -103

    def dislike_leaf(self, request, leaf_id):
        """
        Dislikes a leaf identified by the given leaf_id and associates the dislike with the currently logged-in user.

        Args:
            request: The HTTP request object containing metadata about the request.
            leaf_id: The unique identifier of the leaf to be disliked.

        Returns:
            Returns -100 if the dislike operation was successful, indicating that the leaf was successfully disliked.
            Returns -103 if the dislike operation was unsuccessful, indicating that the leaf could not be disliked, either because it does not exist or because the user has already disliked the leaf.
        """
        if self.is_authorised(request):
            user_object = self.get_logged_in_user(request)
            print(self.check_dislike(leaf_id, user_object.user_id)["message"])
            if (
                self.check_leaf(leaf_id)
                and not self.check_dislike(leaf_id, user_object.user_id)["message"]
            ):
                dislike_object = LeafDisLikes()
                dislike_object.leaf = self.get_leaf_object(leaf_id)
                dislike_object.disliked_by = user_object
                dislike_object.save()
                self.run_leaf_middleware(self.get_leaf_object(leaf_id), "update_dislikes", 1)
                self.run_exp_engine_per_leaf(self.get_leaf_object(leaf_id))
                self.run_conX_engine(leaf_id,'dislike')
                self.run_user_topic_middleware(leaf_id,
                                               "dislike",
                                               self.get_user_object(user_object.user_id),
                                                1)
                return -100
            else:
                return -103

    def remove_like(self, request, leaf_id):
        """
        The remove_like function takes a request and leaf_id as input parameters, and removes the like on a leaf if it exists. It first checks if the request is authorized, then gets the logged-in user object and checks the like status of the leaf for that user. If the leaf exists and the user has liked it, the like object is retrieved and deleted, and the update_likes middleware is run to update the like count. The function returns -100 if the like is successfully removed, and -105 if the user has not liked the leaf or the leaf does not exist.
        Args:

        request: A HttpRequest object that contains metadata about the request.
        leaf_id: An integer value representing the ID of the leaf that the user is attempting to remove the like from.
        Returns:

        -100 if the like is successfully removed.
        -105 if the user has not liked the leaf or the leaf does not exist.
        """
        if self.is_authorised(request):
            user_object = self.get_logged_in_user(request)
            like_status = self.check_like(leaf_id, user_object.user_id)
            if self.check_leaf(leaf_id) and like_status["message"]:
                like_object = self.get_like_object(leaf_id, user_object.user_id)
                like_object.delete()
                self.run_leaf_middleware(self.get_leaf_object(leaf_id), "update_likes", -1)
                self.run_exp_engine_per_leaf(self.get_leaf_object(leaf_id))
                self.run_user_topic_middleware(leaf_id,
                                               "like",
                                               self.get_user_object(user_object.user_id),
                                                -1)
                return -100
            else:
                return -105

    def remove_dislike(self, request, leaf_id):
        """
        Removes a dislike for a leaf by the logged in user.

        Parameters:

        request: HttpRequest object containing metadata about the current request.
        leaf_id: Integer representing the ID of the leaf to remove the dislike for.
        Returns:

        Integer -100 if the dislike was successfully removed, -105 if the dislike was not found.
        This function checks if the request is authorized and obtains the user object for the logged in user. It then checks if the specified leaf exists and if the user has previously disliked it. If both conditions are met, the function retrieves the dislike object and deletes it. Finally, the function runs the 'update_dislikes' middleware for the specified leaf and returns -100 to indicate success or -105 if the dislike was not found.
        """
        if self.is_authorised(request):
            user_object = self.get_logged_in_user(request)
            like_status = self.check_dislike(leaf_id, user_object.user_id)
            print(like_status)
            if self.check_leaf(leaf_id) and like_status["message"]:
                dislike_object = self.get_dislike_object(leaf_id, user_object.user_id)
                dislike_object.delete()
                self.run_leaf_middleware(self.get_leaf_object(leaf_id), "update_dislikes", -1)
                self.run_exp_engine_per_leaf(self.get_leaf_object(leaf_id))
                self.run_user_topic_middleware(leaf_id,
                                               "dislike",
                                               self.get_user_object(user_object.user_id),
                                                -1)
                return -100
            else:
                return -105

    def get_total_likes(self, leaf_id, page_number):
        """
        This function returns the total number of likes for a given leaf.

        Args:
        leaf_id (int): The ID of the leaf for which the total number of likes is requested.

        Returns:
        QuerySet or int: If the leaf exists, the function returns a QuerySet object containing all the likes for the given leaf. If the leaf does not exist, it returns -104.
        """
        if self.check_leaf(leaf_id):
            return self.paginator(LeafLikes.objects.filter(leaf_id=leaf_id).order_by('-creation_date').all(), page_number)
        else:
            return -104

    def get_total_dislikes(self, leaf_id, page_number):
        """
        Returns the total number of dislikes for the given leaf identified by `leaf_id`.

        Args:
            leaf_id (int): The ID of the leaf to get the total number of dislikes for.

        Returns:
            If the leaf exists, the function returns a queryset of all `LeafDisLikes` instances for the given `leaf_id`.
            If the leaf doesn't exist, the function returns -104.
        """
        if self.check_leaf(leaf_id):
            return self.paginator(LeafDisLikes.objects.filter(leaf_id=leaf_id).order_by('-creation_date').all(),page_number)
        else:
            return -104

    def get_total_comments(self, request, leaf_id, page_number):
        """
        Return the total number of comments for the given leaf_id.

        If the given leaf_id exists in the database, return the queryset containing all the LeafComments objects
        associated with the leaf_id. Otherwise, return -104.

        Parameters:
        - request (HttpRequest): The HTTP request object.
        - leaf_id (int): The ID of the leaf for which total comments need to be calculated.

        Returns:
        If leaf_id exists in the database, return the queryset containing all the LeafComments objects
        associated with the leaf_id. Otherwise, return -104.

        """
        if self.check_leaf(leaf_id):
            return self.paginator(LeafComments.objects.filter(leaf_id=leaf_id).order_by('-creation_date').all(), page_number)
        else:
            return -104

    def add_comment(self, request, leaf_id, comment_string):
        """
        Add a new comment to the specified leaf.

        Args:
        - request: HttpRequest object representing the incoming request.
        - leaf_id: integer representing the ID of the leaf to add the comment to.
        - comment_string: string representing the comment text to be added.

        Returns:
        - integer: returns -100 and leaf_comment_id if the comment was successfully added.
                returns -101 if the user is not authorized.
                returns -103 if an exception occurs.
                returns -106 if the comment_string is None.
                returns -108 if the comment already exists for the given leaf_id.

        """
        if self.is_authorised(request):
            user_object = self.get_logged_in_user(request)
            if comment_string != None:
                try:
                    if self.check_leaf(leaf_id):
                        leaf_comment_object = LeafComments()
                        leaf_comment_object.commented_by = user_object
                        leaf_comment_object.leaf = self.get_leaf_object(leaf_id)
                        leaf_comment_object.comment = comment_string
                        logging.info("partial saving leaf comment object.")
                        leaf_comment_object.save()
                        leaf_comment_object.root_comment = leaf_comment_object
                        leaf_comment_object.save()
                        logging.info("root comment saved to leaf_comment object.")
                        self.run_leaf_middleware(self.get_leaf_object(leaf_id), "update_comments", 1)
                        self.run_exp_engine_per_leaf(self.get_leaf_object(leaf_id))
                        self.run_conX_engine(leaf_id,'comment')
                        self.run_user_topic_middleware(leaf_id,
                                               "comment",
                                               user_object.user_id,
                                                1, comment_id=leaf_comment_object.comment_id)
                        response = {
                            'status_code':-100,
                            'leaf_comment_id':str(leaf_comment_object.comment_id)
                        }
                        return response
                    else:
                        return {"status_code":-105}
                except Exception as E:
                    print(E)
                    return -103
            else:
                return -106
        else:
            return -101

    def remove_comment(self, request, leaf_id):
        """
        Removes a comment from a leaf object if it exists and if the user making the request is authorized to do so.

        Args:
        - request: a HTTP request object
        - leaf_id: an integer representing the ID of the leaf object

        Returns:
        - an integer code indicating the result of the operation:
            - -100: comment removed successfully
            - -101: user not authorized to perform the action
            - -105: comment not found or unexpected error occurred
        """
        if self.is_authorised(request):
            user_object = self.get_logged_in_user(request)
            comment_status = self.check_comment(leaf_id, user_object.user_id)
            try:
                if self.check_leaf(leaf_id) and comment_status["message"]:
                    leaf_object = self.get_leaf_object(leaf_id)
                    comment_object = self.get_comment_object(
                        leaf_id, user_object.user_id
                    )
                    
                    self.run_leaf_middleware(leaf_object, "update_comments", -1)
                    self.run_exp_engine_per_leaf(leaf_object)
                    self.run_user_topic_middleware(leaf_id,
                                               "comment",
                                               self.get_user_object(leaf_object.owner.user_id),
                                                -1, comment_id=comment_object.comment_id)
                    comment_object.delete()
                    return -100
            except Exception as E:
                print(E)
                return -105
        pass
    
    def remove_sub_comment(self, request,leaf_id, comment_id):
        if self.check_comment(leaf_id,comment_id):
            leaf_object = self.get_leaf_object(leaf_id)
            
            self.run_leaf_middleware(leaf_object, "update_comments", -1)
            self.run_exp_engine_per_leaf(leaf_object)
            self.run_user_topic_middleware(leaf_id,
                                            "sub_comment",
                                            self.get_user_object(leaf_object.owner.user_id),
                                            -1, comment_id=comment_id)
            LeafComments.objects.filter(comment_id= comment_id).first().delete()
            return -100
        else:
            return -104

    def add_view(self,leaf_object, user_object):
        """
        This function adds a view to a leaf object and returns a status code.

        Args:
        request: An HTTP request object.
        leaf_id: An integer representing the ID of the leaf object.

        Returns:
        -100 if the view was successfully added.
        -105 if the view could not be added due to an exception.
        """
        try:

            obj = LeafViewedBy()
            obj.leaf = leaf_object
            obj.viewed_by = user_object
            self.run_leaf_middleware(leaf_object, "update_view", 1)
            self.run_exp_engine_per_leaf(leaf_object)
            self.run_conX_engine(leaf_object.leaf_id,'view',)
            self.run_user_topic_middleware(leaf_object.leaf_id,
                                               "leaves_served",
                                               self.get_user_object(leaf_object.owner.user_id),
                                                1)
            return -100
        except Exception:
            return -105

    def create_view_object(self,request,leaf_id):
        if self.is_authorised(request):
            try:
                user_object = self.get_logged_in_user(request)
                leaf_object = self.get_leaf_object(leaf_id)
                if self.check_leaf(leaf_id) and self.check_viewed_by(user_object,leaf_object):
                    self.add_view(leaf_object,user_object)
                    return -100
            except Exception:
                return -105
    
    def check_viewed_by(self, user_object, leaf_object):
        try:
            return LeafViewedBy.objects.filer(leaf=leaf_object, viewed_by = user_object).exists()
        except:
            False
        
    def add_sub_comment_db(self, leaf_comment_id, leaf_comment_parent_id):
        """
        Adds a sub-comment to the database with the specified leaf_comment_id and leaf_comment_parent_id.

        If the sub-comment relationship between the given IDs already exists, the function does nothing and returns -100.
        If an exception occurs during the save operation, the function returns -105.

        Args:
            leaf_comment_id (int): The ID of the sub-comment to be added.
            leaf_comment_parent_id (int): The ID of the parent comment to which the sub-comment should be added.

        Returns:
            int: -100 if the sub-comment relationship already exists, -105 if an exception occurs during the save operation.
        """
        comment_object = LeafComments.objects.filter(comment_id=leaf_comment_id).first()
        parent_object = LeafComments.objects.filter(comment_id=leaf_comment_parent_id).first()
        base_comment = False
        if parent_object.comment_depth == 1:
            base_comment = True
        
        if self.check_subcomment(leaf_comment_id,leaf_comment_parent_id):
            try:
                root_leaf_object = self.get_leaf_object(comment_object.leaf_id)
                comment_object.comment_depth = parent_object.comment_depth + 1
                comment_object.parent_comment =  parent_object
                if base_comment:
                    comment_object.root_comment = parent_object
                else:
                    comment_object.root_comment = parent_object.root_comment
                comment_object.save()
                self.run_leaf_middleware(self.get_leaf_object(comment_object.leaf_id), "update_comments", 1)
                self.run_exp_engine_per_leaf(self.get_leaf_object(comment_object.leaf_id))
                self.run_conX_engine(comment_object.leaf_id,"sub_comment",comment_object.commented_by.user_id)

                root_leaf_object = self.get_leaf_object(comment_object.leaf_id)
                self.run_user_topic_middleware(comment_object.leaf_id,
                                               "sub_comment",
                                               self.get_user_object(root_leaf_object.owner.user_id),
                                                1, comment_id= comment_object.comment_id)
                return -100
            except Exception as E:
                comment_object.delete()
                return -105
        else:
            comment_object.delete()
            return -109

    def delete_comment_by_id(self,comment_id):
        """
           Deletes a comment by its ID.

           Args:
               id (int): The ID of the comment to be deleted.

           Returns:
               int: Returns -100 indicating the comment was successfully deleted.
           """
        if self.check_comment_by_id(comment_id):
            comment_object = LeafComments.objects.filter(comment_id=comment_id).first()
            if comment_object.comment_depth > 1:
                comment_type = "sub_comment"
            else:
                comment_type = "comment"
            leaf_object = self.get_leaf_object(comment_object.leaf_id)
            
            self.run_leaf_middleware(leaf_object, "update_comments", -1)
            self.run_exp_engine_per_leaf(leaf_object)
            self.run_user_topic_middleware(comment_object.leaf_id,
                                               comment_type,
                                               self.get_user_object(leaf_object.owner.user_id),
                                                -1, 
                                                comment_id= comment_object.comment_id)
            comment_object.delete()
            return -100

    def check_comment_by_id(self,id):
        """
           Checks if a comment exists by its ID.

           Args:
               id (int): The ID of the comment to check.

           Returns:
               bool: True if a comment with the specified ID exists, False otherwise.
           """
        return LeafComments.objects.filter(comment_id= id).first is not None

    def check_subcomment(self,comment_id,parent_comment_id):
        """
        Checks if a comment with the given comment_id is a sub-comment of the comment with the specified parent_comment_id.

        Args:
            comment_id (int): The ID of the comment to be checked.
            parent_comment_id (int): The ID of the parent comment to which the sub-comment should belong.

        Returns:
            bool: True if the comment with comment_id is a sub-comment of the comment with parent_comment_id, False otherwise.
        """
        relation_object = LeafComments.objects.filter(comment_id= comment_id).first()
        parent_comment_object = LeafComments.objects.filter(comment_id= parent_comment_id).first()
        if (relation_object is None and parent_comment_object is None) or relation_object.parent_comment == parent_comment_object:
            return False
        return True

    def check_leaf(self, leaf_id):
        """
        This function checks whether a given leaf_id exists in the database by querying the Leaf model. If a Leaf object with the specified leaf_id exists, it returns True, otherwise it returns False.

        The function takes a single argument:

        leaf_id: A string representing the leaf_id of the Leaf object to be checked.
        Returns:

        True if a Leaf object with the specified leaf_id exists in the database.
        False otherwise.
        """
        leaf_object = Leaf.objects.filter(leaf_id=leaf_id).first()
        return leaf_object is not None

    def check_comment(self, leaf_id, user_id):
        """
        The check_comment function checks if a comment exists on a given leaf_id for a given user_id. It returns a dictionary containing the status, message, and code keys.

        Args:

        leaf_id (int): The id of the leaf to check the comment on.
        user_id (int): The id of the user who commented on the leaf.
        Returns:

        A dictionary containing the following keys:
        status (int): The status code indicating the outcome of the check. Returns -100 if the comment exists, -104 if the leaf doesn't exist or the user doesn't exist.
        message (str): A message indicating if the comment exists on the leaf for the given user_id.
        code (bool): A boolean value indicating if the check was successful. If True, the comment exists. If False, it does not.
        """
        user_object = self.get_user_object(user_id)
        leaf_valid = self.check_leaf(leaf_id)
        response = {}
        if user_object is not None and leaf_valid:
            leaf_object = self.get_leaf_object(leaf_id)
            leaf_comment_object = LeafComments.objects.filter(
                leaf=leaf_object, commented_by=user_object.user_id
            ).first()
            response["status"] = -100
            response["message"] = leaf_comment_object is not None
            response["code"] = True
        else:
            response["status"] = -104
            response["code"] = False
            if not leaf_valid:
                response["message"] = "Leaf doesn't exist."
            else:
                response["message"] = "User doesn't exist"
        return response

    def check_like(self, leaf_id, user_id):
        """Check whether a user has liked a leaf or not.

        Args:
            leaf_id (int): The id of the leaf to check for likes.
            user_id (int): The id of the user to check if they have liked the leaf.

        Returns:
            dict: A dictionary containing the following keys:
                  - "status": An integer status code indicating the result of the operation.
                  - "message": A boolean value indicating whether the user has liked the leaf or not.
                  - "code": A boolean value indicating whether the operation was successful or not.

        Possible status codes:
            - -100: The operation was successful.
            - -104: The leaf doesn't exist.
            - -100: The user doesn't exist.
        """
        user_object = self.get_user_object(user_id)
        leaf_valid = self.check_leaf(leaf_id)
        response = {}
        if user_object is not None and leaf_valid:
            leaf_object = self.get_leaf_object(leaf_id)
            leaf_like_object = LeafLikes.objects.filter(
                leaf=leaf_object, liked_by=user_object.user_id
            ).first()
            response["status"] = -100
            response["message"] = leaf_like_object != None
            response["code"] = True
        else:
            response["status"] = -100
            response["code"] = False
            if not leaf_valid:
                response["message"] = "Leaf doesn't exist."
            else:
                response["message"] = "User doesn't exist"
        print(response)
        return response

    def check_dislike(self, leaf_id, user_id):
        """
        Check if a given user has disliked a leaf with the given id.

        Args:
        - leaf_id (int): id of the leaf to be checked.
        - user_id (int): id of the user whose dislike is to be checked.

        Returns:
        - response (dict): a dictionary with the following keys:
            - 'status' (int): status code of the operation (-100 for success, and -1XX for error).
            - 'message' (str): a message indicating whether the user has disliked the leaf or not.
            - 'code' (bool): a flag indicating whether the operation was successful or not.

        Raises:
        - None.
        """
        user_object = self.get_user_object(user_id)
        leaf_valid = self.check_leaf(leaf_id)
        response = {}
        if user_object is not None and leaf_valid:
            leaf_object = self.get_leaf_object(leaf_id)
            leaf_like_object = LeafDisLikes.objects.filter(
                leaf=leaf_object, disliked_by=user_object.user_id
            ).first()
            print(leaf_like_object)
            response["status"] = -100
            response["message"] = leaf_like_object != None
            response["code"] = True

        else:
            response["status"] = -100
            response["code"] = False
            if not leaf_valid:
                response["message"] = "Leaf doesn't exist."
            else:
                response["message"] = "User doesn't exist"
        return response

    def get_leaf_object(self, leaf_id):
        """
        Return the leaf object with the given leaf_id if it exists, otherwise return None.
        Args:
            leaf_id (int): The ID of the leaf object to retrieve.

        Returns:
            Leaf or None: The leaf object with the given leaf_id, or None if it does not exist.
        """
        if self.check_leaf(leaf_id):
            return Leaf.objects.filter(leaf_id=leaf_id).first()

    def get_comment_object(self, leaf_id, user_id):
        """
        Return the comment object with the given leaf_id and user_id if the leaf exists, otherwise return None.

        Args:
            leaf_id (int): The ID of the leaf object to retrieve the comment for.
            user_id (int): The ID of the user who made the comment.

        Returns:
            LeafComments or None: The comment object with the given leaf_id and user_id, or None if the leaf does not exist.
        """
        if self.check_leaf(leaf_id):
            return Leaf.objects.filter(leaf_id=leaf_id)

    def get_like_object(self, leaf_id, user_id):
        """Return the like object with the given leaf_id and user_id if the leaf exists and the user has liked it, otherwise return None.

        Args:
            leaf_id (int): The ID of the leaf object to retrieve the like for.
            user_id (int): The ID of the user who made the like.

        Returns:
            LeafLikes or None: The like object with the given leaf_id and user_id, or None if the leaf does not exist or the user has not liked it.
        """
        leaf_info = self.check_like(leaf_id, user_id)["message"]
        if leaf_info:
            user_object = self.get_user_object(user_id)
            leaf_object = self.get_leaf_object(leaf_id)
            return LeafLikes.objects.filter(leaf=leaf_object, liked_by=user_object)
        else:
            None

    def get_dislike_object(self, leaf_id, user_id):
        """Return the dislike object with the given leaf_id and user_id if the leaf exists and the user has disliked it, otherwise return None.

        Args:
            leaf_id (int): The ID of the leaf object to retrieve the dislike for.
            user_id (int): The ID of the user who made the dislike.

        Returns:
            LeafDisLikes or None: The dislike object with the given leaf_id and user_id, or None if the leaf does not exist or the user has not disliked it.
        """
        leaf_info = self.check_dislike(leaf_id, user_id)["message"]
        if leaf_info:
            user_object = self.get_user_object(user_id)
            leaf_object = self.get_leaf_object(leaf_id)
            return LeafDisLikes.objects.filter(leaf=leaf_object, disliked_by=user_object)
        else:
            None

    def is_authorised(self, request) -> bool:
        """Check if the given request is authorized.

        Args:
            request (HttpRequest): The HTTP request to check.

        Returns:
            bool: True if the request is authorized, False otherwise.
        """
        return session_management_object.current_session(
            request
        ) != None and session_management_object.check_session(
            request.session["auth_token"]
        )

    def get_logged_in_user(self, request):
        """Return the logged in user for the given request.

        Args:
            request (HttpRequest): The HTTP request to get the logged in user for.

        Returns:
            User or None: The logged in user for the given request, or None if no user is logged in.
        """
        return session_management_object.get_session_user(request)

    def get_user_object(self, user_id):
        """Return the user object with the given user_id if it exists, otherwise return None.

        Args:
            user_id (int): The ID of the user object to retrieve.

        Returns:
            UserProfile or None: The user object with the given user_id, or None if it does not exist.
        """
        return UserProfile.objects.filter(user_id=user_id).first()

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

    def get_leaf_comment_object_with_id(self,leaf_comment_id):
        """Retrieves the LeafComments object with the specified leaf_comment_id from the database.

        Args:
            leaf_comment_id (int): The ID of the LeafComments object to retrieve.

        Returns:
            LeafComments or None: The LeafComments object corresponding to the leaf_comment_id if found, or None if not found.
        """
        return LeafComments.objects.filter(comment_id= leaf_comment_id).first()

    def run_user_middleware(self, user_object, operation, value):
        """
        Run middleware operation on user object.
        Args:
            user_object (UserProfile): The user object on which to run the middleware operation.
            operation (str): The middleware operation to run. Must be one of 'update_public_leaf', 
                            'update_private_leaf', 'update_followers', 'update_following', 
                            'update_user_exp', or 'update_user_level'.
            value (int): The value to use for the middleware operation.

        Returns:
            The result of the middleware operation.

        Raises:
            None
        """
        user_middleware_object = EdenUserMiddleWare(user_object)
        allowed_operations = ['update_public_leaf', "update_private_leaf",
                              "update_followers", "update_following", "update_user_exp", "update_user_level"]
        if operation not in allowed_operations:
            return -111
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
            return 100
      

    def run_leaf_middleware(self, leaf_object, operation, value):
        """
        Call the appropriate method of EdenLeafMiddleware class based on the given operation.
        Args:
            leaf_object (Leaf): The leaf object to perform the operation on.
            operation (str): The name of the operation to perform. Must be one of "update_likes",
                "update_dislikes", "update_comments", or "update_views".
            value (int): The value to pass to the operation method.

        Returns:
            The return value of the appropriate operation method, or False if the operation is not allowed.

        """
        leaf_middleware_object = EdenLeafMiddleware(leaf_object)
        allowed_operations = ["update_likes", "update_dislikes", "update_comments", "update_views"]
        if operation not in allowed_operations:
            return -111
        else:
            match operation:
                case "update_likes":
                    return leaf_middleware_object.update_likes(value)
                case "update_dislikes":
                    return leaf_middleware_object.update_dislikes(value)
                case "update_comments":
                    return leaf_middleware_object.update_comments(value)
                case "update_views":
                    return leaf_middleware_object.update_views(value)
            return 100
                

    def run_exp_engine_per_leaf(self,leaf_object):
        from exp_engine.exp_manager import EdenExperienceEngine
        exp_engine_object = EdenExperienceEngine()
        return exp_engine_object.initiate_per_leaf(leaf_object)
    
    def run_conX_engine(self,leaf_id, interaction, interacted_by):
        conX_engine = Eden_CONX_Engine()
        allowed_interactions = ['like', 'dislike', 'comment', 'view', 'sub_comment']
        if interaction not in allowed_interactions:
            return -111
        else:
            match interaction:
                case "like":
                    leaf_interaction = InteractionType.Like 
                case "dislike":
                    leaf_interaction = InteractionType.Dislike
                case "comments":
                    leaf_interaction = InteractionType.Comment
                case "view":
                    leaf_interaction = InteractionType.View
                case "sub_comment":
                    leaf_interaction = InteractionType.SubComment
            data= {
                'leaf_id': leaf_id,
                'leaf_interaction': leaf_interaction,
                'interacted_by': interacted_by
            }
            conX_engine.start_pipeline(data)
            return 100

    def handle_comment_sentiment_middleware(self,comment_id, topic_id, user_object, value):
        try:
            comment_object = self.get_leaf_comment_object_with_id(comment_id)
            sentiment = comment_object.comment_sentiment
            user_topic_relation_object = self.get_user_topic_relation_object(topic_id,user_object)
            middleware_object = EdenUserTopicRelationMiddleWare(user_topic_relation_object)
            if sentiment > 0:
                middleware_object.update_positive_comments_made(value)
                
            else:
                middleware_object.update_negative_comments_made(value)
            middleware_object.update_times_interacted(value)
            return 100
        except:
            return -111

    def run_user_topic_middleware(self,leaf_id,interaction, user_object, value, comment_id=None):
        conX_engine = Eden_CONX_Engine()
        leaf_object = self.get_leaf_object(leaf_id)
        topic_id = leaf_object.leaf_topic_id
        topic_category_id = leaf_object.leaf_topic_category_id
        if comment_id is not None:
            self.handle_comment_sentiment_middleware(comment_id,topic_id,user_object,value)
        
        if conX_engine.check_user_topic_relation(topic_id,user_object):
            return conX_engine.update_user_topic_relation_middleware(leaf_id, topic_id, interaction,user_object,value)
        else:
            data = {
                'topic_id':topic_id,
                'topic_category_id': topic_category_id,
                'user_id': user_object.user_id
            }
            status = conX_engine.create_user_topic_relation(data)
            if status == 100:
                return conX_engine.update_user_topic_relation_middleware(leaf_id, topic_id, interaction,user_object,value)
        return -111
